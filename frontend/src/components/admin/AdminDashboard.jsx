import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import ticketService from '../../services/ticketService'; // Admins can get all tickets
import LoadingSpinner from '../shared/LoadingSpinner';
import Modal from '../shared/Modal';
import brandService from '../../services/brandService';
import './Admin.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    users: 0,
    brands: 0,
    tickets: 0,
    resolved: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [addBrand, setAddBrand] = useState({ name: '', industry: '', logo_url: '', contact_info: '', support_email: '' });
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState('');

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Fetching admin dashboard data...');
      
      // Fetch all data streams concurrently
      const [usersData, brandsData, ticketsData] = await Promise.all([
        adminService.getAllUsers(),
        adminService.getAllBrands(),
        ticketService.getTickets(), // The mock service will return all tickets
      ]);

      console.log('Data fetched:', { usersData, brandsData, ticketsData });

      // Calculate stats
      const resolvedTickets = ticketsData.filter(t => t.status === 'resolved').length;
      
      const newStats = {
        users: usersData.length,
        brands: brandsData.length,
        tickets: ticketsData.length,
        resolved: resolvedTickets,
      };

      console.log('Calculated stats:', newStats);
      setStats(newStats);

    } catch (err) {
      console.error('Admin dashboard error:', err);
      setError('Failed to load dashboard data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    setAddLoading(true);
    setAddError('');
    try {
      await brandService.createBrand({
        name: addBrand.name,
        industry: addBrand.industry,
        logo_url: addBrand.logo_url,
        contact_info: addBrand.contact_info,
        support_email: addBrand.support_email
      });
      setShowAddModal(false);
      setAddBrand({ name: '', industry: '', logo_url: '', contact_info: '', support_email: '' });
      // Optionally refresh brand list if present
    } catch (err) {
      setAddError('Failed to add brand.');
    } finally {
      setAddLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  if (loading) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Admin Dashboard</h1>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Admin Dashboard</h1>
        <div className="alert alert-danger">
          <h5>Error Loading Dashboard</h5>
          <p>{error}</p>
          <button 
            className="btn btn-primary me-2" 
            onClick={fetchAllData}
          >
            Retry
          </button>
          <button 
            className="btn btn-secondary" 
            onClick={() => window.location.reload()}
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  const resolutionRate = stats.tickets > 0 ? ((stats.resolved / stats.tickets) * 100).toFixed(1) : 0;

  return (
    <div className="admin-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Admin Dashboard</h1>
        <button 
          className="btn btn-outline-primary btn-sm" 
          onClick={fetchAllData}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      <button className="btn btn-success mb-3" onClick={() => setShowAddModal(true)}>
        + Add Brand
      </button>

      {/* Stats Cards */}
      <div className="row g-4 mb-4">
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <h5 className="card-title">Total Users</h5>
              <p className="card-text display-4">{stats.users}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <h5 className="card-title">Total Brands</h5>
              <p className="card-text display-4">{stats.brands}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <h5 className="card-title">Total Complaints</h5>
              <p className="card-text display-4">{stats.tickets}</p>
            </div>
          </div>
        </div>
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <h5 className="card-title">Resolution Rate</h5>
              <p className="card-text display-4">{resolutionRate}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation and Reports */}
      <div className="row g-4">
        <div className="col-lg-8">
            <div className="card h-100">
                <div className="card-header">
                    <h4>Reports</h4>
                </div>
                <div className="card-body">
                    <p className="text-muted">Chart visualizations will be displayed here.</p>
                    <div className="chart-placeholder">
                        Complaints per Day (Chart)
                    </div>
                </div>
            </div>
        </div>
        <div className="col-lg-4">
            <div className="card h-100">
                 <div className="card-header">
                    <h4>Management</h4>
                </div>
                {/* These links are now correctly pointing to the new pages */}
                <div className="list-group list-group-flush">
                    <Link to="/admin/brands" className="list-group-item list-group-item-action">Manage Brands</Link>
                    <Link to="/admin/users" className="list-group-item list-group-item-action">Manage Users</Link>
                    <Link to="/admin/complaints" className="list-group-item list-group-item-action">Manage Complaints</Link>
                    <Link to="/admin/brands-analytics" className="list-group-item list-group-item-action">Brands Analytics</Link>
                    <Link to="/admin/reports" className="list-group-item list-group-item-action">System Reports</Link>
                    <Link to="/admin/settings" className="list-group-item list-group-item-action">System Settings</Link>
                    <Link to="/admin/billing" className="list-group-item list-group-item-action">View Billing Logs</Link>
                </div>
            </div>
        </div>
      </div>

      {showAddModal && (
        <Modal onClose={() => setShowAddModal(false)} title="Register New Brand">
          <form onSubmit={handleAdd}>
            <div className="mb-3">
              <label className="form-label">Name</label>
              <input type="text" className="form-control" value={addBrand.name} onChange={e => setAddBrand({ ...addBrand, name: e.target.value })} required />
            </div>
            <div className="mb-3">
              <label className="form-label">Industry</label>
              <input type="text" className="form-control" value={addBrand.industry} onChange={e => setAddBrand({ ...addBrand, industry: e.target.value })} />
            </div>
            <div className="mb-3">
              <label className="form-label">Logo URL</label>
              <input type="text" className="form-control" value={addBrand.logo_url} onChange={e => setAddBrand({ ...addBrand, logo_url: e.target.value })} />
            </div>
            <div className="mb-3">
              <label className="form-label">Contact Info</label>
              <input type="text" className="form-control" value={addBrand.contact_info} onChange={e => setAddBrand({ ...addBrand, contact_info: e.target.value })} />
            </div>
            <div className="mb-3">
              <label className="form-label">Default Support Email</label>
              <input type="email" className="form-control" value={addBrand.support_email} onChange={e => setAddBrand({ ...addBrand, support_email: e.target.value })} required />
            </div>
            {addError && <div className="alert alert-danger">{addError}</div>}
            <button className="btn btn-primary" type="submit" disabled={addLoading}>{addLoading ? 'Adding...' : 'Add Brand'}</button>
            <button className="btn btn-secondary ms-2" type="button" onClick={() => setShowAddModal(false)}>Cancel</button>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default AdminDashboard;
