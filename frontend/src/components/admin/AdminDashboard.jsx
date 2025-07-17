import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import Modal from '../shared/Modal';
import brandService from '../../services/brandService';
import './Admin.css';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState({
    overview: {},
    realTime: {},
    recentActivity: [],
    systemHealth: {},
    topBrands: [],
    channelStats: {},
    revenueMetrics: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [addBrand, setAddBrand] = useState({ name: '', industry: '', logo_url: '', support_email: '' });
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState('');
  const [addSuccess, setAddSuccess] = useState('');
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [dateRange, setDateRange] = useState('30d');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Fetching admin dashboard data...');
      
      // Fetch comprehensive dashboard data
      const [dashboardRes, usersData, brandsData, ticketsData] = await Promise.all([
        adminService.getDashboardData(dateRange),
        adminService.getAllUsers(),
        adminService.getAllBrands(),
        ticketService.getTickets()
      ]);

      console.log('Dashboard data fetched:', dashboardRes);

      // Set dashboard data
      setDashboardData(dashboardRes);

    } catch (err) {
      console.error('Admin dashboard error:', err);
      setError('Failed to load dashboard data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const startRealTimeUpdates = () => {
    // Update real-time data every 30 seconds
    const interval = setInterval(async () => {
      try {
        const realTimeData = await adminService.getRealTimeMetrics();
        setDashboardData(prev => ({
          ...prev,
          realTime: realTimeData
        }));
      } catch (err) {
        console.error('Error updating real-time data:', err);
      }
    }, 30000);

    setRefreshInterval(interval);
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
      fetchDashboardData();
    } catch (err) {
      console.error('Brand creation error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to save brand. Please try again.';
      setAddError(`Failed to save brand. Details: ${errorMessage}`);
    } finally {
      setAddLoading(false);
    }
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  const handleExport = async (type) => {
    try {
      const result = await adminService.exportReport(type, 'csv', { dateRange });
      if (result.success) {
        // Create download link
        const blob = new Blob([result.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `admin-${type}-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Error exporting report:', err);
      setError('Failed to export report: ' + (err.message || 'Unknown error'));
    }
  };

  useEffect(() => {
    fetchDashboardData();
    startRealTimeUpdates();
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [dateRange]);

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
                onClick={fetchDashboardData}
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

  const overview = dashboardData.overview?.overview || {};
  const realTime = dashboardData.realTime || {};

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
            <div className="date-range-selector">
              <select 
                value={dateRange} 
                onChange={(e) => handleDateRangeChange(e.target.value)}
                className="form-select"
              >
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
                <option value="1y">Last year</option>
              </select>
            </div>
            <button 
              className="btn btn-outline-primary" 
              onClick={fetchDashboardData}
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

        {/* System Overview Stats */}
        <div className="stats-grid mb-4">
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-users"></i>
              </div>
              <h2 className="stat-number">{overview.total_users || 0}</h2>
              <p className="stat-label">Total Users</p>
              <div className="stat-trend positive">+12% this month</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-building"></i>
              </div>
              <h2 className="stat-number">{overview.total_brands || 0}</h2>
              <p className="stat-label">Total Brands</p>
              <div className="stat-trend positive">+5 new this month</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-ticket-alt"></i>
              </div>
              <h2 className="stat-number">{overview.total_tickets || 0}</h2>
              <p className="stat-label">Total Complaints</p>
              <div className="stat-trend positive">+8% vs last period</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <h2 className="stat-number">{overview.resolution_rate || 0}%</h2>
              <p className="stat-label">Resolution Rate</p>
              <div className="stat-trend positive">+2.1% improvement</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-clock"></i>
              </div>
              <h2 className="stat-number">{overview.avg_resolution_time || 0}h</h2>
              <p className="stat-label">Avg Resolution Time</p>
              <div className="stat-trend positive">-15% faster</div>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-dollar-sign"></i>
              </div>
              <h2 className="stat-number">₹{overview.total_revenue || 0}</h2>
              <p className="stat-label">Total Revenue</p>
              <div className="stat-trend positive">+18% growth</div>
            </div>
          </div>
        </div>

        {/* Real-time Metrics */}
        <div className="realtime-metrics mb-4">
          <div className="card">
            <div className="card-header">
              <h4>
                <i className="fas fa-broadcast-tower me-2"></i>
                Real-time Metrics
                <span className="pulse-indicator ms-2">
                  <span className="pulse"></span>
                  Live
                </span>
              </h4>
            </div>
            <div className="card-body">
              <div className="realtime-grid">
                <div className="realtime-item">
                  <div className="realtime-value">{realTime.today_tickets || 0}</div>
                  <div className="realtime-label">Tickets Today</div>
                </div>
                <div className="realtime-item">
                  <div className="realtime-value">{realTime.last_hour_tickets || 0}</div>
                  <div className="realtime-label">Last Hour</div>
                </div>
                <div className="realtime-item">
                  <div className="realtime-value">{realTime.active_conversations || 0}</div>
                  <div className="realtime-label">Active Conversations</div>
                </div>
                <div className="realtime-item">
                  <div className="realtime-value">{realTime.pending_tickets || 0}</div>
                  <div className="realtime-label">Pending Tickets</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Health and Reports */}
      <div className="page-container">
        <div className="row g-4">
          <div className="col-lg-8">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h4>
                  <i className="fas fa-chart-bar me-2"></i>
                  System Performance
                </h4>
                <div className="export-buttons">
                  <button className="btn btn-sm btn-outline-primary" onClick={() => handleExport('performance')}>
                    <i className="fas fa-download me-1"></i>Export
                  </button>
                </div>
              </div>
              <div className="card-body">
                <div className="performance-metrics">
                  <div className="metric-row">
                    <div className="metric-item">
                      <span className="metric-label">System Status:</span>
                      <span className={`metric-value status-${realTime.system_health?.status || 'unknown'}`}>
                        {realTime.system_health?.status || 'Unknown'}
                      </span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Error Rate:</span>
                      <span className="metric-value">{(realTime.system_health?.error_rate || 0) * 100}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Avg Response Time:</span>
                      <span className="metric-value">{realTime.system_health?.avg_response_time || 0}ms</span>
                    </div>
                  </div>
                  
                  <div className="chart-placeholder">
                    <i className="fas fa-chart-area fa-3x text-muted mb-3"></i>
                    <p>Complaints per Day (Chart)</p>
                    <small className="text-muted">Chart visualization will be implemented here</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-lg-4">
            <div className="card h-100">
              <div className="card-header">
                <h4>
                  <i className="fas fa-cogs me-2"></i>
                  Quick Actions
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
                  <Link to="/admin/analytics" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-chart-pie me-3"></i>
                    System Analytics
                  </Link>
                  <Link to="/admin/reports" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-file-alt me-3"></i>
                    Generate Reports
                  </Link>
                  <Link to="/admin/settings" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-cog me-3"></i>
                    System Settings
                  </Link>
                  <Link to="/admin/security" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-shield-alt me-3"></i>
                    Security & Monitoring
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity and Top Brands */}
        <div className="row g-4 mt-4">
          <div className="col-lg-6">
            <div className="card">
              <div className="card-header">
                <h4>
                  <i className="fas fa-history me-2"></i>
                  Recent Activity
                </h4>
              </div>
              <div className="card-body">
                <div className="activity-list">
                  {dashboardData.recentActivity?.slice(0, 5).map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-icon">
                        <i className={`fas ${activity.icon}`}></i>
                      </div>
                      <div className="activity-content">
                        <div className="activity-title">{activity.title}</div>
                        <div className="activity-time">{activity.time}</div>
                      </div>
                    </div>
                  )) || (
                    <div className="text-muted text-center py-3">
                      <i className="fas fa-info-circle me-2"></i>
                      No recent activity
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          <div className="col-lg-6">
            <div className="card">
              <div className="card-header">
                <h4>
                  <i className="fas fa-trophy me-2"></i>
                  Top Performing Brands
                </h4>
              </div>
              <div className="card-body">
                <div className="brands-list">
                  {dashboardData.topBrands?.slice(0, 5).map((brand, index) => (
                    <div key={index} className="brand-item">
                      <div className="brand-rank">#{index + 1}</div>
                      <div className="brand-info">
                        <div className="brand-name">{brand.name}</div>
                        <div className="brand-stats">
                          {brand.resolution_rate}% resolution rate • {brand.avg_response_time}h avg response
                        </div>
                      </div>
                    </div>
                  )) || (
                    <div className="text-muted text-center py-3">
                      <i className="fas fa-info-circle me-2"></i>
                      No brand data available
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add Brand Modal */}
      <Modal show={showAddModal} onClose={() => setShowAddModal(false)} title="Add New Brand">
        <form onSubmit={handleAdd}>
          {addError && (
            <div className="alert alert-danger">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {addError}
            </div>
          )}
          
          <div className="mb-3">
            <label htmlFor="brandName" className="form-label">Brand Name *</label>
            <input
              type="text"
              id="brandName"
              className="form-control"
              value={addBrand.name}
              onChange={(e) => setAddBrand({...addBrand, name: e.target.value})}
              required
            />
          </div>
          
          <div className="mb-3">
            <label htmlFor="brandIndustry" className="form-label">Industry</label>
            <select
              id="brandIndustry"
              className="form-select"
              value={addBrand.industry}
              onChange={(e) => setAddBrand({...addBrand, industry: e.target.value})}
            >
              <option value="">Select Industry</option>
              <option value="technology">Technology</option>
              <option value="retail">Retail</option>
              <option value="finance">Finance</option>
              <option value="healthcare">Healthcare</option>
              <option value="telecommunications">Telecommunications</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <div className="mb-3">
            <label htmlFor="brandLogo" className="form-label">Logo URL</label>
            <input
              type="url"
              id="brandLogo"
              className="form-control"
              value={addBrand.logo_url}
              onChange={(e) => setAddBrand({...addBrand, logo_url: e.target.value})}
              placeholder="https://example.com/logo.png"
            />
          </div>
          
          <div className="mb-3">
            <label htmlFor="brandEmail" className="form-label">Support Email</label>
            <input
              type="email"
              id="brandEmail"
              className="form-control"
              value={addBrand.support_email}
              onChange={(e) => setAddBrand({...addBrand, support_email: e.target.value})}
              placeholder="support@brand.com"
            />
          </div>
          
          <div className="d-flex gap-2">
            <button type="submit" className="btn btn-primary" disabled={addLoading}>
              {addLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin me-2"></i>
                  Creating...
                </>
              ) : (
                <>
                  <i className="fas fa-plus me-2"></i>
                  Create Brand
                </>
              )}
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default AdminDashboard;
