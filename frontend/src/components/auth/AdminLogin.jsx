import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './auth.css';

const AdminLogin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login, logout, mockupMode } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const user = await login(email, password);
            if (user.role === 'admin') {
                navigate('/admin/dashboard');
            } else {
                setError('Access denied. Administrator privileges required.');
                logout(); // Log out the non-admin user
            }
        } catch (err) {
            setError('Login failed. Please check your credentials.');
            console.error(err);
        }
    };

    if (mockupMode) {
        return (
            <div className="auth-container">
                <div className="auth-form">
                    <h2>🎭 Mockup Mode Active</h2>
                    <div style={{ 
                        background: '#e3f2fd', 
                        padding: '15px', 
                        borderRadius: '8px', 
                        marginBottom: '20px',
                        border: '1px solid #2196f3'
                    }}>
                        <p style={{ margin: 0, color: '#1976d2' }}>
                            <strong>Authentication is disabled.</strong> You can access all sections directly.
                        </p>
                    </div>
                    
                    <div style={{ marginBottom: '20px' }}>
                        <h4>Quick Access:</h4>
                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '15px' }}>
                            <button 
                                onClick={() => navigate('/admin/dashboard')} 
                                className="btn btn-warning"
                            >
                                Admin Dashboard
                            </button>
                            <button 
                                onClick={() => navigate('/admin/brands')} 
                                className="btn btn-info"
                            >
                                Manage Brands
                            </button>
                            <button 
                                onClick={() => navigate('/admin/users')} 
                                className="btn btn-secondary"
                            >
                                Manage Users
                            </button>
                            <button 
                                onClick={() => navigate('/admin/billing')} 
                                className="btn btn-success"
                            >
                                Billing Logs
                            </button>
                        </div>
                    </div>

                    <div style={{ 
                        background: '#f5f5f5', 
                        padding: '15px', 
                        borderRadius: '8px',
                        fontSize: '14px'
                    }}>
                        <p style={{ margin: 0, color: '#666' }}>
                            Use the role switcher in the bottom-right corner to change your role and see different views.
                        </p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <form onSubmit={handleSubmit} className="auth-form">
                <h2>Administrator Login</h2>
                <p>Access the admin panel to manage the platform.</p>
                
                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                    <label htmlFor="email">Email Address</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        autoComplete="username"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        autoComplete="current-password"
                    />
                </div>
                <button type="submit" className="btn btn-warning">
                    Login as Administrator
                </button>
            </form>
        </div>
    );
};

export default AdminLogin;