import React, { useState, useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';
import apiClient from '../../services/apiClient';
import './BrandSettings.css';

export default function BrandSettings() {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ show: false, type: '', message: '' });

  // Brand profile state
  const [brandProfile, setBrandProfile] = useState({
    name: user?.brand_name || 'Acme Corporation',
    description: 'Leading provider of innovative solutions',
    website: 'https://acme.com',
    industry: 'Technology',
    address: '123 Business Street, Tech City, TC 12345',
    contactEmail: 'support@acme.com',
    contactPhone: '+1 (555) 123-4567'
  });

  // Integration settings
  const [integrations, setIntegrations] = useState({
    webhook: {
      enabled: true,
      url: 'https://acme.com/webhook/complaints',
      secret: 'webhook_secret_123'
    },
    api: {
      enabled: false,
      key: 'api_key_456',
      rateLimit: 1000
    },
    email: {
      enabled: true,
      address: 'complaints@acme.com'
    }
  });

  // Team management
  const [teamMembers, setTeamMembers] = useState([
    {
      id: 1,
      name: 'John Smith',
      email: 'john@acme.com',
      role: 'admin',
      status: 'active',
      lastActive: '2024-01-15'
    },
    {
      id: 2,
      name: 'Sarah Johnson',
      email: 'sarah@acme.com',
      role: 'agent',
      status: 'active',
      lastActive: '2024-01-14'
    }
  ]);

  // Notification preferences
  const [notifications, setNotifications] = useState({
    newComplaints: true,
    urgentComplaints: true,
    dailyDigest: false,
    weeklyReport: true,
    emailNotifications: true,
    smsNotifications: false
  });

  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: '', message: '' }), 3000);
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/brand/profile', brandProfile);
      showAlert('success', 'Brand profile updated successfully!');
    } catch (error) {
      showAlert('error', 'Failed to update brand profile');
    } finally {
      setLoading(false);
    }
  };

  const handleIntegrationSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/brand/integrations', integrations);
      showAlert('success', 'Integration settings updated!');
    } catch (error) {
      showAlert('error', 'Failed to update integration settings');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.put('/brand/notifications', notifications);
      showAlert('success', 'Notification preferences saved!');
    } catch (error) {
      showAlert('error', 'Failed to save notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const addTeamMember = () => {
    const newMember = {
      id: Date.now(),
      name: '',
      email: '',
      role: 'agent',
      status: 'pending',
      lastActive: new Date().toISOString().split('T')[0]
    };
    setTeamMembers([...teamMembers, newMember]);
  };

  const removeTeamMember = (id) => {
    if (window.confirm('Are you sure you want to remove this team member?')) {
      setTeamMembers(teamMembers.filter(member => member.id !== id));
      showAlert('success', 'Team member removed successfully');
    }
  };

  return (
    <div className="brand-settings">
      {/* Header */}
      <header className="settings-header">
        <div className="header-content">
          <div className="brand-info">
            <div className="brand-logo">AC</div>
            <div>
              <h2>{brandProfile.name}</h2>
              <p>Brand Settings</p>
            </div>
          </div>
          <div className="user-menu">
            <Link to="/brand/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
            <Link to="/" className="btn btn-primary">Logout</Link>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <ul>
          <li><button 
            className={`nav-tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Brand Profile
          </button></li>
          <li><button 
            className={`nav-tab ${activeTab === 'integrations' ? 'active' : ''}`}
            onClick={() => setActiveTab('integrations')}
          >
            Integrations
          </button></li>
          <li><button 
            className={`nav-tab ${activeTab === 'team' ? 'active' : ''}`}
            onClick={() => setActiveTab('team')}
          >
            Team Management
          </button></li>
          <li><button 
            className={`nav-tab ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            Notifications
          </button></li>
        </ul>
      </nav>

      {/* Alert Messages */}
      {alert.show && (
        <div className={`alert alert-${alert.type === 'error' ? 'danger' : alert.type} show`}>
          {alert.message}
        </div>
      )}

      <div className="container">
        {/* Brand Profile Tab */}
        {activeTab === 'profile' && (
          <div className="settings-section">
            <h2 className="section-title">Brand Profile</h2>
            
            <form onSubmit={handleProfileSubmit}>
              <div className="form-group">
                <label className="form-label">Brand Name</label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={brandProfile.name}
                  onChange={(e) => setBrandProfile({...brandProfile, name: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea 
                  className="form-control" 
                  rows="3"
                  value={brandProfile.description}
                  onChange={(e) => setBrandProfile({...brandProfile, description: e.target.value})}
                />
                <div className="form-text">Brief description of your brand</div>
              </div>

              <div className="form-group">
                <label className="form-label">Website</label>
                <input 
                  type="url" 
                  className="form-control" 
                  value={brandProfile.website}
                  onChange={(e) => setBrandProfile({...brandProfile, website: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Industry</label>
                <select 
                  className="form-control" 
                  value={brandProfile.industry}
                  onChange={(e) => setBrandProfile({...brandProfile, industry: e.target.value})}
                >
                  <option value="Technology">Technology</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Finance">Finance</option>
                  <option value="Retail">Retail</option>
                  <option value="Education">Education</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Address</label>
                <textarea 
                  className="form-control" 
                  rows="2"
                  value={brandProfile.address}
                  onChange={(e) => setBrandProfile({...brandProfile, address: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contact Email</label>
                <input 
                  type="email" 
                  className="form-control" 
                  value={brandProfile.contactEmail}
                  onChange={(e) => setBrandProfile({...brandProfile, contactEmail: e.target.value})}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contact Phone</label>
                <input 
                  type="tel" 
                  className="form-control" 
                  value={brandProfile.contactPhone}
                  onChange={(e) => setBrandProfile({...brandProfile, contactPhone: e.target.value})}
                />
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </form>
          </div>
        )}

        {/* Integrations Tab */}
        {activeTab === 'integrations' && (
          <div className="settings-section">
            <h2 className="section-title">Integrations</h2>
            
            <form onSubmit={handleIntegrationSubmit}>
              <div className="integration-grid">
                <div className="integration-card">
                  <h3>Webhook Integration</h3>
                  <div className="form-group">
                    <label className="form-label">
                      <input 
                        type="checkbox" 
                        checked={integrations.webhook.enabled}
                        onChange={(e) => setIntegrations({
                          ...integrations, 
                          webhook: {...integrations.webhook, enabled: e.target.checked}
                        })}
                      />
                      Enable Webhook
                    </label>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Webhook URL</label>
                    <input 
                      type="url" 
                      className="form-control" 
                      value={integrations.webhook.url}
                      onChange={(e) => setIntegrations({
                        ...integrations, 
                        webhook: {...integrations.webhook, url: e.target.value}
                      })}
                      disabled={!integrations.webhook.enabled}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Webhook Secret</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={integrations.webhook.secret}
                      onChange={(e) => setIntegrations({
                        ...integrations, 
                        webhook: {...integrations.webhook, secret: e.target.value}
                      })}
                      disabled={!integrations.webhook.enabled}
                    />
                  </div>
                </div>

                <div className="integration-card">
                  <h3>API Integration</h3>
                  <div className="form-group">
                    <label className="form-label">
                      <input 
                        type="checkbox" 
                        checked={integrations.api.enabled}
                        onChange={(e) => setIntegrations({
                          ...integrations, 
                          api: {...integrations.api, enabled: e.target.checked}
                        })}
                      />
                      Enable API Access
                    </label>
                  </div>
                  <div className="form-group">
                    <label className="form-label">API Key</label>
                    <input 
                      type="text" 
                      className="form-control" 
                      value={integrations.api.key}
                      onChange={(e) => setIntegrations({
                        ...integrations, 
                        api: {...integrations.api, key: e.target.value}
                      })}
                      disabled={!integrations.api.enabled}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Rate Limit (requests/hour)</label>
                    <input 
                      type="number" 
                      className="form-control" 
                      value={integrations.api.rateLimit}
                      onChange={(e) => setIntegrations({
                        ...integrations, 
                        api: {...integrations.api, rateLimit: parseInt(e.target.value)}
                      })}
                      disabled={!integrations.api.enabled}
                    />
                  </div>
                </div>

                <div className="integration-card">
                  <h3>Email Integration</h3>
                  <div className="form-group">
                    <label className="form-label">
                      <input 
                        type="checkbox" 
                        checked={integrations.email.enabled}
                        onChange={(e) => setIntegrations({
                          ...integrations, 
                          email: {...integrations.email, enabled: e.target.checked}
                        })}
                      />
                      Enable Email Integration
                    </label>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Email Address</label>
                    <input 
                      type="email" 
                      className="form-control" 
                      value={integrations.email.address}
                      onChange={(e) => setIntegrations({
                        ...integrations, 
                        email: {...integrations.email, address: e.target.value}
                      })}
                      disabled={!integrations.email.enabled}
                    />
                  </div>
                </div>
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Saving...' : 'Save Integration Settings'}
              </button>
            </form>
          </div>
        )}

        {/* Team Management Tab */}
        {activeTab === 'team' && (
          <div className="settings-section">
            <h2 className="section-title">Team Management</h2>
            
            <div className="team-header">
              <h3>Team Members ({teamMembers.length})</h3>
              <button className="btn btn-primary" onClick={addTeamMember}>
                + Add Team Member
              </button>
            </div>

            <div className="team-list">
              {teamMembers.map((member) => (
                <div key={member.id} className="team-member-card">
                  <div className="member-info">
                    <div className="member-avatar">
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="member-details">
                      <h4>{member.name || 'New Member'}</h4>
                      <p>{member.email || 'email@example.com'}</p>
                      <span className={`status-badge ${member.status}`}>
                        {member.status}
                      </span>
                    </div>
                  </div>
                  <div className="member-actions">
                    <select 
                      className="form-control role-select"
                      value={member.role}
                      onChange={(e) => {
                        const updatedMembers = teamMembers.map(m => 
                          m.id === member.id ? {...m, role: e.target.value} : m
                        );
                        setTeamMembers(updatedMembers);
                      }}
                    >
                      <option value="admin">Admin</option>
                      <option value="agent">Agent</option>
                      <option value="viewer">Viewer</option>
                    </select>
                    <button 
                      className="btn btn-danger btn-sm"
                      onClick={() => removeTeamMember(member.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="settings-section">
            <h2 className="section-title">Notification Preferences</h2>
            
            <form onSubmit={handleNotificationSubmit}>
              <div className="notification-group">
                <h3>Complaint Notifications</h3>
                
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="newComplaints"
                    checked={notifications.newComplaints}
                    onChange={(e) => setNotifications({...notifications, newComplaints: e.target.checked})}
                  />
                  <label htmlFor="newComplaints">
                    <strong>New complaints</strong><br />
                    <span className="form-text">Get notified when new complaints are received</span>
                  </label>
                </div>

                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="urgentComplaints"
                    checked={notifications.urgentComplaints}
                    onChange={(e) => setNotifications({...notifications, urgentComplaints: e.target.checked})}
                  />
                  <label htmlFor="urgentComplaints">
                    <strong>Urgent complaints</strong><br />
                    <span className="form-text">Immediate notification for high-priority complaints</span>
                  </label>
                </div>
              </div>

              <div className="notification-group">
                <h3>Report Notifications</h3>
                
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="dailyDigest"
                    checked={notifications.dailyDigest}
                    onChange={(e) => setNotifications({...notifications, dailyDigest: e.target.checked})}
                  />
                  <label htmlFor="dailyDigest">
                    <strong>Daily digest</strong><br />
                    <span className="form-text">Summary of all complaints received in the last 24 hours</span>
                  </label>
                </div>

                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="weeklyReport"
                    checked={notifications.weeklyReport}
                    onChange={(e) => setNotifications({...notifications, weeklyReport: e.target.checked})}
                  />
                  <label htmlFor="weeklyReport">
                    <strong>Weekly report</strong><br />
                    <span className="form-text">Comprehensive weekly analytics and insights</span>
                  </label>
                </div>
              </div>

              <div className="notification-group">
                <h3>Delivery Methods</h3>
                
                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="emailNotifications"
                    checked={notifications.emailNotifications}
                    onChange={(e) => setNotifications({...notifications, emailNotifications: e.target.checked})}
                  />
                  <label htmlFor="emailNotifications">
                    <strong>Email notifications</strong><br />
                    <span className="form-text">Receive notifications via email</span>
                  </label>
                </div>

                <div className="form-check">
                  <input 
                    type="checkbox" 
                    id="smsNotifications"
                    checked={notifications.smsNotifications}
                    onChange={(e) => setNotifications({...notifications, smsNotifications: e.target.checked})}
                  />
                  <label htmlFor="smsNotifications">
                    <strong>SMS notifications</strong><br />
                    <span className="form-text">Receive urgent notifications via SMS</span>
                  </label>
                </div>
              </div>

              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Saving...' : 'Save Notification Preferences'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
