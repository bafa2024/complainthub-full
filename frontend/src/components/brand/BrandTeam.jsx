import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const BrandTeam = () => {
    // Mock data for UI demonstration
    const [teamMembers, setTeamMembers] = useState([
        { id: 1, name: 'Alice Johnson', email: 'alice@brand.com', role: 'Manager' },
        { id: 2, name: 'Bob Williams', email: 'bob@brand.com', role: 'Agent' },
        { id: 3, name: 'Charlie Brown', email: 'charlie@brand.com', role: 'Agent' },
    ]);
    
    const [showInviteForm, setShowInviteForm] = useState(false);
    const [newMemberEmail, setNewMemberEmail] = useState('');
    const [newMemberRole, setNewMemberRole] = useState('Agent');

    const handleInviteSubmit = (e) => {
        e.preventDefault();
        if (!newMemberEmail) {
            alert('Please enter an email address.');
            return;
        }
        alert(`Invitation sent to ${newMemberEmail} with the role of ${newMemberRole}. (Mocked)`);
        // In a real app, this would call a backend service.
        setShowInviteForm(false);
        setNewMemberEmail('');
    };

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Manage Team</h1>
                <button className="btn btn-primary" onClick={() => setShowInviteForm(!showInviteForm)}>
                    + Invite New Member
                </button>
            </div>

            {/* Invite New Member Form */}
            {showInviteForm && (
                <div className="card mb-4">
                    <div className="card-body">
                        <h5 className="card-title">Invite New Team Member</h5>
                        <form onSubmit={handleInviteSubmit}>
                            <div className="row g-3 align-items-end">
                                <div className="col-md-5">
                                    <label htmlFor="email" className="form-label">Email Address</label>
                                    <input type="email" className="form-control" id="email" value={newMemberEmail} onChange={(e) => setNewMemberEmail(e.target.value)} required />
                                </div>
                                <div className="col-md-4">
                                    <label htmlFor="role" className="form-label">Role</label>
                                    <select id="role" className="form-select" value={newMemberRole} onChange={(e) => setNewMemberRole(e.target.value)}>
                                        <option>Agent</option>
                                        <option>Manager</option>
                                    </select>
                                </div>
                                <div className="col-md-3">
                                    <button type="submit" className="btn btn-success w-100">Send Invite</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Team Members List */}
            <div className="card">
                <div className="card-header">
                    <h4>Current Members</h4>
                </div>
                <ul className="list-group list-group-flush">
                    {teamMembers.map(member => (
                        <li key={member.id} className="list-group-item d-flex justify-content-between align-items-center">
                            <div>
                                <div className="fw-bold">{member.name}</div>
                                <div className="text-muted">{member.email}</div>
                            </div>
                            <span className="badge bg-secondary">{member.role}</span>
                        </li>
                    ))}
                </ul>
            </div>
             <Link to="/brand/dashboard" className="btn btn-link mt-3">← Go Back to Dashboard</Link>
        </div>
    );
};

export default BrandTeam;