import React, { useState, useEffect } from 'react';
import LoadingSpinner from '../shared/LoadingSpinner';
import adminService from '../../services/adminService';
import './AdminReports.css';

export default function AdminReports() {
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeReportType, setActiveReportType] = useState('overview');
  const [dateRange, setDateRange] = useState('30d');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-01-31');

  // Mock reports data
  const mockReports = {
    overview: {
      totalComplaints: 1247,
      resolvedComplaints: 1189,
      pendingComplaints: 58,
      avgResolutionTime: '2.3h',
      satisfactionScore: 4.2,
      totalBrands: 156,
      totalUsers: 2847,
      revenue: 45600
    },
    complaints: {
      byStatus: [
        { status: 'Resolved', count: 1189, percentage: 95.3 },
        { status: 'In Progress', count: 45, percentage: 3.6 },
        { status: 'Pending', count: 13, percentage: 1.1 }
      ],
      byCategory: [
        { category: 'Technical Issues', count: 456, percentage: 36.6 },
        { category: 'Billing', count: 234, percentage: 18.8 },
        { category: 'Service Quality', count: 198, percentage: 15.9 },
        { category: 'Product Issues', count: 156, percentage: 12.5 },
        { category: 'Other', count: 203, percentage: 16.2 }
      ],
      byBrand: [
        { brand: 'TechCorp Solutions', count: 89, avgResolution: '1.8h' },
        { brand: 'Global Retail', count: 67, avgResolution: '2.1h' },
        { brand: 'Digital Services', count: 54, avgResolution: '2.5h' },
        { brand: 'Mobile Telecom', count: 43, avgResolution: '3.2h' },
        { brand: 'Cloud Computing', count: 38, avgResolution: '1.9h' }
      ]
    },
    performance: {
      responseTime: {
        average: '2.3h',
        target: '4h',
        trend: '+12%'
      },
      resolutionRate: {
        current: '95.3%',
        target: '90%',
        trend: '+2.1%'
      },
      satisfaction: {
        current: '4.2/5',
        target: '4.0/5',
        trend: '+0.3'
      }
    },
    financial: {
      monthlyRevenue: 45600,
      monthlyGrowth: '+15%',
      topRevenueBrands: [
        { brand: 'TechCorp Solutions', revenue: 8900, complaints: 89 },
        { brand: 'Global Retail', revenue: 6700, complaints: 67 },
        { brand: 'Digital Services', revenue: 5400, complaints: 54 },
        { brand: 'Mobile Telecom', revenue: 4300, complaints: 43 },
        { brand: 'Cloud Computing', revenue: 3800, complaints: 38 }
      ]
    }
  };

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        // Simulate API call
        setTimeout(() => {
          setReports(mockReports);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    // In a real app, this would fetch new data based on the date range
  };

  const handleExport = (type) => {
    console.log(`Exporting ${type} report...`);
    alert(`${type} report exported successfully!`);
  };

  if (loading) return <LoadingSpinner />;

  if (!reports) {
    return (
      <div className="admin-reports">
        <div className="no-reports">
          <h3>No reports available</h3>
          <p>Reports will be generated once there is sufficient data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-reports">
      {/* Page Header */}
      <div className="page-header">
        <h1>System Reports</h1>
        <div className="export-buttons">
          <button className="btn btn-secondary" onClick={() => handleExport('PDF')}>
            Export PDF
          </button>
          <button className="btn btn-secondary" onClick={() => handleExport('CSV')}>
            Export CSV
          </button>
        </div>
      </div>

      {/* Report Type Tabs */}
      <div className="report-tabs">
        <button 
          className={`report-tab ${activeReportType === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveReportType('overview')}
        >
          Overview
        </button>
        <button 
          className={`report-tab ${activeReportType === 'complaints' ? 'active' : ''}`}
          onClick={() => setActiveReportType('complaints')}
        >
          Complaints
        </button>
        <button 
          className={`report-tab ${activeReportType === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveReportType('performance')}
        >
          Performance
        </button>
        <button 
          className={`report-tab ${activeReportType === 'financial' ? 'active' : ''}`}
          onClick={() => setActiveReportType('financial')}
        >
          Financial
        </button>
      </div>

      {/* Date Range Selector */}
      <div className="date-range-section">
        <div className="date-inputs">
          <label>Date Range:</label>
          <select 
            value={dateRange} 
            onChange={(e) => handleDateRangeChange(e.target.value)}
            className="date-input"
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
                className="date-input"
              />
              <span>to</span>
              <input 
                type="date" 
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="date-input"
              />
            </>
          )}
        </div>
        <div className="quick-ranges">
          <button className="quick-range">Today</button>
          <button className="quick-range">Yesterday</button>
          <button className="quick-range">This Week</button>
          <button className="quick-range">This Month</button>
        </div>
      </div>

      {/* Overview Report */}
      {activeReportType === 'overview' && (
        <div className="report-content">
          <div className="summary-grid">
            <div className="summary-card">
              <div className="summary-value">{reports.overview.totalComplaints}</div>
              <div className="summary-label">Total Complaints</div>
              <div className="summary-change positive">+12% vs last period</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.resolvedComplaints}</div>
              <div className="summary-label">Resolved</div>
              <div className="summary-change positive">95.3% resolution rate</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.pendingComplaints}</div>
              <div className="summary-label">Pending</div>
              <div className="summary-change neutral">4.7% pending</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.avgResolutionTime}</div>
              <div className="summary-label">Avg Resolution Time</div>
              <div className="summary-change positive">+12% improvement</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.satisfactionScore}/5</div>
              <div className="summary-label">Satisfaction Score</div>
              <div className="summary-change positive">+0.3 vs last period</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.totalBrands}</div>
              <div className="summary-label">Active Brands</div>
              <div className="summary-change positive">+8 new this month</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">{reports.overview.totalUsers}</div>
              <div className="summary-label">Total Users</div>
              <div className="summary-change positive">+156 new users</div>
            </div>
            <div className="summary-card">
              <div className="summary-value">${reports.overview.revenue.toLocaleString()}</div>
              <div className="summary-label">Monthly Revenue</div>
              <div className="summary-change positive">+15% vs last month</div>
            </div>
          </div>
        </div>
      )}

      {/* Complaints Report */}
      {activeReportType === 'complaints' && (
        <div className="report-content">
          <div className="report-grid">
            <div className="report-card">
              <h3>Complaints by Status</h3>
              <div className="status-chart">
                {reports.complaints.byStatus.map((item, index) => (
                  <div key={index} className="status-item">
                    <div className="status-info">
                      <span className="status-name">{item.status}</span>
                      <span className="status-count">{item.count}</span>
                    </div>
                    <div className="status-bar">
                      <div 
                        className="status-fill" 
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <span className="status-percentage">{item.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="report-card">
              <h3>Complaints by Category</h3>
              <div className="category-list">
                {reports.complaints.byCategory.map((item, index) => (
                  <div key={index} className="category-item">
                    <div className="category-info">
                      <span className="category-name">{item.category}</span>
                      <span className="category-count">{item.count}</span>
                    </div>
                    <div className="category-bar">
                      <div 
                        className="category-fill" 
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <span className="category-percentage">{item.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="report-card full-width">
              <h3>Top Brands by Complaint Volume</h3>
              <div className="brands-table">
                <table>
                  <thead>
                    <tr>
                      <th>Brand</th>
                      <th>Complaints</th>
                      <th>Avg Resolution Time</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.complaints.byBrand.map((brand, index) => (
                      <tr key={index}>
                        <td>{brand.brand}</td>
                        <td>{brand.count}</td>
                        <td>{brand.avgResolution}</td>
                        <td>
                          <span className="status-badge good">Good</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Report */}
      {activeReportType === 'performance' && (
        <div className="report-content">
          <div className="performance-grid">
            <div className="performance-card">
              <h3>Response Time</h3>
              <div className="metric-display">
                <div className="metric-value">{reports.performance.responseTime.average}</div>
                <div className="metric-target">Target: {reports.performance.responseTime.target}</div>
                <div className="metric-trend positive">{reports.performance.responseTime.trend}</div>
              </div>
            </div>

            <div className="performance-card">
              <h3>Resolution Rate</h3>
              <div className="metric-display">
                <div className="metric-value">{reports.performance.resolutionRate.current}</div>
                <div className="metric-target">Target: {reports.performance.resolutionRate.target}</div>
                <div className="metric-trend positive">{reports.performance.resolutionRate.trend}</div>
              </div>
            </div>

            <div className="performance-card">
              <h3>Customer Satisfaction</h3>
              <div className="metric-display">
                <div className="metric-value">{reports.performance.satisfaction.current}</div>
                <div className="metric-target">Target: {reports.performance.satisfaction.target}</div>
                <div className="metric-trend positive">{reports.performance.satisfaction.trend}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Financial Report */}
      {activeReportType === 'financial' && (
        <div className="report-content">
          <div className="financial-summary">
            <div className="financial-card">
              <h3>Monthly Revenue</h3>
              <div className="financial-value">${reports.financial.monthlyRevenue.toLocaleString()}</div>
              <div className="financial-growth positive">{reports.financial.monthlyGrowth}</div>
            </div>
          </div>

          <div className="report-card">
            <h3>Top Revenue Generating Brands</h3>
            <div className="revenue-table">
              <table>
                <thead>
                  <tr>
                    <th>Brand</th>
                    <th>Revenue</th>
                    <th>Complaints</th>
                    <th>Revenue per Complaint</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.financial.topRevenueBrands.map((brand, index) => (
                    <tr key={index}>
                      <td>{brand.brand}</td>
                      <td>${brand.revenue.toLocaleString()}</td>
                      <td>{brand.complaints}</td>
                      <td>${(brand.revenue / brand.complaints).toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}