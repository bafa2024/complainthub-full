import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';

const AdminSettings = () => {
    const [settings, setSettings] = useState({
        openAiKey: '',
        twilioSid: '',
        deepgramKey: '',
        feeAmount: '50',
        resolutionWindow: '24'
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        const loadSettings = async () => {
            try {
                // In a real implementation, you'd fetch current settings
                // For now, we'll use default values
                setLoading(false);
            } catch (err) {
                console.error('Error loading settings:', err);
                setError('Failed to load settings');
                setLoading(false);
            }
        };
        loadSettings();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({ ...prev, [name]: value }));
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

    if (loading) return <div>Loading...</div>;

    return (
        <div className="container mt-4">
            <h1 className="mb-4">System Settings</h1>
            {error && <div className="alert alert-danger">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <div className="card">
                <div className="card-header">
                    <h4>API Credentials & Rules</h4>
                </div>
                <div className="card-body">
                    <form onSubmit={handleSubmit}>
                        <fieldset>
                            <legend>Third-Party API Keys</legend>
                            <div className="mb-3">
                                <label htmlFor="openAiKey" className="form-label">OpenAI API Key</label>
                                <input type="password" id="openAiKey" name="openAiKey" className="form-control" value={settings.openAiKey} onChange={handleInputChange} />
                            </div>
                            <div className="mb-3">
                                <label htmlFor="twilioSid" className="form-label">Twilio Account SID</label>
                                <input type="password" id="twilioSid" name="twilioSid" className="form-control" value={settings.twilioSid} onChange={handleInputChange} />
                            </div>
                             <div className="mb-3">
                                <label htmlFor="deepgramKey" className="form-label">Deepgram API Key</label>
                                <input type="password" id="deepgramKey" name="deepgramKey" className="form-control" value={settings.deepgramKey} onChange={handleInputChange} />
                            </div>
                        </fieldset>
                        <fieldset className="mt-4">
                            <legend>Business Rules</legend>
                             <div className="mb-3">
                                <label htmlFor="feeAmount" className="form-label">Unresolved Complaint Fee (in credits)</label>
                                <input type="number" id="feeAmount" name="feeAmount" className="form-control" value={settings.feeAmount} onChange={handleInputChange} />
                            </div>
                             <div className="mb-3">
                                <label htmlFor="resolutionWindow" className="form-label">Free Resolution Window (in hours)</label>
                                <input type="number" id="resolutionWindow" name="resolutionWindow" className="form-control" value={settings.resolutionWindow} onChange={handleInputChange} />
                            </div>
                        </fieldset>
                        <div className="mt-4">
                            <button type="submit" className="btn btn-primary" disabled={saving}>
                                {saving ? 'Saving...' : 'Save Settings'}
                            </button>
                            <Link to="/admin/dashboard" className="btn btn-secondary ms-2">Cancel</Link>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AdminSettings;