import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import brandService from '../../services/brandService';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminBrandsAnalytics = () => {
  const [brands, setBrands] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('all');
  const [dateRange, setDateRange] = useState('30'); // days

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch brands and tickets concurrently
      const [brandsData, ticketsData] = await Promise.all([
        brandService.getBrands(),
        ticketService.getTickets()
      ]);

      setBrands(brandsData);
      setTickets(ticketsData);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  // Calculate analytics for all brands
  const calculateBrandAnalytics = () => {
    const analytics = brands.map(brand => {
      const brandTickets = tickets.filter(ticket => ticket.brand_id === brand.id);
      const totalTickets = brandTickets.length;
      
      const statusCounts = {
        new: brandTickets.filter(t => t.status === 'new').length,
        'in-progress': brandTickets.filter(t => t.status === 'in-progress').length,
        resolved: brandTickets.filter(t => t.status === 'resolved').length,
        closed: brandTickets.filter(t => t.status === 'closed').length
      };

      const resolvedTickets = statusCounts.resolved;
      const resolutionRate = totalTickets > 0 ? ((resolvedTickets / totalTickets) * 100).toFixed(1) : 0;

      // Calculate average resolution time (mock data for now)
      const avgResolutionTime = totalTickets > 0 ? Math.floor(Math.random() * 7) + 1 : 0;

      return {
        ...brand,
        totalTickets,
        statusCounts,
        resolutionRate,
        avgResolutionTime
      };
    });

    return analytics;
  };

  // Calculate overall statistics
  const calculateOverallStats = () => {
    const totalBrands = brands.length;
    const totalTickets = tickets.length;
    const totalResolved = tickets.filter(t => t.status === 'resolved').length;
    const totalNew = tickets.filter(t => t.status === 'new').length;
    const totalInProgress = tickets.filter(t => t.status === 'in-progress').length;

    return {
      totalBrands,
      totalTickets,
      totalResolved,
      totalNew,
      totalInProgress,
      overallResolutionRate: totalTickets > 0 ? ((totalResolved / totalTickets) * 100).toFixed(1) : 0
    };
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'new': return 'badge-primary';
      case 'in-progress': return 'badge-warning';
      case 'resolved': return 'badge-success';
      case 'closed': return 'badge-secondary';
      default: return 'badge-light';
    }
  };

  if (loading) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Brand Analytics</h1>
        <LoadingSpinner />
      </div>
    );
  }

  const brandAnalytics = calculateBrandAnalytics();
  const overallStats = calculateOverallStats();

  return (
    <div className="admin-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Brand Analytics</h1>
        <button 
          className="btn btn-outline-primary btn-sm" 
          onClick={fetchData}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Data'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger mb-4">
          <h5>Error Loading Analytics</h5>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchData}>Retry</button>
        </div>
      )}

      {/* Overall Statistics */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h3 className="card-title text-primary">{overallStats.totalBrands}</h3>
              <p className="card-text">Total Brands</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h3 className="card-title text-info">{overallStats.totalTickets}</h3>
              <p className="card-text">Total Complaints</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h3 className="card-title text-success">{overallStats.totalResolved}</h3>
              <p className="card-text">Resolved</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card text-center">
            <div className="card-body">
              <h3 className="card-title text-warning">{overallStats.overallResolutionRate}%</h3>
              <p className="card-text">Resolution Rate</p>
            </div>
          </div>
        </div>
      </div>

      {/* Current Status Overview */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>Current Status Overview</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <div className="d-flex align-items-center">
                <span className={`badge ${getStatusBadgeClass('new')} me-2`}>
                  {overallStats.totalNew}
                </span>
                <span>New Complaints</span>
              </div>
            </div>
            <div className="col-md-3">
              <div className="d-flex align-items-center">
                <span className={`badge ${getStatusBadgeClass('in-progress')} me-2`}>
                  {overallStats.totalInProgress}
                </span>
                <span>In Progress</span>
              </div>
            </div>
            <div className="col-md-3">
              <div className="d-flex align-items-center">
                <span className={`badge ${getStatusBadgeClass('resolved')} me-2`}>
                  {overallStats.totalResolved}
                </span>
                <span>Resolved</span>
              </div>
            </div>
            <div className="col-md-3">
              <div className="d-flex align-items-center">
                <span className={`badge ${getStatusBadgeClass('closed')} me-2`}>
                  {overallStats.totalTickets - overallStats.totalNew - overallStats.totalInProgress - overallStats.totalResolved}
                </span>
                <span>Closed</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Brand Analytics Table */}
      <div className="card">
        <div className="card-header">
          <h5>Brand Performance Analytics</h5>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Brand</th>
                  <th>Total Complaints</th>
                  <th>New</th>
                  <th>In Progress</th>
                  <th>Resolved</th>
                  <th>Resolution Rate</th>
                  <th>Avg Resolution (Days)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {brandAnalytics.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="text-center text-muted py-4">
                      No brands found
                    </td>
                  </tr>
                ) : (
                  brandAnalytics.map(brand => (
                    <tr key={brand.id}>
                      <td>
                        <div className="fw-bold">{brand.name}</div>
                        <small className="text-muted">{brand.email}</small>
                      </td>
                      <td>
                        <span className="badge bg-info fs-6">{brand.totalTickets}</span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass('new')}`}>
                          {brand.statusCounts.new}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass('in-progress')}`}>
                          {brand.statusCounts['in-progress']}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass('resolved')}`}>
                          {brand.statusCounts.resolved}
                        </span>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <span className="fw-bold me-2">{brand.resolutionRate}%</span>
                          <div className="progress flex-grow-1" style={{ height: '8px' }}>
                            <div 
                              className="progress-bar bg-success" 
                              style={{ width: `${brand.resolutionRate}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="text-muted">{brand.avgResolutionTime} days</span>
                      </td>
                      <td>
                        <Link 
                          to={`/admin/brands`} 
                          className="btn btn-sm btn-outline-primary me-1"
                        >
                          View Brand
                        </Link>
                        <Link 
                          to={`/admin/complaints?brand=${brand.id}`} 
                          className="btn btn-sm btn-outline-secondary"
                        >
                          View Complaints
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-4">
        <div className="d-flex gap-2">
          <Link to="/admin/brands" className="btn btn-primary">
            Manage Brands
          </Link>
          <Link to="/admin/complaints" className="btn btn-outline-primary">
            View All Complaints
          </Link>
          <Link to="/admin/reports" className="btn btn-outline-secondary">
            Generate Reports
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminBrandsAnalytics; 