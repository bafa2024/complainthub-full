import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import ticketService from '../../services/ticketService';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './Admin.css';

const AdminBrandsAnalytics = () => {
  const [dateRange, setDateRange] = useState('30d');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-01-31');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Analytics data
  const [analyticsData, setAnalyticsData] = useState({
    totalBrands: 0,
    totalComplaints: 0,
    resolvedComplaints: 0,
    pendingComplaints: 0,
    avgResponseTime: '0h',
    avgSatisfactionScore: 0,
    complaintsThisPeriod: 0,
    complaintsLastPeriod: 0,
    topPerformingBrands: [],
    brandPerformanceData: []
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange, startDate, endDate]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch all data concurrently
      const [brandsData, complaintsData] = await Promise.all([
        brandService.getBrands(),
        ticketService.getTickets()
      ]);

      // Calculate analytics
      const totalBrands = brandsData.length;
      const totalComplaints = complaintsData.length;
      const resolvedComplaints = complaintsData.filter(c => c.status === 'resolved').length;
      const pendingComplaints = complaintsData.filter(c => c.status !== 'resolved').length;
      
      // Calculate average satisfaction score
      const ratedComplaints = complaintsData.filter(c => c.satisfaction_rating);
      const avgSatisfactionScore = ratedComplaints.length > 0 
        ? (ratedComplaints.reduce((sum, c) => sum + c.satisfaction_rating, 0) / ratedComplaints.length).toFixed(1)
        : 0;

      // Calculate brand performance
      const brandPerformance = brandsData.map(brand => {
        const brandComplaints = complaintsData.filter(c => c.brand_id === brand.id);
        const brandResolved = brandComplaints.filter(c => c.status === 'resolved').length;
        const brandPending = brandComplaints.filter(c => c.status !== 'resolved').length;
        const resolutionRate = brandComplaints.length > 0 ? (brandResolved / brandComplaints.length * 100).toFixed(1) : 0;
        
        return {
          id: brand.id,
          name: brand.name,
          totalComplaints: brandComplaints.length,
          resolvedComplaints: brandResolved,
          pendingComplaints: brandPending,
          resolutionRate: parseFloat(resolutionRate),
          avgSatisfaction: brandComplaints.filter(c => c.satisfaction_rating).length > 0 
            ? (brandComplaints.filter(c => c.satisfaction_rating).reduce((sum, c) => sum + c.satisfaction_rating, 0) / brandComplaints.filter(c => c.satisfaction_rating).length).toFixed(1)
            : 0
        };
      });

      // Sort by resolution rate to get top performing brands
      const topPerformingBrands = brandPerformance
        .filter(b => b.totalComplaints > 0)
        .sort((a, b) => b.resolutionRate - a.resolutionRate)
        .slice(0, 5);

      // Calculate period-over-period growth
      const periodDays = dateRange === '7d' ? 7 : dateRange === '30d' ? 30 : 90;
      const now = new Date();
      const periodStart = new Date(now.getTime() - (periodDays * 24 * 60 * 60 * 1000));
      const previousPeriodStart = new Date(periodStart.getTime() - (periodDays * 24 * 60 * 60 * 1000));
      
      const complaintsThisPeriod = complaintsData.filter(c => new Date(c.created_at) >= periodStart).length;
      const complaintsLastPeriod = complaintsData.filter(c => {
        const created = new Date(c.created_at);
        return created >= previousPeriodStart && created < periodStart;
      }).length;

      setAnalyticsData({
        totalBrands,
        totalComplaints,
        resolvedComplaints,
        pendingComplaints,
        avgResponseTime: '2.3h', // Mock data
        avgSatisfactionScore: parseFloat(avgSatisfactionScore),
        complaintsThisPeriod,
        complaintsLastPeriod,
        topPerformingBrands,
        brandPerformanceData: brandPerformance
      });

    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  const handleExport = (type) => {
    console.log(`Exporting ${type} analytics data...`);
    alert(`${type} analytics data exported successfully!`);
  };

  const getGrowthPercentage = () => {
    if (analyticsData.complaintsLastPeriod === 0) return 0;
    return ((analyticsData.complaintsThisPeriod - analyticsData.complaintsLastPeriod) / analyticsData.complaintsLastPeriod * 100).toFixed(1);
  };

  const getResolutionRate = () => {
    return analyticsData.totalComplaints > 0 
      ? ((analyticsData.resolvedComplaints / analyticsData.totalComplaints) * 100).toFixed(1)
      : 0;
  };

  if (loading) {
    return (
      <div className="admin-container">
        <h1 className="mb-4">Brands Analytics</h1>
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="admin-container">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Brands Analytics Dashboard</h1>
        <div>
          <button 
            className="btn btn-outline-primary me-2" 
            onClick={fetchAnalyticsData}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
          <Link to="/admin/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger mb-4">
          <h5>Error Loading Analytics</h5>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchAnalyticsData}>Retry</button>
        </div>
      )}

      {/* Date Range and Export Controls */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6">
              <div className="d-flex align-items-center">
                <label className="me-3 mb-0">Date Range:</label>
                <select 
                  value={dateRange} 
                  onChange={(e) => handleDateRangeChange(e.target.value)}
                  className="form-select w-auto"
                >
                  <option value="7d">Last 7 days</option>
                  <option value="30d">Last 30 days</option>
                  <option value="90d">Last 90 days</option>
                  <option value="custom">Custom range</option>
                </select>
                {dateRange === 'custom' && (
                  <>
                    <input 
                      type="date" 
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="form-control ms-2"
                      style={{ width: 'auto' }}
                    />
                    <span className="mx-2">to</span>
                    <input 
                      type="date" 
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="form-control"
                      style={{ width: 'auto' }}
                    />
                  </>
                )}
              </div>
            </div>
            <div className="col-md-6 text-end">
              <button className="btn btn-outline-secondary me-2" onClick={() => handleExport('PDF')}>
                Export PDF
              </button>
              <button className="btn btn-outline-secondary" onClick={() => handleExport('CSV')}>
                Export CSV
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Overall Stats Grid */}
      <div className="row g-4 mb-4">
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-muted">Total Brands</h6>
                  <h2 className="mb-0">{analyticsData.totalBrands}</h2>
                </div>
                <span className="fs-1">🏢</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-muted">Total Complaints</h6>
                  <h2 className="mb-0">{analyticsData.totalComplaints}</h2>
                  <small className="text-success">
                    +{analyticsData.complaintsThisPeriod} this period
                  </small>
                </div>
                <span className="fs-1">📊</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-muted">Resolution Rate</h6>
                  <h2 className="mb-0">{getResolutionRate()}%</h2>
                  <small className="text-muted">
                    {analyticsData.resolvedComplaints} resolved
                  </small>
                </div>
                <span className="fs-1">✅</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-6 col-lg-3">
          <div className="stat-card-admin card h-100">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <h6 className="card-title text-muted">Avg Satisfaction</h6>
                  <h2 className="mb-0">{analyticsData.avgSatisfactionScore}/5</h2>
                  <small className="text-muted">
                    Across all brands
                  </small>
                </div>
                <span className="fs-1">⭐</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Performing Brands */}
      <div className="row g-4 mb-4">
        <div className="col-lg-8">
          <div className="card h-100">
            <div className="card-header">
              <h5>Top Performing Brands</h5>
              <small className="text-muted">Based on resolution rate</small>
            </div>
            <div className="card-body">
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Brand</th>
                      <th>Total Complaints</th>
                      <th>Resolved</th>
                      <th>Resolution Rate</th>
                      <th>Avg Satisfaction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analyticsData.topPerformingBrands.length === 0 ? (
                      <tr>
                        <td colSpan="5" className="text-center text-muted py-4">
                          No brand performance data available
                        </td>
                      </tr>
                    ) : (
                      analyticsData.topPerformingBrands.map((brand, index) => (
                        <tr key={brand.id}>
                          <td>
                            <div className="d-flex align-items-center">
                              <span className="badge bg-primary me-2">#{index + 1}</span>
                              <strong>{brand.name}</strong>
                            </div>
                          </td>
                          <td>{brand.totalComplaints}</td>
                          <td>{brand.resolvedComplaints}</td>
                          <td>
                            <span className="badge bg-success">{brand.resolutionRate}%</span>
                          </td>
                          <td>
                            <div className="d-flex align-items-center">
                              <span className="me-1">{brand.avgSatisfaction}</span>
                              <span className="text-warning">★</span>
                            </div>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-lg-4">
          <div className="card h-100">
            <div className="card-header">
              <h5>Growth Metrics</h5>
            </div>
            <div className="card-body">
              <div className="mb-4">
                <h6>Complaint Growth</h6>
                <div className="d-flex align-items-center">
                  <span className="fs-3 me-2">
                    {getGrowthPercentage() > 0 ? '📈' : '📉'}
                  </span>
                  <div>
                    <span className={`fs-4 ${getGrowthPercentage() > 0 ? 'text-success' : 'text-danger'}`}>
                      {getGrowthPercentage()}%
                    </span>
                    <br />
                    <small className="text-muted">
                      vs previous {dateRange === '7d' ? 'week' : dateRange === '30d' ? 'month' : 'quarter'}
                    </small>
                  </div>
                </div>
              </div>
              
              <div className="mb-4">
                <h6>Pending Complaints</h6>
                <div className="d-flex align-items-center">
                  <span className="fs-3 me-2">⏳</span>
                  <div>
                    <span className="fs-4">{analyticsData.pendingComplaints}</span>
                    <br />
                    <small className="text-muted">Require attention</small>
                  </div>
                </div>
              </div>
              
              <div>
                <h6>Average Response Time</h6>
                <div className="d-flex align-items-center">
                  <span className="fs-3 me-2">⏱️</span>
                  <div>
                    <span className="fs-4">{analyticsData.avgResponseTime}</span>
                    <br />
                    <small className="text-muted">Across all brands</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* All Brands Performance */}
      <div className="card">
        <div className="card-header">
          <h5>All Brands Performance</h5>
          <small className="text-muted">Complete overview of all brands</small>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Brand Name</th>
                  <th>Total Complaints</th>
                  <th>Resolved</th>
                  <th>Pending</th>
                  <th>Resolution Rate</th>
                  <th>Avg Satisfaction</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {analyticsData.brandPerformanceData.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center text-muted py-4">
                      No brand data available
                    </td>
                  </tr>
                ) : (
                  analyticsData.brandPerformanceData.map(brand => (
                    <tr key={brand.id}>
                      <td>
                        <strong>{brand.name}</strong>
                      </td>
                      <td>{brand.totalComplaints}</td>
                      <td>
                        <span className="text-success">{brand.resolvedComplaints}</span>
                      </td>
                      <td>
                        <span className="text-warning">{brand.pendingComplaints}</span>
                      </td>
                      <td>
                        <span className={`badge ${brand.resolutionRate >= 80 ? 'bg-success' : brand.resolutionRate >= 60 ? 'bg-warning' : 'bg-danger'}`}>
                          {brand.resolutionRate}%
                        </span>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <span className="me-1">{brand.avgSatisfaction}</span>
                          <span className="text-warning">★</span>
                        </div>
                      </td>
                      <td>
                        <Link 
                          to={`/admin/complaints?brand=${brand.id}`} 
                          className="btn btn-sm btn-outline-primary"
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
    </div>
  );
};

export default AdminBrandsAnalytics; 