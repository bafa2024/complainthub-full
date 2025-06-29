import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './auth.css'; // Import the stylesheet

const BrandLogin = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login, logout, mockupMode } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const user = await login(email, password);
            // Ensure only brand users or admins can access the brand dashboard
            if (user.role === 'brand_user' || user.role === 'admin') {
                navigate('/brand/dashboard');
            } else {
                setError('Access denied. This login is for brand accounts only.');
                logout(); // Log out the non-brand user to be safe
            }
        } catch (err) {
            setError('Login failed. Please check your credentials.');
            console.error(err);
        } finally {
            setLoading(false);
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
                                onClick={() => navigate('/brand/dashboard')} 
                                className="btn btn-success"
                            >
                                Brand Dashboard
                            </button>
                            <button 
                                onClick={() => navigate('/brand/billing')} 
                                className="btn btn-info"
                            >
                                Brand Billing
                            </button>
                            <button 
                                onClick={() => navigate('/brand/team')} 
                                className="btn btn-secondary"
                            >
                                Brand Team
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
                <h2>Brand Login</h2>
                <p>Access your brand dashboard to manage customer complaints.</p>

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
                <button type="submit" className="btn btn-success" disabled={loading}>
                    {loading ? 'Logging in...' : 'Login'}
                </button>
                <p className="auth-switch">
                    Don't have a brand account? <Link to="/brand/signup">Sign Up</Link>
                </p>
                <p className="auth-switch">
                    Are you a customer? <Link to="/login">Customer Login</Link>
                </p>
            </form>
        </div>
    );
};

export default BrandLogin;