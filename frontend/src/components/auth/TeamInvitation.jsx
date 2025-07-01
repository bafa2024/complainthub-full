import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import teamService from '../../services/teamService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './auth.css';

const TeamInvitation = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    
    const [invitation, setInvitation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    
    const [formData, setFormData] = useState({
        full_name: '',
        password: '',
        confirmPassword: '',
        phone_number: ''
    });

    useEffect(() => {
        fetchInvitationDetails();
    }, [token]);

    const fetchInvitationDetails = async () => {
        try {
            setLoading(true);
            setError('');
            
            const invitationData = await teamService.getInvitationByToken(token);
            setInvitation(invitationData);
            
        } catch (err) {
            console.error('Error fetching invitation:', err);
            setError('Invalid or expired invitation link. Please contact your team administrator.');
        } finally {
            setLoading(false);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation
        if (!formData.full_name.trim()) {
            setError('Please enter your full name.');
            return;
        }
        
        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters long.');
            return;
        }
        
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        try {
            setSubmitting(true);
            setError('');
            
            const userData = {
                full_name: formData.full_name,
                password: formData.password,
                phone_number: formData.phone_number || null
            };
            
            const result = await teamService.acceptInvitation(token, userData);
            
            // Show success message and redirect to login
            alert('Account created successfully! You can now log in with your email and password.');
            navigate('/brand/login', { 
                state: { 
                    message: 'Team invitation accepted successfully! Please log in with your new account.' 
                } 
            });
            
        } catch (err) {
            console.error('Error accepting invitation:', err);
            setError('Failed to accept invitation: ' + (err.message || 'Unknown error'));
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="auth-container">
                <div className="auth-form">
                    <div className="d-flex justify-content-center">
                        <LoadingSpinner />
                    </div>
                    <p className="text-center mt-3">Loading invitation details...</p>
                </div>
            </div>
        );
    }

    if (error && !invitation) {
        return (
            <div className="auth-container">
                <div className="auth-form">
                    <div className="alert alert-danger">
                        <h4>Invalid Invitation</h4>
                        <p>{error}</p>
                        <button 
                            className="btn btn-primary" 
                            onClick={() => navigate('/')}
                        >
                            Go to Homepage
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="auth-container">
            <form onSubmit={handleSubmit} className="auth-form">
                <div className="invitation-header">
                    <h2>🎉 You're Invited!</h2>
                    <p>Join the <strong>{invitation?.brand_name}</strong> team</p>
                </div>
                
                <div className="invitation-details">
                    <div className="detail-item">
                        <span className="label">Email:</span>
                        <span className="value">{invitation?.email}</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Role:</span>
                        <span className="value">{invitation?.role === 'brand_user' ? 'Agent' : 'Admin'}</span>
                    </div>
                    <div className="detail-item">
                        <span className="label">Expires:</span>
                        <span className="value">
                            {invitation?.expires_at ? new Date(invitation.expires_at).toLocaleDateString() : 'Unknown'}
                        </span>
                    </div>
                </div>

                {error && <div className="error-message">{error}</div>}
                
                <div className="form-group">
                    <label htmlFor="fullName">Full Name</label>
                    <input
                        type="text"
                        id="fullName"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleInputChange}
                        required
                        autoComplete="name"
                        placeholder="Enter your full name"
                    />
                </div>
                
                <div className="form-group">
                    <label htmlFor="phone">Phone Number (Optional)</label>
                    <input
                        type="tel"
                        id="phone"
                        name="phone_number"
                        value={formData.phone_number}
                        onChange={handleInputChange}
                        autoComplete="tel"
                        placeholder="Enter your phone number"
                    />
                </div>
                
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        required
                        autoComplete="new-password"
                        placeholder="Create a password (min 6 characters)"
                        minLength="6"
                    />
                </div>
                
                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        required
                        autoComplete="new-password"
                        placeholder="Confirm your password"
                        minLength="6"
                    />
                </div>
                
                <button 
                    type="submit" 
                    className="btn btn-success" 
                    disabled={submitting}
                >
                    {submitting ? 'Creating Account...' : 'Accept Invitation & Create Account'}
                </button>
                
                <div className="invitation-footer">
                    <p>
                        By accepting this invitation, you'll be able to:
                    </p>
                    <ul>
                        <li>View and respond to customer complaints</li>
                        <li>Access analytics and performance metrics</li>
                        <li>Collaborate with your team members</li>
                        <li>Manage customer relationships effectively</li>
                    </ul>
                </div>
            </form>
        </div>
    );
};

export default TeamInvitation; 