import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandAnalytics.css';

export default function BrandAnalytics() {
  const [dateRange, setDateRange] = useState('7d');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-01-31');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const { user } = useAuth();

  // Real analytics data
  const [analyticsData, setAnalyticsData] = useState({
    totalComplaints: 0,
    resolvedComplaints: 0,
    pendingComplaints: 0,
    avgResponseTime: '0h',
    satisfactionScore: 0,
    complaintsThisWeek: 0,
    complaintsLastWeek: 0,
    responseTimeTrend: '0%',
    satisfactionTrend: '0%'
  });

  const [tickets, setTickets] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange, startDate, endDate]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Fetch all tickets for the brand
      const allTickets = await ticketService.getTickets();
      
      // Filter tickets for this brand
      const brandTickets = allTickets.filter(ticket => ticket.brand_id === user?.brand_id);
      setTickets(brandTickets);

      // Calculate date ranges
      const now = new Date();
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

      // Calculate analytics
      const totalComplaints = brandTickets.length;
      const resolvedComplaints = brandTickets.filter(t => t.status === 'resolved').length;
      const pendingComplaints = brandTickets.filter(t => t.status !== 'resolved').length;
      
      // Calculate average response time (mock calculation for now)
      const avgResponseTime = totalComplaints > 0 ? '2.3h' : '0h';
      
      // Calculate satisfaction score
      const ratedTickets = brandTickets.filter(t => t.satisfaction_rating);
      const satisfactionScore = ratedTickets.length > 0 
        ? (ratedTickets.reduce((sum, t) => sum + (t.satisfaction_rating || 0), 0) / ratedTickets.length).toFixed(1)
        : 0;

      // Calculate weekly trends
      const complaintsThisWeek = brandTickets.filter(t => new Date(t.created_at) >= weekAgo).length;
      const complaintsLastWeek = brandTickets.filter(t => {
        const ticketDate = new Date(t.created_at);
        return ticketDate >= twoWeeksAgo && ticketDate < weekAgo;
      }).length;

      // Calculate trends
      const responseTimeTrend = '+12%'; // Mock trend
      const satisfactionTrend = '+5%'; // Mock trend

      // Generate recent activity
      const recentTickets = brandTickets
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5);

      const activity = recentTickets.map(ticket => ({
        id: ticket.id,
        type: ticket.status === 'resolved' ? 'resolved' : ticket.status === 'new' ? 'new' : 'urgent',
        title: `Complaint #${ticket.id} ${ticket.status === 'resolved' ? 'resolved' : ticket.status === 'new' ? 'received' : 'updated'}`,
        details: ticket.description?.substring(0, 50) + '...' || 'No description',
        time: getTimeAgo(ticket.created_at),
        icon: ticket.status === 'resolved' ? '✅' : ticket.status === 'new' ? '📝' : '🚨'
      }));

      setAnalyticsData({
        totalComplaints,
        resolvedComplaints,
        pendingComplaints,
        avgResponseTime,
        satisfactionScore: parseFloat(satisfactionScore),
        complaintsThisWeek,
        complaintsLastWeek,
        responseTimeTrend,
        satisfactionTrend
      });

      setRecentActivity(activity);

    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const getTimeAgo = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} days ago`;
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    // In a real app, this would fetch new data based on the date range
    fetchAnalyticsData();
  };

  const handleExport = (type) => {
    // Mock export functionality
    console.log(`Exporting ${type} data...`);
    alert(`${type} data exported successfully!`);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return '#27ae60';
      case 'pending': return '#f39c12';
      case 'urgent': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  // Calculate chart data for complaints over time
  const getChartData = () => {
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dayStart = new Date(date.setHours(0, 0, 0, 0));
      const dayEnd = new Date(date.setHours(23, 59, 59, 999));
      
      const dayTickets = tickets.filter(t => {
        const ticketDate = new Date(t.created_at);
        return ticketDate >= dayStart && ticketDate <= dayEnd;
      }).length;
      
      last7Days.push(dayTickets);
    }
    return last7Days;
  };

  // Calculate category distribution
  const getCategoryData = () => {
    const categories = {};
    tickets.forEach(ticket => {
      const category = ticket.category || 'other';
      categories[category] = (categories[category] || 0) + 1;
    });
    return categories;
  };

  const chartData = getChartData();
  const categoryData = getCategoryData();

  // Render Overview Tab Content
  const renderOverviewTab = () => (
    <>
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
            {analyticsData.totalComplaints > 0 ? ((analyticsData.resolvedComplaints / analyticsData.totalComplaints) * 100).toFixed(1) : 0}% resolution rate
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
            {analyticsData.complaintsLastWeek > 0 
              ? ((analyticsData.complaintsThisWeek - analyticsData.complaintsLastWeek) / analyticsData.complaintsLastWeek * 100).toFixed(1)
              : 0}%
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
              {chartData.map((height, index) => (
                <div 
                  key={index} 
                  className="chart-bar" 
                  style={{ height: `${Math.max(height * 10, 5)}%` }}
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
              {Object.entries(categoryData).map(([category, count]) => (
                <div key={category} className="legend-item">
                  <span className="legend-color" style={{ background: '#3498db' }}></span>
                  <span>{category.charAt(0).toUpperCase() + category.slice(1)} ({count})</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {recentActivity.length === 0 ? (
            <div className="text-center text-muted py-4">No recent activity</div>
          ) : (
            recentActivity.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">{activity.icon}</div>
                <div className="activity-content">
                  <div className="activity-title">{activity.title}</div>
                  <div className="activity-details">{activity.details}</div>
                  <div className="activity-time">{activity.time}</div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );

  // Render Complaints Tab Content
  const renderComplaintsTab = () => (
    <div className="complaints-tab">
      <div className="complaints-header">
        <h3>Complaint Details</h3>
        <div className="complaints-filters">
          <select className="filter-select">
            <option value="">All Status</option>
            <option value="new">New</option>
            <option value="pending">Pending</option>
            <option value="resolved">Resolved</option>
          </select>
          <select className="filter-select">
            <option value="">All Categories</option>
            <option value="technical">Technical</option>
            <option value="billing">Billing</option>
            <option value="service">Service</option>
            <option value="other">Other</option>
          </select>
        </div>
      </div>

      <div className="complaints-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Category</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center text-muted py-4">No complaints found</td>
              </tr>
            ) : (
              tickets.map((ticket) => (
                <tr key={ticket.id}>
                  <td>#{ticket.id}</td>
                  <td>{ticket.title || 'No title'}</td>
                  <td>{ticket.category || 'Other'}</td>
                  <td>
                    <span className={`status-badge status-${ticket.status}`}>
                      {ticket.status}
                    </span>
                  </td>
                  <td>{new Date(ticket.created_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/brand/tickets/${ticket.id}`} className="btn btn-sm btn-primary">
                      View
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );

  // Render Performance Tab Content
  const renderPerformanceTab = () => (
    <div className="performance-tab">
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
              {analyticsData.totalComplaints > 0 ? ((analyticsData.resolvedComplaints / analyticsData.totalComplaints) * 100).toFixed(1) : 0}%
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

      <div className="performance-charts">
        <div className="chart-container">
          <h3>Response Time Trend</h3>
          <div className="chart-placeholder">
            <div className="line-chart">
              <div className="line" style={{ background: 'linear-gradient(to right, #3498db, #27ae60)' }}></div>
              <div className="chart-points">
                <span className="point" style={{ left: '10%', top: '60%' }}></span>
                <span className="point" style={{ left: '30%', top: '40%' }}></span>
                <span className="point" style={{ left: '50%', top: '30%' }}></span>
                <span className="point" style={{ left: '70%', top: '20%' }}></span>
                <span className="point" style={{ left: '90%', top: '15%' }}></span>
              </div>
            </div>
          </div>
        </div>

        <div className="chart-container">
          <h3>Satisfaction Trend</h3>
          <div className="chart-placeholder">
            <div className="line-chart">
              <div className="line" style={{ background: 'linear-gradient(to right, #f39c12, #e74c3c)' }}></div>
              <div className="chart-points">
                <span className="point" style={{ left: '10%', top: '70%' }}></span>
                <span className="point" style={{ left: '30%', top: '50%' }}></span>
                <span className="point" style={{ left: '50%', top: '40%' }}></span>
                <span className="point" style={{ left: '70%', top: '30%' }}></span>
                <span className="point" style={{ left: '90%', top: '25%' }}></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render Trends Tab Content
  const renderTrendsTab = () => (
    <div className="trends-tab">
      <div className="trends-overview">
        <h3>Trends Analysis</h3>
        <div className="trends-grid">
          <div className="trend-card">
            <h4>Complaint Volume</h4>
            <div className="trend-value positive">+15%</div>
            <div className="trend-description">Increase from last month</div>
            <div className="trend-chart">
              <div className="mini-chart">
                <div className="bar" style={{ height: '30%' }}></div>
                <div className="bar" style={{ height: '45%' }}></div>
                <div className="bar" style={{ height: '60%' }}></div>
                <div className="bar" style={{ height: '75%' }}></div>
              </div>
            </div>
          </div>

          <div className="trend-card">
            <h4>Resolution Time</h4>
            <div className="trend-value negative">-8%</div>
            <div className="trend-description">Faster resolution</div>
            <div className="trend-chart">
              <div className="mini-chart">
                <div className="bar" style={{ height: '80%' }}></div>
                <div className="bar" style={{ height: '65%' }}></div>
                <div className="bar" style={{ height: '50%' }}></div>
                <div className="bar" style={{ height: '35%' }}></div>
              </div>
            </div>
          </div>

          <div className="trend-card">
            <h4>Customer Satisfaction</h4>
            <div className="trend-value positive">+12%</div>
            <div className="trend-description">Improved ratings</div>
            <div className="trend-chart">
              <div className="mini-chart">
                <div className="bar" style={{ height: '40%' }}></div>
                <div className="bar" style={{ height: '55%' }}></div>
                <div className="bar" style={{ height: '70%' }}></div>
                <div className="bar" style={{ height: '85%' }}></div>
              </div>
            </div>
          </div>

          <div className="trend-card">
            <h4>Category Distribution</h4>
            <div className="trend-value neutral">Stable</div>
            <div className="trend-description">No significant changes</div>
            <div className="trend-chart">
              <div className="mini-chart">
                <div className="bar" style={{ height: '50%' }}></div>
                <div className="bar" style={{ height: '50%' }}></div>
                <div className="bar" style={{ height: '50%' }}></div>
                <div className="bar" style={{ height: '50%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="trends-details">
        <div className="chart-container">
          <h3>Monthly Comparison</h3>
          <div className="comparison-chart">
            <div className="chart-legend">
              <span className="legend-item">
                <span className="legend-color" style={{ background: '#3498db' }}></span>
                Current Month
              </span>
              <span className="legend-item">
                <span className="legend-color" style={{ background: '#95a5a6' }}></span>
                Previous Month
              </span>
            </div>
            <div className="chart-bars">
              {[1, 2, 3, 4].map((week) => (
                <div key={week} className="week-group">
                  <div className="bar current" style={{ height: `${Math.random() * 60 + 20}%` }}></div>
                  <div className="bar previous" style={{ height: `${Math.random() * 60 + 20}%` }}></div>
                  <span className="week-label">Week {week}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="brand-analytics">
        <div className="analytics-header">
          <div className="header-container">
            <div className="brand-info">
              <div className="brand-logo">Analytics Dashboard</div>
              <div className="user-info">
                <span>Welcome back, {user?.full_name || 'User'}</span>
                <Link to="/brand/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
              </div>
            </div>
          </div>
        </div>
        <div className="main-content">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="brand-analytics">
        <div className="analytics-header">
          <div className="header-container">
            <div className="brand-info">
              <div className="brand-logo">Analytics Dashboard</div>
              <div className="user-info">
                <span>Welcome back, {user?.full_name || 'User'}</span>
                <Link to="/brand/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
              </div>
            </div>
          </div>
        </div>
        <div className="main-content">
          <div className="alert alert-danger">
            <h5>Error Loading Analytics</h5>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchAnalyticsData}>Retry</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="brand-analytics">
      {/* Header */}
      <header className="analytics-header">
        <div className="header-container">
          <div className="brand-info">
            <div className="brand-logo">Analytics Dashboard</div>
            <div className="user-info">
              <span>Welcome back, {user?.full_name || 'User'}</span>
              <Link to="/brand/dashboard" className="btn btn-secondary">← Back to Dashboard</Link>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <div className="nav-container">
          <button 
            className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => handleTabChange('overview')}
          >
            Overview
          </button>
          <button 
            className={`nav-tab ${activeTab === 'complaints' ? 'active' : ''}`}
            onClick={() => handleTabChange('complaints')}
          >
            Complaints
          </button>
          <button 
            className={`nav-tab ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => handleTabChange('performance')}
          >
            Performance
          </button>
          <button 
            className={`nav-tab ${activeTab === 'trends' ? 'active' : ''}`}
            onClick={() => handleTabChange('trends')}
          >
            Trends
          </button>
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

        {/* Tab Content */}
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'complaints' && renderComplaintsTab()}
        {activeTab === 'performance' && renderPerformanceTab()}
        {activeTab === 'trends' && renderTrendsTab()}
      </div>
    </div>
  );
}
