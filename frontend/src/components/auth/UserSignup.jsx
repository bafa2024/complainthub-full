import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // Import useAuth hook
import './auth.css';

const UserSignup = () => {
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const { signup, mockupMode } = useAuth(); // Get the signup function from the context
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }
        
        setError('');
        setLoading(true);

        try {
            const userData = {
                full_name: fullName,
                email: email,
                phone_number: phone,
                password: password,
                role: 'user' // Add default role
            };
            
            console.log('Submitting signup data:', userData); // Debug log
            
            await signup(userData);
            // On successful signup, redirect to login page with a success message
            navigate('/login', { state: { message: 'Signup successful! Please log in.' } });
        } catch (err) {
            setError(err.message || 'Signup failed. Please try again.');
            console.error('Signup error:', err);
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
                                onClick={() => navigate('/dashboard')} 
                                className="btn btn-primary"
                            >
                                User Dashboard
                            </button>
                            <button 
                                onClick={() => navigate('/new-complaint')} 
                                className="btn btn-success"
                            >
                                New Complaint
                            </button>
                            <button 
                                onClick={() => navigate('/lodge-voice')} 
                                className="btn btn-info"
                            >
                                Lodge Voice
                            </button>
                            <button 
                                onClick={() => navigate('/chat')} 
                                className="btn btn-secondary"
                            >
                                Chat
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
                <h2>Create Account</h2>
                <p>Join us to start managing your complaints effectively.</p>

                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                    <label htmlFor="fullName">Full Name</label>
                    <input
                        type="text"
                        id="fullName"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        required
                        autoComplete="name"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="email">Email Address</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        autoComplete="email"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="phone">Phone Number</label>
                    <input
                        type="tel"
                        id="phone"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        required
                        autoComplete="tel"
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
                        autoComplete="new-password"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        autoComplete="new-password"
                    />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Creating Account...' : 'Create Account'}
                </button>
                <p className="auth-switch">
                    Already have an account? <Link to="/login">Login</Link>
                </p>
            </form>
        </div>
    );
};

export default UserSignup;