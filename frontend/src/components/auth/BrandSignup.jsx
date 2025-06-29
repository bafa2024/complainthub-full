import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './auth.css';

const BrandSignup = () => {
    const { mockupMode } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        alert("Thank you. Your brand registration request has been submitted for review by our administrators.");
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
                <h2>Register Your Brand</h2>
                <p>Submit your details for approval by our team.</p>
                
                <div className="form-group">
                    <label htmlFor="brandName">Brand Name</label>
                    <input type="text" id="brandName" required />
                </div>
                <div className="form-group">
                    <label htmlFor="workEmail">Your Work Email</label>
                    <input type="email" id="workEmail" required />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input type="password" id="password" required />
                </div>
                <button type="submit" className="btn btn-primary">Request Approval</button>
                <p className="auth-switch">
                    Already have a brand account? <Link to="/brand/login">Brand Login</Link>
                </p>
            </form>
        </div>
    );
};

export default BrandSignup;