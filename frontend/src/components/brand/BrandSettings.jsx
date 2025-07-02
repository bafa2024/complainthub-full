import React, { useState, useContext, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';
import brandService from '../../services/brandService';
import './BrandSettings.css';

export default function BrandSettings() {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [alert, setAlert] = useState({ show: false, type: '', message: '' });

  // Brand profile state
  const [brandProfile, setBrandProfile] = useState({
    name: '',
    support_email: '',
    industry: '',
    logo_url: ''
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

  // Load brand data on component mount
  useEffect(() => {
    const loadBrandData = async () => {
      try {
        setInitialLoading(true);
        const brandData = await brandService.getCurrentUserBrand();
        setBrandProfile({
          name: brandData.name || '',
          support_email: brandData.support_email || '',
          industry: brandData.industry || '',
          logo_url: brandData.logo_url || ''
        });
      } catch (error) {
        console.error('Error loading brand data:', error);
        showAlert('error', 'Failed to load brand data. Please try again.');
      } finally {
        setInitialLoading(false);
      }
    };

    if (user) {
      loadBrandData();
    }
  }, [user]);

  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: '', message: '' }), 3000);
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Map frontend fields to backend schema
      const brandUpdateData = {
        name: brandProfile.name,
        support_email: brandProfile.support_email,
        industry: brandProfile.industry,
        logo_url: brandProfile.logo_url
      };

      await brandService.updateCurrentUserBrand(brandUpdateData);
      showAlert('success', 'Brand profile updated successfully!');
    } catch (error) {
      console.error('Error updating brand profile:', error);
      showAlert('error', error.message || 'Failed to update brand profile');
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

  if (initialLoading) {
    return (
      <div className="brand-settings">
        <div className="container">
          <div className="text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <p className="mt-3">Loading brand settings...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="brand-settings">
      {/* Header */}
      <header className="settings-header">
        <div className="header-content">
          <div className="brand-info">
            <div className="brand-logo">{brandProfile.name ? brandProfile.name.charAt(0).toUpperCase() : 'B'}</div>
            <div>
              <h2>{brandProfile.name || 'Brand Settings'}</h2>
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
                <label className="form-label">Support Email</label>
                <input 
                  type="email" 
                  className="form-control" 
                  value={brandProfile.support_email}
                  onChange={(e) => setBrandProfile({...brandProfile, support_email: e.target.value})}
                  required
                />
                <div className="form-text">Primary contact email for customer support</div>
              </div>

              <div className="form-group">
                <label className="form-label">Industry</label>
                <select 
                  className="form-control" 
                  value={brandProfile.industry}
                  onChange={(e) => setBrandProfile({...brandProfile, industry: e.target.value})}
                >
                  <option value="">Select Industry</option>
                  <option value="Technology">Technology</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Finance">Finance</option>
                  <option value="Retail">Retail</option>
                  <option value="Education">Education</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Logo URL</label>
                <input 
                  type="url" 
                  className="form-control" 
                  value={brandProfile.logo_url}
                  onChange={(e) => setBrandProfile({...brandProfile, logo_url: e.target.value})}
                  placeholder="https://example.com/logo.png"
                />
                <div className="form-text">URL to your brand logo</div>
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
            
            <div className="team-members">
              <div className="team-header">
                <h3>Team Members</h3>
                <button onClick={addTeamMember} className="btn btn-success btn-sm">
                  + Add Member
                </button>
              </div>
              
              <div className="team-list">
                {teamMembers.map((member, index) => (
                  <div key={member.id} className="team-member-card">
                    <div className="member-info">
                      <input 
                        type="text" 
                        className="form-control" 
                        placeholder="Name"
                        value={member.name}
                        onChange={(e) => {
                          const updatedMembers = [...teamMembers];
                          updatedMembers[index].name = e.target.value;
                          setTeamMembers(updatedMembers);
                        }}
                      />
                      <input 
                        type="email" 
                        className="form-control" 
                        placeholder="Email"
                        value={member.email}
                        onChange={(e) => {
                          const updatedMembers = [...teamMembers];
                          updatedMembers[index].email = e.target.value;
                          setTeamMembers(updatedMembers);
                        }}
                      />
                      <select 
                        className="form-control" 
                        value={member.role}
                        onChange={(e) => {
                          const updatedMembers = [...teamMembers];
                          updatedMembers[index].role = e.target.value;
                          setTeamMembers(updatedMembers);
                        }}
                      >
                        <option value="admin">Admin</option>
                        <option value="agent">Agent</option>
                      </select>
                    </div>
                    <div className="member-actions">
                      <span className={`status-badge status-${member.status}`}>
                        {member.status}
                      </span>
                      <button 
                        onClick={() => removeTeamMember(member.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="settings-section">
            <h2 className="section-title">Notification Preferences</h2>
            
            <form onSubmit={handleNotificationSubmit}>
              <div className="notification-settings">
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.newComplaints}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        newComplaints: e.target.checked
                      })}
                    />
                    New Complaint Notifications
                  </label>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.urgentComplaints}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        urgentComplaints: e.target.checked
                      })}
                    />
                    Urgent Complaint Alerts
                  </label>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.dailyDigest}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        dailyDigest: e.target.checked
                      })}
                    />
                    Daily Digest Email
                  </label>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.weeklyReport}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        weeklyReport: e.target.checked
                      })}
                    />
                    Weekly Report
                  </label>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.emailNotifications}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        emailNotifications: e.target.checked
                      })}
                    />
                    Email Notifications
                  </label>
                </div>
                
                <div className="form-group">
                  <label className="form-label">
                    <input 
                      type="checkbox" 
                      checked={notifications.smsNotifications}
                      onChange={(e) => setNotifications({
                        ...notifications, 
                        smsNotifications: e.target.checked
                      })}
                    />
                    SMS Notifications
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
