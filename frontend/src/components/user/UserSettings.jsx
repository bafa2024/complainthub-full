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
    timezone: 'Asia/Kolkata',
    address: user?.address || '',
    dateOfBirth: user?.date_of_birth || '',
    gender: user?.gender || '',
    preferences: {
      emailNotifications: true,
      smsNotifications: false,
      whatsappNotifications: true,
      publicProfile: false,
      shareAnalytics: false
    }
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
    whatsappEnable: true,
    pushNotifications: true,
    marketingEmails: false
  });
  
  // Privacy settings state
  const [privacy, setPrivacy] = useState({
    profileVisibility: 'anonymous',
    shareAnalytics: false,
    shareLocation: false,
    allowContact: true,
    dataRetention: '1year'
  });
  
  // Loading states
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [complaintHistory, setComplaintHistory] = useState([]);
  const [exportLoading, setExportLoading] = useState(false);

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
    setExportLoading(true);
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
    } finally {
      setExportLoading(false);
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
    <div className="user-settings">
      <div className="settings-container">
        {/* Alert Messages */}
        {alert.show && (
          <div className={`alert alert-${alert.type === 'error' ? 'danger' : alert.type} show`}>
            {alert.message}
          </div>
        )}

        {/* Settings Navigation */}
        <div className="settings-nav">
          <div className="nav-section">
            <h3>Account</h3>
            <button 
              className={`nav-item ${activeSection === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveSection('profile')}
            >
              <i className="fas fa-user"></i>
              Profile Information
            </button>
            <button 
              className={`nav-item ${activeSection === 'security' ? 'active' : ''}`}
              onClick={() => setActiveSection('security')}
            >
              <i className="fas fa-shield-alt"></i>
              Security & Password
            </button>
            <button 
              className={`nav-item ${activeSection === 'notifications' ? 'active' : ''}`}
              onClick={() => setActiveSection('notifications')}
            >
              <i className="fas fa-bell"></i>
              Notifications
            </button>
            <button 
              className={`nav-item ${activeSection === 'privacy' ? 'active' : ''}`}
              onClick={() => setActiveSection('privacy')}
            >
              <i className="fas fa-lock"></i>
              Privacy & Data
            </button>
          </div>

          <div className="nav-section">
            <h3>Data & History</h3>
            <button 
              className={`nav-item ${activeSection === 'history' ? 'active' : ''}`}
              onClick={() => setActiveSection('history')}
            >
              <i className="fas fa-history"></i>
              Complaint History
            </button>
            <button 
              className={`nav-item ${activeSection === 'sessions' ? 'active' : ''}`}
              onClick={() => setActiveSection('sessions')}
            >
              <i className="fas fa-desktop"></i>
              Active Sessions
            </button>
            <button 
              className={`nav-item ${activeSection === 'export' ? 'active' : ''}`}
              onClick={() => setActiveSection('export')}
            >
              <i className="fas fa-download"></i>
              Export Data
            </button>
          </div>

          <div className="nav-section">
            <h3>Account Actions</h3>
            <button 
              className={`nav-item ${activeSection === 'delete' ? 'active' : ''}`}
              onClick={() => setActiveSection('delete')}
            >
              <i className="fas fa-trash"></i>
              Delete Account
            </button>
          </div>
        </div>

        {/* Settings Content */}
        <div className="settings-content">
          {/* Profile Section */}
          {activeSection === 'profile' && (
            <div className="settings-section">
              <h2>Profile Information</h2>
              <form onSubmit={handleProfileSubmit}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>Full Name</label>
                    <input
                      type="text"
                      value={profileData.displayName}
                      onChange={(e) => setProfileData({...profileData, displayName: e.target.value})}
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Date of Birth</label>
                    <input
                      type="date"
                      value={profileData.dateOfBirth}
                      onChange={(e) => setProfileData({...profileData, dateOfBirth: e.target.value})}
                      className="form-control"
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      value={profileData.gender}
                      onChange={(e) => setProfileData({...profileData, gender: e.target.value})}
                      className="form-control"
                    >
                      <option value="">Prefer not to say</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Language</label>
                    <select
                      value={profileData.language}
                      onChange={(e) => setProfileData({...profileData, language: e.target.value})}
                      className="form-control"
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                    </select>
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Address</label>
                  <textarea
                    value={profileData.address}
                    onChange={(e) => setProfileData({...profileData, address: e.target.value})}
                    className="form-control"
                    rows="3"
                  />
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </form>
            </div>
          )}

          {/* Security Section */}
          {activeSection === 'security' && (
            <div className="settings-section">
              <h2>Security & Password</h2>
              <form onSubmit={handleSecuritySubmit}>
                <div className="form-group">
                  <label>Current Password</label>
                  <input
                    type="password"
                    value={securityData.currentPassword}
                    onChange={(e) => setSecurityData({...securityData, currentPassword: e.target.value})}
                    className="form-control"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>New Password</label>
                  <input
                    type="password"
                    value={securityData.newPassword}
                    onChange={(e) => setSecurityData({...securityData, newPassword: e.target.value})}
                    className="form-control"
                    required
                  />
                  <div className={`password-strength ${passwordStrength}`}>
                    Password strength: {passwordStrength}
                  </div>
                </div>
                
                <div className="form-group">
                  <label>Confirm New Password</label>
                  <input
                    type="password"
                    value={securityData.confirmPassword}
                    onChange={(e) => setSecurityData({...securityData, confirmPassword: e.target.value})}
                    className="form-control"
                    required
                  />
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Updating...' : 'Update Password'}
                </button>
              </form>
            </div>
          )}

          {/* Notifications Section */}
          {activeSection === 'notifications' && (
            <div className="settings-section">
              <h2>Notification Preferences</h2>
              <form onSubmit={handleNotificationSubmit}>
                <div className="notification-options">
                  <h3>Email Notifications</h3>
                  <div className="checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.emailResponse}
                        onChange={(e) => setNotifications({...notifications, emailResponse: e.target.checked})}
                      />
                      Brand responses to complaints
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.emailStatus}
                        onChange={(e) => setNotifications({...notifications, emailStatus: e.target.checked})}
                      />
                      Status updates on complaints
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.emailWeekly}
                        onChange={(e) => setNotifications({...notifications, emailWeekly: e.target.checked})}
                      />
                      Weekly summary emails
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.marketingEmails}
                        onChange={(e) => setNotifications({...notifications, marketingEmails: e.target.checked})}
                      />
                      Marketing and promotional emails
                    </label>
                  </div>
                  
                  <h3>SMS Notifications</h3>
                  <div className="checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.smsUrgent}
                        onChange={(e) => setNotifications({...notifications, smsUrgent: e.target.checked})}
                      />
                      Urgent updates only
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.smsAll}
                        onChange={(e) => setNotifications({...notifications, smsAll: e.target.checked})}
                      />
                      All updates via SMS
                    </label>
                  </div>
                  
                  <h3>Other Notifications</h3>
                  <div className="checkbox-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.whatsappEnable}
                        onChange={(e) => setNotifications({...notifications, whatsappEnable: e.target.checked})}
                      />
                      WhatsApp notifications
                    </label>
                    <label>
                      <input
                        type="checkbox"
                        checked={notifications.pushNotifications}
                        onChange={(e) => setNotifications({...notifications, pushNotifications: e.target.checked})}
                      />
                      Push notifications
                    </label>
                  </div>
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Preferences'}
                </button>
              </form>
            </div>
          )}

          {/* Privacy Section */}
          {activeSection === 'privacy' && (
            <div className="settings-section">
              <h2>Privacy & Data Settings</h2>
              <form onSubmit={handlePrivacySubmit}>
                <div className="form-group">
                  <label>Profile Visibility</label>
                  <select
                    value={privacy.profileVisibility}
                    onChange={(e) => setPrivacy({...privacy, profileVisibility: e.target.value})}
                    className="form-control"
                  >
                    <option value="anonymous">Anonymous (recommended)</option>
                    <option value="firstname">First Name Only</option>
                    <option value="fullname">Full Name</option>
                  </select>
                </div>
                
                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={privacy.shareAnalytics}
                      onChange={(e) => setPrivacy({...privacy, shareAnalytics: e.target.checked})}
                    />
                    Share analytics data to improve service
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={privacy.shareLocation}
                      onChange={(e) => setPrivacy({...privacy, shareLocation: e.target.checked})}
                    />
                    Allow location sharing for better support
                  </label>
                  <label>
                    <input
                      type="checkbox"
                      checked={privacy.allowContact}
                      onChange={(e) => setPrivacy({...privacy, allowContact: e.target.checked})}
                    />
                    Allow brands to contact me directly
                  </label>
                </div>
                
                <div className="form-group">
                  <label>Data Retention</label>
                  <select
                    value={privacy.dataRetention}
                    onChange={(e) => setPrivacy({...privacy, dataRetention: e.target.value})}
                    className="form-control"
                  >
                    <option value="6months">6 months</option>
                    <option value="1year">1 year</option>
                    <option value="2years">2 years</option>
                    <option value="indefinite">Indefinite</option>
                  </select>
                </div>
                
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Privacy Settings'}
                </button>
              </form>
            </div>
          )}

          {/* History Section */}
          {activeSection === 'history' && (
            <div className="settings-section">
              <h2>Complaint History</h2>
              <div className="history-stats">
                <div className="stat-card">
                  <h3>Total Complaints</h3>
                  <span className="stat-number">24</span>
                </div>
                <div className="stat-card">
                  <h3>Resolved</h3>
                  <span className="stat-number">18</span>
                </div>
                <div className="stat-card">
                  <h3>Pending</h3>
                  <span className="stat-number">6</span>
                </div>
              </div>
              
              <div className="history-list">
                <h3>Recent Complaints</h3>
                <div className="complaint-items">
                  {[1, 2, 3, 4, 5].map(i => (
                    <div key={i} className="complaint-item">
                      <div className="complaint-info">
                        <h4>Complaint #{i}</h4>
                        <p>Brand: TechCorp</p>
                        <p>Status: {i % 2 === 0 ? 'Resolved' : 'In Progress'}</p>
                      </div>
                      <div className="complaint-actions">
                        <Link to={`/tickets/${i}`} className="btn btn-sm btn-outline">
                          View
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Sessions Section */}
          {activeSection === 'sessions' && (
            <div className="settings-section">
              <h2>Active Sessions</h2>
              <div className="sessions-list">
                <div className="session-item current">
                  <div className="session-info">
                    <h4>Current Session</h4>
                    <p>Chrome on Windows • 192.168.1.100</p>
                    <p>Last active: Just now</p>
                  </div>
                  <span className="session-status">Active</span>
                </div>
                
                <div className="session-item">
                  <div className="session-info">
                    <h4>Mobile Session</h4>
                    <p>Safari on iPhone • 192.168.1.101</p>
                    <p>Last active: 2 hours ago</p>
                  </div>
                  <button className="btn btn-sm btn-danger">Terminate</button>
                </div>
              </div>
              
              <button onClick={handleSignOutAll} className="btn btn-warning">
                Sign Out All Sessions
              </button>
            </div>
          )}

          {/* Export Section */}
          {activeSection === 'export' && (
            <div className="settings-section">
              <h2>Export Your Data</h2>
              <p>Download all your personal data including complaints, settings, and activity history.</p>
              
              <div className="export-options">
                <div className="export-option">
                  <h4>Complete Data Export</h4>
                  <p>Includes all your complaints, profile data, and settings</p>
                  <button onClick={handleDownloadData} className="btn btn-primary" disabled={exportLoading}>
                    {exportLoading ? 'Preparing...' : 'Download JSON'}
                  </button>
                </div>
                
                <div className="export-option">
                  <h4>Complaints Only</h4>
                  <p>Export just your complaint history</p>
                  <button className="btn btn-outline">Download CSV</button>
                </div>
              </div>
            </div>
          )}

          {/* Delete Account Section */}
          {activeSection === 'delete' && (
            <div className="settings-section">
              <h2>Delete Account</h2>
              <div className="delete-warning">
                <i className="fas fa-exclamation-triangle"></i>
                <h3>This action cannot be undone</h3>
                <p>Deleting your account will permanently remove all your data including:</p>
                <ul>
                  <li>All your complaints and their history</li>
                  <li>Personal information and settings</li>
                  <li>Notification preferences</li>
                  <li>Account activity logs</li>
                </ul>
                <p>You will receive a confirmation email before the deletion is processed.</p>
              </div>
              
              <button onClick={handleDeleteAccount} className="btn btn-danger">
                Delete My Account
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
