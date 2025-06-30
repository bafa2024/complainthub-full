import React, { useState, useContext, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import apiClient from '../../services/apiClient';
import { AuthContext } from '../../contexts/AuthContext';
import './UserSettings.css';

export default function UserSettings() {
  const { user, updateUser } = useContext(AuthContext);
  const navigate = useNavigate();
  
  // Active section state
  const [activeSection, setActiveSection] = useState('profile');
  
  // Alert state
  const [alert, setAlert] = useState({ show: false, type: '', message: '' });
  
  // Profile form state
  const [profileData, setProfileData] = useState({
    displayName: user?.full_name || '',
    phone: user?.phone || '',
    email: user?.email || '',
    language: 'en',
    timezone: 'Asia/Kolkata'
  });
  
  // Security form state
  const [securityData, setSecurityData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordStrength, setPasswordStrength] = useState('weak');
  
  // Notification preferences state
  const [notifications, setNotifications] = useState({
    emailResponse: true,
    emailStatus: true,
    emailWeekly: false,
    emailNews: false,
    smsUrgent: true,
    smsAll: false,
    whatsappEnable: true
  });
  
  // Privacy settings state
  const [privacy, setPrivacy] = useState({
    profileVisibility: 'anonymous',
    shareAnalytics: false,
    shareLocation: false
  });
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);

  // Password strength checker
  useEffect(() => {
    const password = securityData.newPassword;
    if (password.length < 6) {
      setPasswordStrength('weak');
    } else if (password.length < 10) {
      setPasswordStrength('medium');
    } else {
      setPasswordStrength('strong');
    }
  }, [securityData.newPassword]);

  // Show alert function
  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: '', message: '' }), 3000);
  };

  // Profile form submission
  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/users/me', profileData);
      updateUser({ ...user, ...profileData });
      showAlert('success', 'Profile updated successfully!');
    } catch (error) {
      showAlert('error', 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  // Security form submission
  const handleSecuritySubmit = async (e) => {
    e.preventDefault();
    if (securityData.newPassword !== securityData.confirmPassword) {
      showAlert('error', 'Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await apiClient.put('/users/me/password', {
        current_password: securityData.currentPassword,
        new_password: securityData.newPassword
      });
      setSecurityData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      showAlert('success', 'Password changed successfully!');
    } catch (error) {
      showAlert('error', 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  // Notification preferences submission
  const handleNotificationSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/users/me/notifications', notifications);
      showAlert('success', 'Notification preferences saved!');
    } catch (error) {
      showAlert('error', 'Failed to save notification preferences');
    } finally {
      setLoading(false);
    }
  };

  // Privacy settings submission
  const handlePrivacySubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/users/me/privacy', privacy);
      showAlert('success', 'Privacy settings updated!');
    } catch (error) {
      showAlert('error', 'Failed to update privacy settings');
    } finally {
      setLoading(false);
    }
  };

  // Download data
  const handleDownloadData = async () => {
    try {
      const response = await apiClient.get('/users/me/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'user-data.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
      showAlert('success', 'Data downloaded successfully!');
    } catch (error) {
      showAlert('error', 'Failed to download data');
    }
  };

  // Delete account
  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      if (window.confirm('This will permanently delete all your complaints and data. Are you absolutely sure?')) {
        try {
          await apiClient.delete('/users/me');
          showAlert('success', 'Account deletion will be processed. You will receive a confirmation email.');
          navigate('/');
        } catch (error) {
          showAlert('error', 'Failed to delete account');
        }
      }
    }
  };

  // Sign out all sessions
  const handleSignOutAll = async () => {
    try {
      await apiClient.post('/auth/logout-all');
      showAlert('success', 'All sessions signed out successfully!');
    } catch (error) {
      showAlert('error', 'Failed to sign out all sessions');
    }
  };

  return (
    <div>
      {/* REMOVE the header section below to avoid duplicated navbar */}
      {/* <header className="settings-header">
        <div className="header-container">
          <div className="logo">ComplaintHub</div>
          <div className="header-nav">
            <Link to="/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
            <Link to="/" className="btn btn-primary">Logout</Link>
          </div>
        </div>
      </header> */}

      <div className="settings-container">
        {/* Alert Messages */}
        {alert.show && (
          <div className={`alert alert-${alert.type === 'error' ? 'danger' : alert.type} show`}>
            {alert.message}
          </div>
        )}

        <div className="settings-layout">
          {/* Sidebar Navigation */}
          <aside className="settings-sidebar">
            <nav>
              <ul className="sidebar-nav">
                <li>
                  <button 
                    className={`sidebar-link ${activeSection === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveSection('profile')}
                  >
                    Profile
                  </button>
                </li>
                <li>
                  <button 
                    className={`sidebar-link ${activeSection === 'security' ? 'active' : ''}`}
                    onClick={() => setActiveSection('security')}
                  >
                    Security
                  </button>
                </li>
                <li>
                  <button 
                    className={`sidebar-link ${activeSection === 'notifications' ? 'active' : ''}`}
                    onClick={() => setActiveSection('notifications')}
                  >
                    Notifications
                  </button>
                </li>
                <li>
                  <button 
                    className={`sidebar-link ${activeSection === 'privacy' ? 'active' : ''}`}
                    onClick={() => setActiveSection('privacy')}
                  >
                    Privacy
                  </button>
                </li>
                <li>
                  <button 
                    className={`sidebar-link ${activeSection === 'account' ? 'active' : ''}`}
                    onClick={() => setActiveSection('account')}
                  >
                    Account
                  </button>
                </li>
              </ul>
            </nav>
          </aside>

          {/* Settings Content */}
          <div className="settings-content">
            {/* Profile Section */}
            {activeSection === 'profile' && (
              <section className="settings-section">
                <h2 className="section-title">Profile Information</h2>
                
                <form onSubmit={handleProfileSubmit}>
                  <div className="form-group">
                    <label className="form-label">Display Name</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={profileData.displayName}
                      onChange={(e) => setProfileData({...profileData, displayName: e.target.value})}
                      required
                    />
                    <p className="form-help">This name will be visible on your complaints (can be an alias)</p>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Phone Number (Primary Contact)</label>
                    <div className="form-control-with-btn">
                      <input 
                        type="tel" 
                        className="form-control" 
                        value={profileData.phone}
                        onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                        required
                      />
                      <button type="button" className="btn btn-secondary">Verify</button>
                    </div>
                    <p className="form-help">Used to identify your complaints</p>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <div className="form-control-with-btn">
                      <input 
                        type="email" 
                        className="form-control" 
                        value={profileData.email}
                        onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                        required
                      />
                      <button type="button" className="btn btn-secondary">Verify</button>
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Preferred Language</label>
                    <select 
                      className="form-control" 
                      value={profileData.language}
                      onChange={(e) => setProfileData({...profileData, language: e.target.value})}
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                      <option value="ta">Tamil</option>
                      <option value="te">Telugu</option>
                      <option value="bn">Bengali</option>
                      <option value="mr">Marathi</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Time Zone</label>
                    <select 
                      className="form-control" 
                      value={profileData.timezone}
                      onChange={(e) => setProfileData({...profileData, timezone: e.target.value})}
                    >
                      <option value="Asia/Kolkata">GMT+5:30 Mumbai, Kolkata, New Delhi</option>
                      <option value="Asia/Singapore">GMT+8:00 Singapore</option>
                      <option value="America/New_York">GMT-5:00 Eastern Time</option>
                      <option value="Europe/London">GMT+0:00 London</option>
                    </select>
                  </div>
                  
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : 'Save Changes'}
                  </button>
                </form>
              </section>
            )}

            {/* Security Section */}
            {activeSection === 'security' && (
              <section className="settings-section">
                <h2 className="section-title">Security Settings</h2>
                
                <form onSubmit={handleSecuritySubmit}>
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Change Password</h3>
                  
                  <div className="form-group">
                    <label className="form-label">Current Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={securityData.currentPassword}
                      onChange={(e) => setSecurityData({...securityData, currentPassword: e.target.value})}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">New Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={securityData.newPassword}
                      onChange={(e) => setSecurityData({...securityData, newPassword: e.target.value})}
                      required
                    />
                    <div className="password-strength">
                      <div className="strength-bar">
                        <div className={`strength-fill ${passwordStrength}`}></div>
                      </div>
                      <p className="form-help">Use at least 8 characters with a mix of letters, numbers & symbols</p>
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Confirm New Password</label>
                    <input 
                      type="password" 
                      className="form-control" 
                      value={securityData.confirmPassword}
                      onChange={(e) => setSecurityData({...securityData, confirmPassword: e.target.value})}
                      required
                    />
                  </div>
                  
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Password'}
                  </button>
                  
                  <hr style={{margin: '40px 0'}} />
                  
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Two-Factor Authentication</h3>
                  
                  <div className="two-factor-setup">
                    <h4 style={{marginBottom: '10px'}}>Enhanced Security</h4>
                    <p style={{marginBottom: '15px'}}>Add an extra layer of security to your account</p>
                    <button type="button" className="btn btn-primary">Enable 2FA</button>
                  </div>
                  
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Login Sessions</h3>
                  
                  <div className="session-item">
                    <div className="session-info">
                      <div>
                        <strong>Current Session</strong><br />
                        <span className="session-details">Chrome on Windows • Mumbai, India</span>
                      </div>
                      <span className="session-status active">Active now</span>
                    </div>
                  </div>
                  
                  <button type="button" className="btn btn-secondary" onClick={handleSignOutAll}>
                    Sign Out All Other Sessions
                  </button>
                </form>
              </section>
            )}

            {/* Notifications Section */}
            {activeSection === 'notifications' && (
              <section className="settings-section">
                <h2 className="section-title">Notification Preferences</h2>
                
                <form onSubmit={handleNotificationSubmit}>
                  <div className="form-check-group">
                    <h4>Email Notifications</h4>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="emailResponse" 
                        checked={notifications.emailResponse}
                        onChange={(e) => setNotifications({...notifications, emailResponse: e.target.checked})}
                      />
                      <label htmlFor="emailResponse">
                        <strong>New response from brand</strong><br />
                        <span className="form-help">Get notified when brands respond to your complaints</span>
                      </label>
                    </div>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="emailStatus" 
                        checked={notifications.emailStatus}
                        onChange={(e) => setNotifications({...notifications, emailStatus: e.target.checked})}
                      />
                      <label htmlFor="emailStatus">
                        <strong>Ticket status changes</strong><br />
                        <span className="form-help">Updates when your ticket status changes</span>
                      </label>
                    </div>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="emailWeekly" 
                        checked={notifications.emailWeekly}
                        onChange={(e) => setNotifications({...notifications, emailWeekly: e.target.checked})}
                      />
                      <label htmlFor="emailWeekly">
                        <strong>Weekly summary</strong><br />
                        <span className="form-help">Summary of all your tickets and their status</span>
                      </label>
                    </div>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="emailNews" 
                        checked={notifications.emailNews}
                        onChange={(e) => setNotifications({...notifications, emailNews: e.target.checked})}
                      />
                      <label htmlFor="emailNews">
                        <strong>Platform updates</strong><br />
                        <span className="form-help">New features and important announcements</span>
                      </label>
                    </div>
                  </div>
                  
                  <div className="form-check-group">
                    <h4>SMS Notifications</h4>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="smsUrgent" 
                        checked={notifications.smsUrgent}
                        onChange={(e) => setNotifications({...notifications, smsUrgent: e.target.checked})}
                      />
                      <label htmlFor="smsUrgent">
                        <strong>Urgent updates only</strong><br />
                        <span className="form-help">Critical updates that need immediate attention</span>
                      </label>
                    </div>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="smsAll" 
                        checked={notifications.smsAll}
                        onChange={(e) => setNotifications({...notifications, smsAll: e.target.checked})}
                      />
                      <label htmlFor="smsAll">
                        <strong>All ticket updates</strong><br />
                        <span className="form-help">SMS for every ticket status change</span>
                      </label>
                    </div>
                  </div>
                  
                  <div className="form-check-group">
                    <h4>WhatsApp Notifications</h4>
                    
                    <div className="form-check">
                      <input 
                        type="checkbox" 
                        id="whatsappEnable" 
                        checked={notifications.whatsappEnable}
                        onChange={(e) => setNotifications({...notifications, whatsappEnable: e.target.checked})}
                      />
                      <label htmlFor="whatsappEnable">
                        <strong>Enable WhatsApp notifications</strong><br />
                        <span className="form-help">Receive updates via WhatsApp</span>
                      </label>
                    </div>
                    
                    <p className="whatsapp-number">
                      Number: {profileData.phone} <a href="#" style={{color: '#3498db'}}>Change</a>
                    </p>
                  </div>
                  
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Saving...' : 'Save Preferences'}
                  </button>
                </form>
              </section>
            )}

            {/* Privacy Section */}
            {activeSection === 'privacy' && (
              <section className="settings-section">
                <h2 className="section-title">Privacy Settings</h2>
                
                <form onSubmit={handlePrivacySubmit}>
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Public Profile Visibility</h3>
                  
                  <div 
                    className={`privacy-option ${privacy.profileVisibility === 'anonymous' ? 'selected' : ''}`}
                    onClick={() => setPrivacy({...privacy, profileVisibility: 'anonymous'})}
                  >
                    <h5>Anonymous</h5>
                    <p>Your complaints will be shown as "User****XXX"</p>
                  </div>
                  
                  <div 
                    className={`privacy-option ${privacy.profileVisibility === 'partial' ? 'selected' : ''}`}
                    onClick={() => setPrivacy({...privacy, profileVisibility: 'partial'})}
                  >
                    <h5>Partial Name</h5>
                    <p>Show only your first name on public complaints</p>
                  </div>
                  
                  <div 
                    className={`privacy-option ${privacy.profileVisibility === 'full' ? 'selected' : ''}`}
                    onClick={() => setPrivacy({...privacy, profileVisibility: 'full'})}
                  >
                    <h5>Full Name</h5>
                    <p>Display your full name on public complaints</p>
                  </div>
                  
                  <hr style={{margin: '30px 0'}} />
                  
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Data Sharing</h3>
                  
                  <div className="form-check">
                    <input 
                      type="checkbox" 
                      id="shareAnalytics" 
                      checked={privacy.shareAnalytics}
                      onChange={(e) => setPrivacy({...privacy, shareAnalytics: e.target.checked})}
                    />
                    <label htmlFor="shareAnalytics">
                      <strong>Share anonymous usage data</strong><br />
                      <span className="form-help">Help us improve the platform with anonymous analytics</span>
                    </label>
                  </div>
                  
                  <div className="form-check">
                    <input 
                      type="checkbox" 
                      id="shareLocation" 
                      checked={privacy.shareLocation}
                      onChange={(e) => setPrivacy({...privacy, shareLocation: e.target.checked})}
                    />
                    <label htmlFor="shareLocation">
                      <strong>Share location on complaints</strong><br />
                      <span className="form-help">Show your city/region on public complaints</span>
                    </label>
                  </div>
                  
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Privacy Settings'}
                  </button>
                </form>
              </section>
            )}

            {/* Account Section */}
            {activeSection === 'account' && (
              <section className="settings-section">
                <h2 className="section-title">Account Management</h2>
                
                <div style={{marginBottom: '30px'}}>
                  <h3 style={{marginBottom: '20px', fontSize: '18px'}}>Account Data</h3>
                  
                  <button className="btn btn-secondary" style={{marginRight: '10px'}} onClick={handleDownloadData}>
                    Download My Data
                  </button>
                  <button className="btn btn-secondary">Export Complaints History</button>
                  
                  <p className="form-help">
                    Download all your personal data and complaint history in a machine-readable format
                  </p>
                </div>
                
                <div className="danger-zone">
                  <h4>Danger Zone</h4>
                  <p style={{marginBottom: '15px'}}>Once you delete your account, there is no going back. Please be certain.</p>
                  <button className="btn btn-danger" onClick={handleDeleteAccount}>Delete Account</button>
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
