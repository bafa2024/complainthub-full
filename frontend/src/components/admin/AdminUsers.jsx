// frontend/src/components/admin/AdminUsers.jsx

import React, { useState, useEffect } from 'react';
import adminService from '../../services/adminService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminUsers = () => {
    const [users, setUsers] = useState([]);
    const [filteredUsers, setFilteredUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    
    // State for the create/edit form
    const [showForm, setShowForm] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [currentUser, setCurrentUser] = useState({
        id: null,
        email: '',
        full_name: '',
        phone_number: '',
        role: 'user',
        brand_id: null,
        password: ''
    });

    const [deletingId, setDeletingId] = useState(null);
    const [deleteError, setDeleteError] = useState('');

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const data = await adminService.getAllUsers();
            setUsers(data);
            setFilteredUsers(data);
        } catch (err) {
            setError('Could not load users.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    // Filter users based on search term
    useEffect(() => {
        if (searchTerm.trim() === '') {
            setFilteredUsers(users);
        } else {
            const filtered = users.filter(user => 
                user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                user.role?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                user.phone_number?.includes(searchTerm) ||
                user.brand_id?.toString().includes(searchTerm)
            );
            setFilteredUsers(filtered);
        }
    }, [searchTerm, users]);

    const handleCreateNew = () => {
        setIsEditing(false);
        setCurrentUser({
            id: null,
            email: '',
            full_name: '',
            phone_number: '',
            role: 'user',
            brand_id: null,
            password: ''
        });
        setShowForm(true);
    };

    const handleEdit = (user) => {
        setIsEditing(true);
        setCurrentUser({
            id: user.id,
            email: user.email || '',
            full_name: user.full_name || '',
            phone_number: user.phone_number || '',
            role: user.role || 'user',
            brand_id: user.brand_id || null,
            password: '' // Don't populate password for editing
        });
        setShowForm(true);
    };

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setCurrentUser(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Prepare user data (exclude password if empty during edit)
            const userData = {
                email: currentUser.email,
                full_name: currentUser.full_name,
                phone_number: currentUser.phone_number,
                role: currentUser.role,
                brand_id: currentUser.brand_id ? parseInt(currentUser.brand_id) : null
            };

            // Only include password if it's provided (for create) or if editing and password is provided
            if (!isEditing || (isEditing && currentUser.password)) {
                userData.password = currentUser.password;
            }

            if (isEditing) {
                await adminService.updateUser(currentUser.id, userData);
            } else {
                await adminService.createUser(userData);
            }
            
            setShowForm(false);
            setCurrentUser({
                id: null,
                email: '',
                full_name: '',
                phone_number: '',
                role: 'user',
                brand_id: null,
                password: ''
            });
            setSuccessMessage(`User ${isEditing ? 'updated' : 'created'} successfully!`);
            setTimeout(() => setSuccessMessage(''), 3000);
            
            await fetchUsers(); // Refresh the list
        } catch (err) {
            let backendMsg = '';
            if (err.response && err.response.data && err.response.data.detail) {
                backendMsg = err.response.data.detail;
            } else if (err.message) {
                backendMsg = err.message;
            }
            setError(`Failed to ${isEditing ? 'update' : 'create'} user. ${backendMsg ? 'Details: ' + backendMsg : 'Please check the details.'}`);
            console.error('User save error:', err);
        }
    };

    const handleDelete = async (userId) => {
        if (!window.confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;
        setDeletingId(userId);
        setDeleteError('');
        setSuccessMessage('');
        try {
            await adminService.deleteUser(userId);
            await fetchUsers();
            setSuccessMessage('User deleted successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            let backendMsg = '';
            if (err.response && err.response.data && err.response.data.detail) {
                backendMsg = err.response.data.detail;
            } else if (err.message) {
                backendMsg = err.message;
            }
            
            // Handle specific error cases
            if (err.response && err.response.status === 400) {
                setDeleteError(backendMsg || 'Cannot delete user due to associated data.');
            } else if (err.response && err.response.status === 403) {
                setDeleteError('You do not have permission to delete this user.');
            } else if (err.response && err.response.status === 404) {
                setDeleteError('User not found.');
            } else {
                setDeleteError('Failed to delete user. ' + (backendMsg ? 'Details: ' + backendMsg : 'Please try again.'));
            }
            console.error('User delete error:', err);
        } finally {
            setDeletingId(null);
        }
    };

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
    };

    const clearSearch = () => {
        setSearchTerm('');
    };

    if (loading) return <LoadingSpinner />;

    return (
        <div className="admin-container">
            <div className="admin-header">
                <h1>Manage Users</h1>
                <button className="btn btn-primary" onClick={handleCreateNew}>+ Add New User</button>
            </div>

            {error && <p className="error-message">{error}</p>}
            {successMessage && <p className="success-message">{successMessage}</p>}

            {/* Search Box */}
            <div className="search-container">
                <div className="search-box">
                    <input
                        type="text"
                        placeholder="Search users by email, name, role, phone, or brand ID..."
                        value={searchTerm}
                        onChange={handleSearchChange}
                        className="search-input"
                    />
                    {searchTerm && (
                        <button 
                            onClick={clearSearch}
                            className="search-clear"
                            title="Clear search"
                        >
                            ×
                        </button>
                    )}
                </div>
                <div className="search-info">
                    {searchTerm && (
                        <span className="search-results">
                            Showing {filteredUsers.length} of {users.length} users
                        </span>
                    )}
                </div>
            </div>

            {showForm && (
                <div className="admin-form-container">
                    <form onSubmit={handleSubmit}>
                        <h3>{isEditing ? 'Edit User' : 'Create New User'}</h3>
                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input 
                                type="email" 
                                name="email" 
                                id="email" 
                                value={currentUser.email} 
                                onChange={handleFormChange} 
                                required 
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="full_name">Full Name</label>
                            <input 
                                type="text" 
                                name="full_name" 
                                id="full_name" 
                                value={currentUser.full_name} 
                                onChange={handleFormChange} 
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="phone_number">Phone Number</label>
                            <input 
                                type="text" 
                                name="phone_number" 
                                id="phone_number" 
                                value={currentUser.phone_number} 
                                onChange={handleFormChange} 
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="role">Role</label>
                            <select 
                                name="role" 
                                id="role" 
                                value={currentUser.role} 
                                onChange={handleFormChange}
                                required
                            >
                                <option value="user">User</option>
                                <option value="brand_user">Brand User</option>
                                <option value="admin">Admin</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label htmlFor="brand_id">Brand ID (optional)</label>
                            <input 
                                type="number" 
                                name="brand_id" 
                                id="brand_id" 
                                value={currentUser.brand_id || ''} 
                                onChange={handleFormChange} 
                                placeholder="Leave empty if no brand association"
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">
                                {isEditing ? 'New Password (leave empty to keep current)' : 'Password'}
                            </label>
                            <input 
                                type="password" 
                                name="password" 
                                id="password" 
                                value={currentUser.password} 
                                onChange={handleFormChange} 
                                required={!isEditing}
                            />
                        </div>
                        <div className="form-actions">
                            <button type="submit" className="btn btn-success">
                                {isEditing ? 'Update User' : 'Create User'}
                            </button>
                            <button 
                                type="button" 
                                className="btn btn-secondary" 
                                onClick={() => setShowForm(false)}
                            >
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {deleteError && <p className="error-message">{deleteError}</p>}

            <table className="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Email</th>
                        <th>Full Name</th>
                        <th>Phone</th>
                        <th>Role</th>
                        <th>Brand ID</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredUsers.map(user => (
                        <tr key={user.id}>
                            <td>{user.id}</td>
                            <td>{user.email}</td>
                            <td>{user.full_name || 'N/A'}</td>
                            <td>{user.phone_number || 'N/A'}</td>
                            <td>
                                <span className={`badge badge-${user.role === 'admin' ? 'danger' : user.role === 'brand_user' ? 'warning' : 'primary'}`}>
                                    {user.role}
                                </span>
                            </td>
                            <td>{user.brand_id || 'N/A'}</td>
                            <td>
                                <span className={`badge badge-${user.is_active ? 'success' : 'secondary'}`}>
                                    {user.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>
                                <button 
                                    className="btn-edit" 
                                    onClick={() => handleEdit(user)}
                                >
                                    Edit
                                </button>
                                <button 
                                    className="btn-delete" 
                                    onClick={() => handleDelete(user.id)} 
                                    disabled={deletingId === user.id}
                                >
                                    {deletingId === user.id ? 'Deleting...' : 'Delete'}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            
            {filteredUsers.length === 0 && !loading && (
                <div className="no-results">
                    {searchTerm ? (
                        <p>No users found matching "{searchTerm}". Try a different search term.</p>
                    ) : (
                        <p>No users found.</p>
                    )}
                </div>
            )}
        </div>
    );
};

export default AdminUsers;