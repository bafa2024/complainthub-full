import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import './Admin.css';

const AdminSettings = () => {
    const [settings, setSettings] = useState({
        // API Credentials
        openAiKey: '',
        twilioSid: '',
        twilioToken: '',
        deepgramKey: '',
        stripeSecretKey: '',
        stripePublishableKey: '',
        
        // Business Rules
        feeAmount: '50',
        resolutionWindow: '24',
        maxTicketsPerUser: '10',
        autoCloseDays: '7',
        satisfactionThreshold: '3.5',
        
        // System Configuration
        systemName: 'ComplaintHub Bot',
        systemEmail: 'admin@complainthub.com',
        timezone: 'Asia/Kolkata',
        maintenanceMode: false,
        debugMode: false,
        
        // Security Settings
        sessionTimeout: '8',
        maxLoginAttempts: '5',
        passwordMinLength: '8',
        requireTwoFactor: false,
        allowedDomains: '',
        
        // Notification Settings
        emailNotifications: true,
        smsNotifications: true,
        pushNotifications: true,
        notificationFrequency: 'immediate',
        
        // Integration Settings
        enableWhatsApp: true,
        enableTelegram: true,
        enableVoice: true,
        enableEmail: true,
        
        // Analytics Settings
        enableAnalytics: true,
        dataRetentionDays: '365',
        enableTracking: true,
        
        // Backup Settings
        autoBackup: true,
        backupFrequency: 'daily',
        backupRetention: '30'
    });
    
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [activeTab, setActiveTab] = useState('general');

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        try {
            setLoading(true);
            const settingsData = await adminService.getSystemSettings();
            setSettings(prev => ({ ...prev, ...settingsData }));
        } catch (err) {
            console.error('Error loading settings:', err);
            setError('Failed to load settings');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setSettings(prev => ({ 
            ...prev, 
            [name]: type === 'checkbox' ? checked : value 
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        setSuccess('');

        try {
            await adminService.updateSystemSettings(settings);
            setSuccess('System settings saved successfully!');
        } catch (err) {
            console.error('Error saving settings:', err);
            setError('Failed to save settings. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    const handleTestConnection = async (type) => {
        try {
            setSaving(true);
            const result = await adminService.testConnection(type);
            if (result.success) {
                setSuccess(`${type} connection test successful!`);
            } else {
                setError(`${type} connection test failed: ${result.error}`);
            }
        } catch (err) {
            setError(`${type} connection test failed: ${err.message}`);
        } finally {
            setSaving(false);
        }
    };

    const handleSystemRestart = async () => {
        if (window.confirm('Are you sure you want to restart the system? This will temporarily interrupt service.')) {
            try {
                setSaving(true);
                await adminService.restartSystem();
                setSuccess('System restart initiated successfully!');
            } catch (err) {
                setError('Failed to restart system: ' + err.message);
            } finally {
                setSaving(false);
            }
        }
    };

    if (loading) {
        return (
            <div className="admin-settings">
                <div className="page-container">
                    <div className="page-header">
                        <h1 className="page-title">
                            <i className="fas fa-cog me-2"></i>
                            System Settings
                        </h1>
                    </div>
                    <div className="text-center py-5">
                        <i className="fas fa-spinner fa-spin fa-2x text-muted"></i>
                        <p className="mt-3">Loading settings...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="admin-settings">
            <div className="page-container">
                <div className="page-header">
                    <h1 className="page-title">
                        <i className="fas fa-cog me-2"></i>
                        System Settings
                    </h1>
                    <p className="page-subtitle">Configure system-wide settings and integrations</p>
                </div>

                {error && (
                    <div className="alert alert-danger alert-dismissible fade show mb-3">
                        <i className="fas fa-exclamation-triangle me-2"></i>
                        {error}
                        <button type="button" className="btn-close" onClick={() => setError('')}></button>
                    </div>
                )}
                
                {success && (
                    <div className="alert alert-success alert-dismissible fade show mb-3">
                        <i className="fas fa-check-circle me-2"></i>
                        {success}
                        <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
                    </div>
                )}

                {/* Settings Navigation */}
                <div className="settings-nav mb-4">
                    <button 
                        className={`nav-btn ${activeTab === 'general' ? 'active' : ''}`}
                        onClick={() => setActiveTab('general')}
                    >
                        <i className="fas fa-cog me-2"></i>
                        General
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'api' ? 'active' : ''}`}
                        onClick={() => setActiveTab('api')}
                    >
                        <i className="fas fa-key me-2"></i>
                        API Credentials
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'business' ? 'active' : ''}`}
                        onClick={() => setActiveTab('business')}
                    >
                        <i className="fas fa-chart-line me-2"></i>
                        Business Rules
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'security' ? 'active' : ''}`}
                        onClick={() => setActiveTab('security')}
                    >
                        <i className="fas fa-shield-alt me-2"></i>
                        Security
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'notifications' ? 'active' : ''}`}
                        onClick={() => setActiveTab('notifications')}
                    >
                        <i className="fas fa-bell me-2"></i>
                        Notifications
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'integrations' ? 'active' : ''}`}
                        onClick={() => setActiveTab('integrations')}
                    >
                        <i className="fas fa-plug me-2"></i>
                        Integrations
                    </button>
                    <button 
                        className={`nav-btn ${activeTab === 'advanced' ? 'active' : ''}`}
                        onClick={() => setActiveTab('advanced')}
                    >
                        <i className="fas fa-tools me-2"></i>
                        Advanced
                    </button>
                </div>

                <form onSubmit={handleSubmit}>
                    {/* General Settings */}
                    {activeTab === 'general' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-cog me-2"></i>General Configuration</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="systemName" className="form-label">System Name</label>
                                                <input 
                                                    type="text" 
                                                    id="systemName" 
                                                    name="systemName" 
                                                    className="form-control" 
                                                    value={settings.systemName} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="systemEmail" className="form-label">System Email</label>
                                                <input 
                                                    type="email" 
                                                    id="systemEmail" 
                                                    name="systemEmail" 
                                                    className="form-control" 
                                                    value={settings.systemEmail} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="timezone" className="form-label">Timezone</label>
                                                <select 
                                                    id="timezone" 
                                                    name="timezone" 
                                                    className="form-select" 
                                                    value={settings.timezone} 
                                                    onChange={handleInputChange}
                                                >
                                                    <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                                                    <option value="UTC">UTC</option>
                                                    <option value="America/New_York">America/New_York (EST)</option>
                                                    <option value="Europe/London">Europe/London (GMT)</option>
                                                </select>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="dataRetentionDays" className="form-label">Data Retention (Days)</label>
                                                <input 
                                                    type="number" 
                                                    id="dataRetentionDays" 
                                                    name="dataRetentionDays" 
                                                    className="form-control" 
                                                    value={settings.dataRetentionDays} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="maintenanceMode" 
                                                    name="maintenanceMode" 
                                                    className="form-check-input" 
                                                    checked={settings.maintenanceMode} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="maintenanceMode" className="form-check-label">Maintenance Mode</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="debugMode" 
                                                    name="debugMode" 
                                                    className="form-check-input" 
                                                    checked={settings.debugMode} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="debugMode" className="form-check-label">Debug Mode</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* API Credentials */}
                    {activeTab === 'api' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-key me-2"></i>API Credentials</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="openAiKey" className="form-label">OpenAI API Key</label>
                                                <div className="input-group">
                                                    <input 
                                                        type="password" 
                                                        id="openAiKey" 
                                                        name="openAiKey" 
                                                        className="form-control" 
                                                        value={settings.openAiKey} 
                                                        onChange={handleInputChange} 
                                                    />
                                                    <button 
                                                        type="button" 
                                                        className="btn btn-outline-secondary"
                                                        onClick={() => handleTestConnection('openai')}
                                                    >
                                                        Test
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="twilioSid" className="form-label">Twilio Account SID</label>
                                                <input 
                                                    type="password" 
                                                    id="twilioSid" 
                                                    name="twilioSid" 
                                                    className="form-control" 
                                                    value={settings.twilioSid} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="twilioToken" className="form-label">Twilio Auth Token</label>
                                                <div className="input-group">
                                                    <input 
                                                        type="password" 
                                                        id="twilioToken" 
                                                        name="twilioToken" 
                                                        className="form-control" 
                                                        value={settings.twilioToken} 
                                                        onChange={handleInputChange} 
                                                    />
                                                    <button 
                                                        type="button" 
                                                        className="btn btn-outline-secondary"
                                                        onClick={() => handleTestConnection('twilio')}
                                                    >
                                                        Test
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="deepgramKey" className="form-label">Deepgram API Key</label>
                                                <div className="input-group">
                                                    <input 
                                                        type="password" 
                                                        id="deepgramKey" 
                                                        name="deepgramKey" 
                                                        className="form-control" 
                                                        value={settings.deepgramKey} 
                                                        onChange={handleInputChange} 
                                                    />
                                                    <button 
                                                        type="button" 
                                                        className="btn btn-outline-secondary"
                                                        onClick={() => handleTestConnection('deepgram')}
                                                    >
                                                        Test
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="stripeSecretKey" className="form-label">Stripe Secret Key</label>
                                                <input 
                                                    type="password" 
                                                    id="stripeSecretKey" 
                                                    name="stripeSecretKey" 
                                                    className="form-control" 
                                                    value={settings.stripeSecretKey} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="stripePublishableKey" className="form-label">Stripe Publishable Key</label>
                                                <input 
                                                    type="text" 
                                                    id="stripePublishableKey" 
                                                    name="stripePublishableKey" 
                                                    className="form-control" 
                                                    value={settings.stripePublishableKey} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Business Rules */}
                    {activeTab === 'business' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-chart-line me-2"></i>Business Rules</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="feeAmount" className="form-label">Unresolved Complaint Fee (Credits)</label>
                                                <input 
                                                    type="number" 
                                                    id="feeAmount" 
                                                    name="feeAmount" 
                                                    className="form-control" 
                                                    value={settings.feeAmount} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="resolutionWindow" className="form-label">Free Resolution Window (Hours)</label>
                                                <input 
                                                    type="number" 
                                                    id="resolutionWindow" 
                                                    name="resolutionWindow" 
                                                    className="form-control" 
                                                    value={settings.resolutionWindow} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="maxTicketsPerUser" className="form-label">Max Tickets Per User</label>
                                                <input 
                                                    type="number" 
                                                    id="maxTicketsPerUser" 
                                                    name="maxTicketsPerUser" 
                                                    className="form-control" 
                                                    value={settings.maxTicketsPerUser} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="autoCloseDays" className="form-label">Auto-Close After (Days)</label>
                                                <input 
                                                    type="number" 
                                                    id="autoCloseDays" 
                                                    name="autoCloseDays" 
                                                    className="form-control" 
                                                    value={settings.autoCloseDays} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="satisfactionThreshold" className="form-label">Satisfaction Threshold</label>
                                                <input 
                                                    type="number" 
                                                    id="satisfactionThreshold" 
                                                    name="satisfactionThreshold" 
                                                    className="form-control" 
                                                    value={settings.satisfactionThreshold} 
                                                    onChange={handleInputChange} 
                                                    step="0.1"
                                                    min="1"
                                                    max="5"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Security Settings */}
                    {activeTab === 'security' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-shield-alt me-2"></i>Security Settings</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="sessionTimeout" className="form-label">Session Timeout (Hours)</label>
                                                <input 
                                                    type="number" 
                                                    id="sessionTimeout" 
                                                    name="sessionTimeout" 
                                                    className="form-control" 
                                                    value={settings.sessionTimeout} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="maxLoginAttempts" className="form-label">Max Login Attempts</label>
                                                <input 
                                                    type="number" 
                                                    id="maxLoginAttempts" 
                                                    name="maxLoginAttempts" 
                                                    className="form-control" 
                                                    value={settings.maxLoginAttempts} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="passwordMinLength" className="form-label">Minimum Password Length</label>
                                                <input 
                                                    type="number" 
                                                    id="passwordMinLength" 
                                                    name="passwordMinLength" 
                                                    className="form-control" 
                                                    value={settings.passwordMinLength} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="allowedDomains" className="form-label">Allowed Email Domains</label>
                                                <input 
                                                    type="text" 
                                                    id="allowedDomains" 
                                                    name="allowedDomains" 
                                                    className="form-control" 
                                                    value={settings.allowedDomains} 
                                                    onChange={handleInputChange} 
                                                    placeholder="example.com, company.com"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="requireTwoFactor" 
                                                    name="requireTwoFactor" 
                                                    className="form-check-input" 
                                                    checked={settings.requireTwoFactor} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="requireTwoFactor" className="form-check-label">Require Two-Factor Authentication</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Notification Settings */}
                    {activeTab === 'notifications' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-bell me-2"></i>Notification Settings</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="emailNotifications" 
                                                    name="emailNotifications" 
                                                    className="form-check-input" 
                                                    checked={settings.emailNotifications} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="emailNotifications" className="form-check-label">Email Notifications</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="smsNotifications" 
                                                    name="smsNotifications" 
                                                    className="form-check-input" 
                                                    checked={settings.smsNotifications} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="smsNotifications" className="form-check-label">SMS Notifications</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="pushNotifications" 
                                                    name="pushNotifications" 
                                                    className="form-check-input" 
                                                    checked={settings.pushNotifications} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="pushNotifications" className="form-check-label">Push Notifications</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="notificationFrequency" className="form-label">Notification Frequency</label>
                                                <select 
                                                    id="notificationFrequency" 
                                                    name="notificationFrequency" 
                                                    className="form-select" 
                                                    value={settings.notificationFrequency} 
                                                    onChange={handleInputChange}
                                                >
                                                    <option value="immediate">Immediate</option>
                                                    <option value="hourly">Hourly</option>
                                                    <option value="daily">Daily</option>
                                                    <option value="weekly">Weekly</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Integration Settings */}
                    {activeTab === 'integrations' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-plug me-2"></i>Integration Settings</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableWhatsApp" 
                                                    name="enableWhatsApp" 
                                                    className="form-check-input" 
                                                    checked={settings.enableWhatsApp} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableWhatsApp" className="form-check-label">Enable WhatsApp Integration</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableTelegram" 
                                                    name="enableTelegram" 
                                                    className="form-check-input" 
                                                    checked={settings.enableTelegram} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableTelegram" className="form-check-label">Enable Telegram Integration</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableVoice" 
                                                    name="enableVoice" 
                                                    className="form-check-input" 
                                                    checked={settings.enableVoice} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableVoice" className="form-check-label">Enable Voice Integration</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableEmail" 
                                                    name="enableEmail" 
                                                    className="form-check-input" 
                                                    checked={settings.enableEmail} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableEmail" className="form-check-label">Enable Email Integration</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Advanced Settings */}
                    {activeTab === 'advanced' && (
                        <div className="settings-section">
                            <div className="card">
                                <div className="card-header">
                                    <h4><i className="fas fa-tools me-2"></i>Advanced Settings</h4>
                                </div>
                                <div className="card-body">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableAnalytics" 
                                                    name="enableAnalytics" 
                                                    className="form-check-input" 
                                                    checked={settings.enableAnalytics} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableAnalytics" className="form-check-label">Enable Analytics</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="enableTracking" 
                                                    name="enableTracking" 
                                                    className="form-check-input" 
                                                    checked={settings.enableTracking} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="enableTracking" className="form-check-label">Enable User Tracking</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="form-check form-switch">
                                                <input 
                                                    type="checkbox" 
                                                    id="autoBackup" 
                                                    name="autoBackup" 
                                                    className="form-check-input" 
                                                    checked={settings.autoBackup} 
                                                    onChange={handleInputChange} 
                                                />
                                                <label htmlFor="autoBackup" className="form-check-label">Auto Backup</label>
                                            </div>
                                        </div>
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="backupFrequency" className="form-label">Backup Frequency</label>
                                                <select 
                                                    id="backupFrequency" 
                                                    name="backupFrequency" 
                                                    className="form-select" 
                                                    value={settings.backupFrequency} 
                                                    onChange={handleInputChange}
                                                >
                                                    <option value="daily">Daily</option>
                                                    <option value="weekly">Weekly</option>
                                                    <option value="monthly">Monthly</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6">
                                            <div className="mb-3">
                                                <label htmlFor="backupRetention" className="form-label">Backup Retention (Days)</label>
                                                <input 
                                                    type="number" 
                                                    id="backupRetention" 
                                                    name="backupRetention" 
                                                    className="form-control" 
                                                    value={settings.backupRetention} 
                                                    onChange={handleInputChange} 
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="settings-actions mt-4">
                        <div className="d-flex gap-2">
                            <button type="submit" className="btn btn-primary" disabled={saving}>
                                {saving ? (
                                    <>
                                        <i className="fas fa-spinner fa-spin me-2"></i>
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <i className="fas fa-save me-2"></i>
                                        Save Settings
                                    </>
                                )}
                            </button>
                            <button 
                                type="button" 
                                className="btn btn-warning" 
                                onClick={handleSystemRestart}
                                disabled={saving}
                            >
                                <i className="fas fa-redo me-2"></i>
                                Restart System
                            </button>
                            <Link to="/admin/dashboard" className="btn btn-secondary">
                                <i className="fas fa-arrow-left me-2"></i>
                                Back to Dashboard
                            </Link>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AdminSettings;