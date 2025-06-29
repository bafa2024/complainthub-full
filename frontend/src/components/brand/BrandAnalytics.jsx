import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './BrandAnalytics.css';

export default function BrandAnalytics() {
  const [dateRange, setDateRange] = useState('7d');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-01-31');
  const [loading, setLoading] = useState(false);

  // Mock analytics data
  const [analyticsData, setAnalyticsData] = useState({
    totalComplaints: 1247,
    resolvedComplaints: 1189,
    pendingComplaints: 58,
    avgResponseTime: '2.3h',
    satisfactionScore: 4.2,
    complaintsThisWeek: 89,
    complaintsLastWeek: 76,
    responseTimeTrend: '+12%',
    satisfactionTrend: '+5%'
  });

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    // In a real app, this would fetch new data based on the date range
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  const handleExport = (type) => {
    // Mock export functionality
    console.log(`Exporting ${type} data...`);
    alert(`${type} data exported successfully!`);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return '#27ae60';
      case 'pending': return '#f39c12';
      case 'urgent': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="brand-analytics">
      {/* Header */}
      <header className="analytics-header">
        <div className="header-container">
          <div className="brand-info">
            <div className="brand-logo">Analytics Dashboard</div>
            <div className="user-info">
              <span>Welcome back, Admin</span>
              <Link to="/brand/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <div className="nav-container">
          <button className="nav-tab active">Overview</button>
          <button className="nav-tab">Complaints</button>
          <button className="nav-tab">Performance</button>
          <button className="nav-tab">Trends</button>
        </div>
      </nav>

      <div className="main-content">
        {/* Analytics Header */}
        <div className="analytics-header">
          <div className="date-range-selector">
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
          <div className="export-buttons">
            <button className="btn btn-secondary" onClick={() => handleExport('PDF')}>
              Export PDF
            </button>
            <button className="btn btn-secondary" onClick={() => handleExport('CSV')}>
              Export CSV
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Total Complaints</span>
              <span className="stat-icon">📊</span>
            </div>
            <div className="stat-value">{analyticsData.totalComplaints}</div>
            <div className="stat-change positive">
              +{analyticsData.complaintsThisWeek} this week
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Resolved</span>
              <span className="stat-icon">✅</span>
            </div>
            <div className="stat-value">{analyticsData.resolvedComplaints}</div>
            <div className="stat-change positive">
              {((analyticsData.resolvedComplaints / analyticsData.totalComplaints) * 100).toFixed(1)}% resolution rate
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Pending</span>
              <span className="stat-icon">⏳</span>
            </div>
            <div className="stat-value">{analyticsData.pendingComplaints}</div>
            <div className="stat-change neutral">
              {analyticsData.pendingComplaints} open tickets
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Avg Response Time</span>
              <span className="stat-icon">⏱️</span>
            </div>
            <div className="stat-value">{analyticsData.avgResponseTime}</div>
            <div className="stat-change positive">
              {analyticsData.responseTimeTrend} vs last period
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Satisfaction Score</span>
              <span className="stat-icon">⭐</span>
            </div>
            <div className="stat-value">{analyticsData.satisfactionScore}/5</div>
            <div className="stat-change positive">
              {analyticsData.satisfactionTrend} vs last period
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-header">
              <span className="stat-title">Weekly Growth</span>
              <span className="stat-icon">📈</span>
            </div>
            <div className="stat-value">
              {((analyticsData.complaintsThisWeek - analyticsData.complaintsLastWeek) / analyticsData.complaintsLastWeek * 100).toFixed(1)}%
            </div>
            <div className="stat-change positive">
              {analyticsData.complaintsThisWeek} vs {analyticsData.complaintsLastWeek} last week
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="charts-section">
          <div className="chart-container">
            <h3>Complaints Over Time</h3>
            <div className="chart-placeholder">
              <div className="chart-bars">
                {[65, 78, 90, 85, 92, 88, 95].map((height, index) => (
                  <div 
                    key={index} 
                    className="chart-bar" 
                    style={{ height: `${height}%` }}
                  >
                    <span className="bar-value">{height}</span>
                  </div>
                ))}
              </div>
              <div className="chart-labels">
                <span>Mon</span>
                <span>Tue</span>
                <span>Wed</span>
                <span>Thu</span>
                <span>Fri</span>
                <span>Sat</span>
                <span>Sun</span>
              </div>
            </div>
          </div>

          <div className="chart-container">
            <h3>Complaint Categories</h3>
            <div className="pie-chart-placeholder">
              <div className="pie-segments">
                <div className="pie-segment" style={{ 
                  background: `conic-gradient(#3498db 0deg 120deg, #e74c3c 120deg 200deg, #f39c12 200deg 280deg, #27ae60 280deg 360deg)` 
                }}></div>
              </div>
              <div className="pie-legend">
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#3498db' }}></span>
                  <span>Technical Issues (33%)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#e74c3c' }}></span>
                  <span>Billing (22%)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#f39c12' }}></span>
                  <span>Service Quality (22%)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color" style={{ background: '#27ae60' }}></span>
                  <span>Other (23%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="recent-activity">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon resolved">✅</div>
              <div className="activity-content">
                <div className="activity-title">Complaint #1247 resolved</div>
                <div className="activity-details">Technical issue with mobile app - resolved in 1.5 hours</div>
                <div className="activity-time">2 hours ago</div>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon new">📝</div>
              <div className="activity-content">
                <div className="activity-title">New complaint received</div>
                <div className="activity-details">Billing dispute from customer #45678</div>
                <div className="activity-time">4 hours ago</div>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon urgent">🚨</div>
              <div className="activity-content">
                <div className="activity-title">Urgent complaint escalated</div>
                <div className="activity-details">Service outage affecting multiple customers</div>
                <div className="activity-time">6 hours ago</div>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon resolved">✅</div>
              <div className="activity-content">
                <div className="activity-title">Complaint #1245 resolved</div>
                <div className="activity-details">Account access issue - resolved in 45 minutes</div>
                <div className="activity-time">8 hours ago</div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="performance-metrics">
          <h3>Performance Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <h4>Response Time</h4>
              <div className="metric-value">{analyticsData.avgResponseTime}</div>
              <div className="metric-target">Target: &lt; 4 hours</div>
              <div className="metric-status good">On Target</div>
            </div>

            <div className="metric-card">
              <h4>Resolution Rate</h4>
              <div className="metric-value">
                {((analyticsData.resolvedComplaints / analyticsData.totalComplaints) * 100).toFixed(1)}%
              </div>
              <div className="metric-target">Target: &gt; 90%</div>
              <div className="metric-status good">Exceeding Target</div>
            </div>

            <div className="metric-card">
              <h4>Customer Satisfaction</h4>
              <div className="metric-value">{analyticsData.satisfactionScore}/5</div>
              <div className="metric-target">Target: &gt; 4.0</div>
              <div className="metric-status good">On Target</div>
            </div>

            <div className="metric-card">
              <h4>First Contact Resolution</h4>
              <div className="metric-value">78%</div>
              <div className="metric-target">Target: &gt; 75%</div>
              <div className="metric-status good">On Target</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
