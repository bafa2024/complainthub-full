import React from 'react';
import { Link } from 'react-router-dom'; // Ensure Link is imported
import './Admin.css';

const AdminDashboard = () => {
  return (
    <div className="admin-container">
      <h1>Admin Dashboard</h1>
      <p>Welcome, Admin. Manage the platform from here.</p>
      <div className="admin-navigation">
        {/* These cards are now functional links */}
        <Link to="/admin/brands" className="admin-nav-card">
          <h3>Manage Brands</h3>
          <p>View, create, and edit brand accounts.</p>
        </Link>
        <Link to="/admin/users" className="admin-nav-card">
          <h3>Manage Users</h3>
          <p>View all users and their roles.</p>
        </Link>
         <Link to="#" className="admin-nav-card">
          <h3>System Settings</h3>
          <p>Manage API keys and global rules (coming soon).</p>
        </Link>
      </div>
    </div>
  );
};

export default AdminDashboard;