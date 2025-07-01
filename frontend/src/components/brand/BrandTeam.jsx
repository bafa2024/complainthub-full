import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import teamService from '../../services/teamService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandTeam.css';

const BrandTeam = () => {
    const [teamMembers, setTeamMembers] = useState([]);
    const [invitations, setInvitations] = useState([]);
    const [showInviteForm, setShowInviteForm] = useState(false);
    const [newMemberEmail, setNewMemberEmail] = useState('');
    const [newMemberRole, setNewMemberRole] = useState('brand_user');
    const [loading, setLoading] = useState(true);
    const [inviteLoading, setInviteLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const { user } = useAuth();

    useEffect(() => {
        fetchTeamData();
    }, []);

    const fetchTeamData = async () => {
        try {
            setLoading(true);
            setError('');
            
            // Fetch team members and invitations
            const [membersData, invitationsData] = await Promise.all([
                teamService.getTeamMembers(user?.brand_id),
                teamService.getInvitations(user?.brand_id)
            ]);
            
            setTeamMembers(membersData || []);
            setInvitations(invitationsData || []);
            
        } catch (err) {
            console.error('Error fetching team data:', err);
            setError('Failed to load team data: ' + (err.message || 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    const handleInviteSubmit = async (e) => {
        e.preventDefault();
        if (!newMemberEmail) {
            setError('Please enter an email address.');
            return;
        }

        try {
            setInviteLoading(true);
            setError('');
            setSuccess('');

            const invitationData = {
                email: newMemberEmail,
                role: newMemberRole
            };

            await teamService.sendInvitation(user?.brand_id, invitationData);
            
            setSuccess(`Invitation sent successfully to ${newMemberEmail}!`);
            setShowInviteForm(false);
            setNewMemberEmail('');
            setNewMemberRole('brand_user');
            
            // Refresh invitations list
            fetchTeamData();
            
        } catch (err) {
            console.error('Error sending invitation:', err);
            setError('Failed to send invitation: ' + (err.message || 'Unknown error'));
        } finally {
            setInviteLoading(false);
        }
    };

    const handleDeleteInvitation = async (invitationId) => {
        if (!window.confirm('Are you sure you want to delete this invitation?')) {
            return;
        }

        try {
            await teamService.deleteInvitation(user?.brand_id, invitationId);
            setSuccess('Invitation deleted successfully!');
            fetchTeamData();
        } catch (err) {
            console.error('Error deleting invitation:', err);
            setError('Failed to delete invitation: ' + (err.message || 'Unknown error'));
        }
    };

    const getRoleDisplayName = (role) => {
        switch (role) {
            case 'brand_user': return 'Agent';
            case 'admin': return 'Admin';
            default: return role;
        }
    };

    const getStatusBadge = (invitation) => {
        if (invitation.is_accepted) {
            return <span className="badge bg-success">Accepted</span>;
        }
        
        const now = new Date();
        const expiresAt = new Date(invitation.expires_at);
        
        if (expiresAt < now) {
            return <span className="badge bg-danger">Expired</span>;
        }
        
        return <span className="badge bg-warning">Pending</span>;
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="container mt-4">
                <div className="d-flex justify-content-center">
                    <LoadingSpinner />
                </div>
            </div>
        );
    }

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Manage Team</h1>
                <button 
                    className="btn btn-primary" 
                    onClick={() => setShowInviteForm(!showInviteForm)}
                    disabled={inviteLoading}
                >
                    {inviteLoading ? 'Sending...' : '+ Invite New Member'}
                </button>
            </div>

            {/* Alert Messages */}
            {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                    {error}
                    <button type="button" className="btn-close" onClick={() => setError('')}></button>
                </div>
            )}
            
            {success && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                    {success}
                    <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
                </div>
            )}

            {/* Invite New Member Form */}
            {showInviteForm && (
                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title">Invite New Team Member</h5>
                        <form onSubmit={handleInviteSubmit}>
                            <div className="row g-3 align-items-end">
                                <div className="col-md-5">
                                    <label htmlFor="email" className="form-label">Email Address</label>
                                    <input 
                                        type="email" 
                                        className="form-control" 
                                        id="email" 
                                        value={newMemberEmail} 
                                        onChange={(e) => setNewMemberEmail(e.target.value)} 
                                        required 
                                        disabled={inviteLoading}
                                    />
                                </div>
                                <div className="col-md-4">
                                    <label htmlFor="role" className="form-label">Role</label>
                                    <select 
                                        id="role" 
                                        className="form-select" 
                                        value={newMemberRole} 
                                        onChange={(e) => setNewMemberRole(e.target.value)}
                                        disabled={inviteLoading}
                                    >
                                        <option value="brand_user">Agent</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </div>
                                <div className="col-md-3">
                                    <button 
                                        type="submit" 
                                        className="btn btn-success w-100"
                                        disabled={inviteLoading}
                                    >
                                        {inviteLoading ? 'Sending...' : 'Send Invite'}
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Pending Invitations */}
            {invitations.length > 0 && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4>Pending Invitations ({invitations.length})</h4>
                    </div>
                    <div className="table-responsive">
                        <table className="table table-hover">
                            <thead>
                                <tr>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Sent</th>
                                    <th>Expires</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invitations.map(invitation => (
                                    <tr key={invitation.id}>
                                        <td>{invitation.email}</td>
                                        <td>{getRoleDisplayName(invitation.role)}</td>
                                        <td>{getStatusBadge(invitation)}</td>
                                        <td>{formatDate(invitation.created_at)}</td>
                                        <td>{formatDate(invitation.expires_at)}</td>
                                        <td>
                                            {!invitation.is_accepted && (
                                                <button 
                                                    className="btn btn-sm btn-danger"
                                                    onClick={() => handleDeleteInvitation(invitation.id)}
                                                >
                                                    Delete
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Team Members List */}
            <div className="card">
                <div className="card-header">
                    <h4>Current Team Members ({teamMembers.length})</h4>
                </div>
                {teamMembers.length === 0 ? (
                    <div className="card-body text-center text-muted">
                        <p>No team members found.</p>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table table-hover">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Status</th>
                                    <th>Joined</th>
                                </tr>
                            </thead>
                            <tbody>
                                {teamMembers.map(member => (
                                    <tr key={member.id}>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                <div className="avatar me-2">
                                                    {member.full_name ? member.full_name.charAt(0).toUpperCase() : 'U'}
                                                </div>
                                                <span>{member.full_name || 'No name'}</span>
                                            </div>
                                        </td>
                                        <td>{member.email}</td>
                                        <td>
                                            <span className="badge bg-secondary">
                                                {getRoleDisplayName(member.role)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${member.is_active ? 'bg-success' : 'bg-danger'}`}>
                                                {member.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td>{formatDate(member.created_at)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            
            <Link to="/brand/dashboard" className="btn btn-link mt-3">← Go Back to Dashboard</Link>
        </div>
    );
};

export default BrandTeam;