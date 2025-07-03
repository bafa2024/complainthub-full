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
  const [addBrand, setAddBrand] = useState({ name: '', industry: '', logo_url: '', support_email: '' });
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState('');
  const [addSuccess, setAddSuccess] = useState('');

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
    setAddSuccess('');
    try {
      await brandService.createBrand({
        name: addBrand.name,
        industry: addBrand.industry,
        logo_url: addBrand.logo_url,
        support_email: addBrand.support_email
      });
      setShowAddModal(false);
      setAddBrand({ name: '', industry: '', logo_url: '', support_email: '' });
      setAddSuccess(`Brand "${addBrand.name}" created successfully!`);
      // Refresh the dashboard data to show the new brand
      fetchAllData();
    } catch (err) {
      console.error('Brand creation error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save brand. Please try again.';
      setAddError(`Failed to save brand. Details: ${errorMessage}`);
    } finally {
      setAddLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="page-container">
          <div className="page-header">
            <h1 className="page-title">
              <i className="fas fa-tachometer-alt me-2"></i>
              Admin Dashboard
            </h1>
          </div>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="page-container">
          <div className="page-header">
            <h1 className="page-title">
              <i className="fas fa-tachometer-alt me-2"></i>
              Admin Dashboard
            </h1>
          </div>
          <div className="alert alert-danger">
            <i className="fas fa-exclamation-triangle me-2"></i>
            <h5>Error Loading Dashboard</h5>
            <p>{error}</p>
            <div className="mt-3">
              <button 
                className="btn btn-primary me-2" 
                onClick={fetchAllData}
              >
                <i className="fas fa-redo me-2"></i>Retry
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => window.location.reload()}
              >
                <i className="fas fa-sync me-2"></i>Reload Page
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const resolutionRate = stats.tickets > 0 ? ((stats.resolved / stats.tickets) * 100).toFixed(1) : 0;

  return (
    <div className="admin-dashboard">
              {/* Dashboard Header */}
        <div className="page-container">
          {addSuccess && (
            <div className="alert alert-success alert-dismissible fade show mb-3">
              <i className="fas fa-check-circle me-2"></i>
              {addSuccess}
              <button type="button" className="btn-close" onClick={() => setAddSuccess('')}></button>
            </div>
          )}
          <div className="page-header d-flex justify-content-between align-items-center">
          <div>
            <h1 className="page-title">
              <i className="fas fa-tachometer-alt me-2"></i>
              Admin Dashboard
            </h1>
            <p className="page-subtitle">System overview and management controls</p>
          </div>
          <div className="d-flex gap-2">
            <button 
              className="btn btn-outline-primary" 
              onClick={fetchAllData}
              disabled={loading}
            >
              <i className="fas fa-redo me-2"></i>
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </button>
            <button className="btn btn-success" onClick={() => setShowAddModal(true)}>
              <i className="fas fa-plus me-2"></i>Add Brand
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid mb-4">
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-users"></i>
              </div>
              <h2 className="stat-number">{stats.users}</h2>
              <p className="stat-label">Total Users</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-building"></i>
              </div>
              <h2 className="stat-number">{stats.brands}</h2>
              <p className="stat-label">Total Brands</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-ticket-alt"></i>
              </div>
              <h2 className="stat-number">{stats.tickets}</h2>
              <p className="stat-label">Total Complaints</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <h2 className="stat-number">{resolutionRate}%</h2>
              <p className="stat-label">Resolution Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Reports and Management Section */}
      <div className="page-container">
        <div className="row g-4">
          <div className="col-lg-8">
            <div className="card h-100">
              <div className="card-header">
                <h4>
                  <i className="fas fa-chart-bar me-2"></i>
                  System Reports
                </h4>
              </div>
              <div className="card-body">
                <p className="text-muted">Chart visualizations will be displayed here.</p>
                <div className="chart-placeholder">
                  <i className="fas fa-chart-area fa-3x text-muted mb-3"></i>
                  <p>Complaints per Day (Chart)</p>
                </div>
              </div>
            </div>
          </div>
          <div className="col-lg-4">
            <div className="card h-100">
              <div className="card-header">
                <h4>
                  <i className="fas fa-cogs me-2"></i>
                  Management
                </h4>
              </div>
              <div className="card-body p-0">
                <div className="list-group list-group-flush">
                  <Link to="/admin/brands" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-building me-3"></i>
                    Manage Brands
                  </Link>
                  <Link to="/admin/users" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-users me-3"></i>
                    Manage Users
                  </Link>
                  <Link to="/admin/complaints" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-ticket-alt me-3"></i>
                    Manage Complaints
                  </Link>
                  <Link to="/admin/brands-analytics" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-chart-pie me-3"></i>
                    Brands Analytics
                  </Link>
                  <Link to="/admin/reports" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-file-alt me-3"></i>
                    System Reports
                  </Link>
                  <Link to="/admin/settings" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-cog me-3"></i>
                    System Settings
                  </Link>
                  <Link to="/admin/billing" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-credit-card me-3"></i>
                    Billing Logs
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Brand Modal */}
      {showAddModal && (
        <Modal onClose={() => setShowAddModal(false)}>
          <div className="modal-header">
            <h5 className="modal-title">Add New Brand</h5>
            <button type="button" className="btn-close" onClick={() => setShowAddModal(false)}></button>
          </div>
          <form onSubmit={handleAdd}>
            <div className="modal-body">
              {addError && (
                <div className="alert alert-danger">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {addError}
                </div>
              )}
              {addSuccess && (
                <div className="alert alert-success">
                  <i className="fas fa-check-circle me-2"></i>
                  {addSuccess}
                </div>
              )}
              <div className="form-group">
                <label className="form-label">Brand Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={addBrand.name}
                  onChange={(e) => setAddBrand({...addBrand, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Industry</label>
                <input
                  type="text"
                  className="form-control"
                  value={addBrand.industry}
                  onChange={(e) => setAddBrand({...addBrand, industry: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Logo URL</label>
                <input
                  type="url"
                  className="form-control"
                  value={addBrand.logo_url}
                  onChange={(e) => setAddBrand({...addBrand, logo_url: e.target.value})}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Support Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={addBrand.support_email}
                  onChange={(e) => setAddBrand({...addBrand, support_email: e.target.value})}
                  required
                />
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={addLoading}>
                {addLoading ? (
                  <>
                    <i className="fas fa-spinner fa-spin me-2"></i>
                    Adding...
                  </>
                ) : (
                  <>
                    <i className="fas fa-plus me-2"></i>
                    Add Brand
                  </>
                )}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default AdminDashboard;
