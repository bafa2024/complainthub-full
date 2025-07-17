import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';
import './AdminReports.css';

export default function AdminReports() {
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [activeReportType, setActiveReportType] = useState('overview');
  const [dateRange, setDateRange] = useState('30d');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-01-31');
  const [exportFormat, setExportFormat] = useState('pdf');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadReports();
  }, [dateRange, startDate, endDate]);

  const loadReports = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [overviewData, complaintsData, brandsData, usersData, revenueData] = await Promise.all([
        adminService.getAnalyticsOverview(dateRange),
        adminService.getComplaintsReport({ startDate, endDate }),
        adminService.getBrandsReport({ startDate, endDate }),
        adminService.getUsersReport({ startDate, endDate }),
        adminService.getRevenueReport({ startDate, endDate })
      ]);

      setReports({
        overview: overviewData.overview,
        complaints: complaintsData,
        brands: brandsData,
        users: usersData,
        revenue: revenueData
      });
    } catch (err) {
      console.error('Error loading reports:', err);
      setError('Failed to load reports: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async (type) => {
    try {
      setGenerating(true);
      setError('');
      setSuccess('');

      const filters = {
        dateRange,
        startDate,
        endDate,
        reportType: type
      };

      const result = await adminService.generateReport(type, exportFormat, filters);
      
      if (result.success) {
        // Handle file download
        if (result.data) {
          const blob = new Blob([result.data], { 
            type: exportFormat === 'pdf' ? 'application/pdf' : 'text/csv' 
          });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `admin-${type}-report-${new Date().toISOString().split('T')[0]}.${exportFormat}`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        }
        setSuccess(`${type} report generated and downloaded successfully!`);
      } else {
        setError(`Failed to generate ${type} report: ${result.error}`);
      }
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report: ' + (err.message || 'Unknown error'));
    } finally {
      setGenerating(false);
    }
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    // Update start and end dates based on range
    const end = new Date();
    let start = new Date();
    
    switch (range) {
      case '7d':
        start.setDate(end.getDate() - 7);
        break;
      case '30d':
        start.setDate(end.getDate() - 30);
        break;
      case '90d':
        start.setDate(end.getDate() - 90);
        break;
      case '1y':
        start.setFullYear(end.getFullYear() - 1);
        break;
      default:
        break;
    }
    
    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  };

  const handleTabChange = (tab) => {
    setActiveReportType(tab);
  };

  if (loading) {
    return (
      <div className="admin-reports">
        <div className="page-container">
          <div className="page-header">
            <h1 className="page-title">
              <i className="fas fa-file-alt me-2"></i>
              System Reports
            </h1>
          </div>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  return (
    <div className="admin-reports">
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">
            <i className="fas fa-file-alt me-2"></i>
            System Reports
          </h1>
          <p className="page-subtitle">Generate and export comprehensive system reports</p>
        </div>

        {error && (
          <div className="alert alert-danger alert-dismissible fade show mb-3">
            <i className="fas fa-exclamation-triangle me-2"></i>
            {error}
            <button type="button" className="btn-close" onClick={() => setError('')}></button>
          </div>
        )}

        {success && (
          <div className="alert alert-success alert-dismissible fade show mb-3">
            <i className="fas fa-check-circle me-2"></i>
            {success}
            <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
          </div>
        )}

        {/* Report Controls */}
        <div className="report-controls mb-4">
          <div className="card">
            <div className="card-body">
              <div className="row align-items-end">
                <div className="col-md-3">
                  <label className="form-label">Date Range</label>
                  <select 
                    value={dateRange} 
                    onChange={(e) => handleDateRangeChange(e.target.value)}
                    className="form-select"
                  >
                    <option value="7d">Last 7 days</option>
                    <option value="30d">Last 30 days</option>
                    <option value="90d">Last 90 days</option>
                    <option value="1y">Last year</option>
                    <option value="custom">Custom Range</option>
                  </select>
                </div>
                {dateRange === 'custom' && (
                  <>
                    <div className="col-md-2">
                      <label className="form-label">Start Date</label>
                      <input 
                        type="date" 
                        value={startDate} 
                        onChange={(e) => setStartDate(e.target.value)}
                        className="form-control"
                      />
                    </div>
                    <div className="col-md-2">
                      <label className="form-label">End Date</label>
                      <input 
                        type="date" 
                        value={endDate} 
                        onChange={(e) => setEndDate(e.target.value)}
                        className="form-control"
                      />
                    </div>
                  </>
                )}
                <div className="col-md-2">
                  <label className="form-label">Export Format</label>
                  <select 
                    value={exportFormat} 
                    onChange={(e) => setExportFormat(e.target.value)}
                    className="form-select"
                  >
                    <option value="pdf">PDF</option>
                    <option value="csv">CSV</option>
                    <option value="json">JSON</option>
                  </select>
                </div>
                <div className="col-md-3">
                  <button 
                    className="btn btn-primary w-100"
                    onClick={() => generateReport(activeReportType)}
                    disabled={generating}
                  >
                    {generating ? (
                      <>
                        <i className="fas fa-spinner fa-spin me-2"></i>
                        Generating...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-download me-2"></i>
                        Export Report
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Report Navigation */}
        <div className="report-nav mb-4">
          <button 
            className={`nav-btn ${activeReportType === 'overview' ? 'active' : ''}`}
            onClick={() => handleTabChange('overview')}
          >
            <i className="fas fa-chart-pie me-2"></i>
            Overview
          </button>
          <button 
            className={`nav-btn ${activeReportType === 'complaints' ? 'active' : ''}`}
            onClick={() => handleTabChange('complaints')}
          >
            <i className="fas fa-ticket-alt me-2"></i>
            Complaints
          </button>
          <button 
            className={`nav-btn ${activeReportType === 'brands' ? 'active' : ''}`}
            onClick={() => handleTabChange('brands')}
          >
            <i className="fas fa-building me-2"></i>
            Brands
          </button>
          <button 
            className={`nav-btn ${activeReportType === 'users' ? 'active' : ''}`}
            onClick={() => handleTabChange('users')}
          >
            <i className="fas fa-users me-2"></i>
            Users
          </button>
          <button 
            className={`nav-btn ${activeReportType === 'revenue' ? 'active' : ''}`}
            onClick={() => handleTabChange('revenue')}
          >
            <i className="fas fa-dollar-sign me-2"></i>
            Revenue
          </button>
          <button 
            className={`nav-btn ${activeReportType === 'health' ? 'active' : ''}`}
            onClick={() => handleTabChange('health')}
          >
            <i className="fas fa-heartbeat me-2"></i>
            System Health
          </button>
        </div>

        {/* Report Content */}
        <div className="report-content">
          {activeReportType === 'overview' && (
            <div className="overview-report">
              <div className="summary-grid">
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.total_tickets || 0}</div>
                  <div className="summary-label">Total Complaints</div>
                  <div className="summary-change positive">+12% vs last period</div>
                </div>
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.resolved_tickets || 0}</div>
                  <div className="summary-label">Resolved</div>
                  <div className="summary-change positive">95.3% resolution rate</div>
                </div>
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.active_tickets || 0}</div>
                  <div className="summary-label">Active</div>
                  <div className="summary-change neutral">4.7% pending</div>
                </div>
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.avg_resolution_time || 0}h</div>
                  <div className="summary-label">Avg Resolution Time</div>
                  <div className="summary-change positive">+12% improvement</div>
                </div>
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.avg_satisfaction || 0}/5</div>
                  <div className="summary-label">Satisfaction Score</div>
                  <div className="summary-change positive">+0.3 vs last period</div>
                </div>
                <div className="summary-card">
                  <div className="summary-value">{reports?.overview?.total_brands || 0}</div>
                  <div className="summary-label">Active Brands</div>
                  <div className="summary-change positive">+8 new this month</div>
                </div>
              </div>

              <div className="row mt-4">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Status Distribution</h5>
                    </div>
                    <div className="card-body">
                      <div className="status-distribution">
                        {reports?.overview?.status_breakdown && Object.entries(reports.overview.status_breakdown).map(([status, count]) => (
                          <div key={status} className="status-item">
                            <div className="status-label">{status}</div>
                            <div className="status-bar">
                              <div 
                                className="status-fill" 
                                style={{ 
                                  width: `${(count / reports.overview.total_tickets) * 100}%`,
                                  backgroundColor: status === 'resolved' ? '#28a745' : 
                                                 status === 'in-progress' ? '#ffc107' : '#dc3545'
                                }}
                              ></div>
                            </div>
                            <div className="status-count">{count}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Channel Distribution</h5>
                    </div>
                    <div className="card-body">
                      <div className="channel-distribution">
                        {reports?.overview?.channel_distribution && Object.entries(reports.overview.channel_distribution).map(([channel, count]) => (
                          <div key={channel} className="channel-item">
                            <div className="channel-icon">
                              {channel === 'whatsapp' && '📱'}
                              {channel === 'telegram' && '📬'}
                              {channel === 'webchat' && '💬'}
                              {channel === 'voice' && '🎤'}
                              {channel === 'email' && '📧'}
                            </div>
                            <div className="channel-info">
                              <span className="channel-name">{channel.charAt(0).toUpperCase() + channel.slice(1)}</span>
                              <span className="channel-count">{count}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeReportType === 'complaints' && (
            <div className="complaints-report">
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Complaints by Status</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-sm">
                          <thead>
                            <tr>
                              <th>Status</th>
                              <th>Count</th>
                              <th>Percentage</th>
                            </tr>
                          </thead>
                          <tbody>
                            {reports?.complaints?.byStatus?.map((item, index) => (
                              <tr key={index}>
                                <td>
                                  <span className={`badge ${item.status === 'Resolved' ? 'bg-success' : 
                                                          item.status === 'In Progress' ? 'bg-warning' : 'bg-danger'}`}>
                                    {item.status}
                                  </span>
                                </td>
                                <td>{item.count}</td>
                                <td>{item.percentage}%</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Complaints by Category</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table table-sm">
                          <thead>
                            <tr>
                              <th>Category</th>
                              <th>Count</th>
                              <th>Percentage</th>
                            </tr>
                          </thead>
                          <tbody>
                            {reports?.complaints?.byCategory?.map((item, index) => (
                              <tr key={index}>
                                <td>{item.category}</td>
                                <td>{item.count}</td>
                                <td>{item.percentage}%</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="row mt-4">
                <div className="col-12">
                  <div className="card">
                    <div className="card-header">
                      <h5>Top Brands by Complaint Volume</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table">
                          <thead>
                            <tr>
                              <th>Brand</th>
                              <th>Complaints</th>
                              <th>Avg Resolution Time</th>
                              <th>Resolution Rate</th>
                              <th>Satisfaction Score</th>
                            </tr>
                          </thead>
                          <tbody>
                            {reports?.complaints?.byBrand?.map((brand, index) => (
                              <tr key={index}>
                                <td>{brand.brand}</td>
                                <td>{brand.count}</td>
                                <td>{brand.avgResolution}</td>
                                <td>{brand.resolutionRate}%</td>
                                <td>{brand.satisfactionScore}/5</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeReportType === 'brands' && (
            <div className="brands-report">
              <div className="row">
                <div className="col-12">
                  <div className="card">
                    <div className="card-header">
                      <h5>Brand Performance Report</h5>
                    </div>
                    <div className="card-body">
                      <div className="table-responsive">
                        <table className="table">
                          <thead>
                            <tr>
                              <th>Brand Name</th>
                              <th>Industry</th>
                              <th>Total Complaints</th>
                              <th>Resolved</th>
                              <th>Resolution Rate</th>
                              <th>Avg Response Time</th>
                              <th>Satisfaction Score</th>
                              <th>Revenue</th>
                            </tr>
                          </thead>
                          <tbody>
                            {reports?.brands?.map((brand, index) => (
                              <tr key={index}>
                                <td>{brand.name}</td>
                                <td>{brand.industry}</td>
                                <td>{brand.totalComplaints}</td>
                                <td>{brand.resolved}</td>
                                <td>{brand.resolutionRate}%</td>
                                <td>{brand.avgResponseTime}h</td>
                                <td>{brand.satisfactionScore}/5</td>
                                <td>₹{brand.revenue}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeReportType === 'users' && (
            <div className="users-report">
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>User Registration Trends</h5>
                    </div>
                    <div className="card-body">
                      <div className="user-stats">
                        <div className="stat-item">
                          <div className="stat-value">{reports?.users?.totalUsers || 0}</div>
                          <div className="stat-label">Total Users</div>
                        </div>
                        <div className="stat-item">
                          <div className="stat-value">{reports?.users?.newUsers || 0}</div>
                          <div className="stat-label">New This Period</div>
                        </div>
                        <div className="stat-item">
                          <div className="stat-value">{reports?.users?.activeUsers || 0}</div>
                          <div className="stat-label">Active Users</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>User Activity</h5>
                    </div>
                    <div className="card-body">
                      <div className="activity-stats">
                        <div className="activity-item">
                          <span className="activity-label">Avg Complaints per User:</span>
                          <span className="activity-value">{reports?.users?.avgComplaintsPerUser || 0}</span>
                        </div>
                        <div className="activity-item">
                          <span className="activity-label">Most Active Users:</span>
                          <span className="activity-value">{reports?.users?.mostActiveUsers || 0}</span>
                        </div>
                        <div className="activity-item">
                          <span className="activity-label">User Satisfaction:</span>
                          <span className="activity-value">{reports?.users?.userSatisfaction || 0}/5</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeReportType === 'revenue' && (
            <div className="revenue-report">
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Revenue Overview</h5>
                    </div>
                    <div className="card-body">
                      <div className="revenue-stats">
                        <div className="revenue-item">
                          <div className="revenue-value">₹{reports?.revenue?.totalRevenue || 0}</div>
                          <div className="revenue-label">Total Revenue</div>
                        </div>
                        <div className="revenue-item">
                          <div className="revenue-value">₹{reports?.revenue?.monthlyRevenue || 0}</div>
                          <div className="revenue-label">Monthly Revenue</div>
                        </div>
                        <div className="revenue-item">
                          <div className="revenue-value">{reports?.revenue?.growthRate || 0}%</div>
                          <div className="revenue-label">Growth Rate</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Top Revenue Brands</h5>
                    </div>
                    <div className="card-body">
                      <div className="top-revenue-brands">
                        {reports?.revenue?.topBrands?.map((brand, index) => (
                          <div key={index} className="brand-revenue-item">
                            <div className="brand-name">{brand.name}</div>
                            <div className="brand-revenue">₹{brand.revenue}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeReportType === 'health' && (
            <div className="health-report">
              <div className="row">
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>System Health Metrics</h5>
                    </div>
                    <div className="card-body">
                      <div className="health-metrics">
                        <div className="health-item">
                          <span className="health-label">System Status:</span>
                          <span className="health-value status-healthy">Healthy</span>
                        </div>
                        <div className="health-item">
                          <span className="health-label">Uptime:</span>
                          <span className="health-value">99.9%</span>
                        </div>
                        <div className="health-item">
                          <span className="health-label">Error Rate:</span>
                          <span className="health-value">0.1%</span>
                        </div>
                        <div className="health-item">
                          <span className="health-label">Avg Response Time:</span>
                          <span className="health-value">150ms</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="card">
                    <div className="card-header">
                      <h5>Recent Issues</h5>
                    </div>
                    <div className="card-body">
                      <div className="issues-list">
                        <div className="issue-item">
                          <div className="issue-severity low">Low</div>
                          <div className="issue-details">
                            <div className="issue-title">Database connection timeout</div>
                            <div className="issue-time">2 hours ago</div>
                          </div>
                        </div>
                        <div className="issue-item">
                          <div className="issue-severity medium">Medium</div>
                          <div className="issue-details">
                            <div className="issue-title">API rate limit exceeded</div>
                            <div className="issue-time">1 day ago</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}