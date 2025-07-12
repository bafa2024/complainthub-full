import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './AdminAnalytics.css';

const AdminAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState('30d');
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    fetchAnalyticsData();
    startRealTimeUpdates();
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [overviewData, realTimeMetrics] = await Promise.all([
        adminService.getAnalyticsOverview(dateRange),
        adminService.getRealTimeMetrics()
      ]);

      setAnalyticsData(overviewData);
      setRealTimeData(realTimeMetrics);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const startRealTimeUpdates = () => {
    // Update real-time data every 30 seconds
    const interval = setInterval(async () => {
      try {
        const realTimeMetrics = await adminService.getRealTimeMetrics();
        setRealTimeData(realTimeMetrics);
      } catch (err) {
        console.error('Error updating real-time data:', err);
      }
    }, 30000);

    setRefreshInterval(interval);
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  const handleExport = async (type) => {
    try {
      const report = await adminService.generateReport(type, { date_range: dateRange });
      console.log(`${type} report generated:`, report);
      alert(`${type} report generated successfully!`);
    } catch (err) {
      console.error('Error generating report:', err);
      alert('Failed to generate report');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return '#007bff';
      case 'in-progress': return '#ffc107';
      case 'resolved': return '#28a745';
      case 'closed': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) return '📈';
    if (trend < 0) return '📉';
    return '➡️';
  };

  const getTrendClass = (trend) => {
    if (trend > 0) return 'trend-positive';
    if (trend < 0) return 'trend-negative';
    return 'trend-neutral';
  };

  if (loading) {
    return (
      <div className="admin-analytics">
        <div className="analytics-header">
          <h1>System Analytics</h1>
        </div>
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-analytics">
        <div className="analytics-header">
          <h1>System Analytics</h1>
        </div>
        <div className="error-container">
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
    <div className="admin-analytics">
      {/* Header */}
      <div className="analytics-header">
        <div className="header-content">
          <h1>System Analytics Dashboard</h1>
          <div className="header-actions">
            <div className="date-range-selector">
              <label>Date Range:</label>
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
            <div className="export-buttons">
              <button className="btn btn-outline-primary" onClick={() => handleExport('performance')}>
                Export Performance
              </button>
              <button className="btn btn-outline-primary" onClick={() => handleExport('trends')}>
                Export Trends
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="analytics-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'realtime' ? 'active' : ''}`}
          onClick={() => handleTabChange('realtime')}
        >
          Real-time
        </button>
        <button 
          className={`tab-button ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => handleTabChange('trends')}
        >
          Trends
        </button>
        <button 
          className={`tab-button ${activeTab === 'brands' ? 'active' : ''}`}
          onClick={() => handleTabChange('brands')}
        >
          Brand Performance
        </button>
        <button 
          className={`tab-button ${activeTab === 'channels' ? 'active' : ''}`}
          onClick={() => handleTabChange('channels')}
        >
          Channel Analysis
        </button>
      </div>

      {/* Tab Content */}
      <div className="analytics-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Key Metrics */}
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Total Users</span>
                  <span className="metric-icon">👥</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.total_users || 0}</div>
                <div className="metric-trend positive">+12% this month</div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Total Brands</span>
                  <span className="metric-icon">🏢</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.total_brands || 0}</div>
                <div className="metric-trend positive">+5 new this month</div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Total Complaints</span>
                  <span className="metric-icon">📝</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.total_tickets || 0}</div>
                <div className="metric-trend positive">+8% vs last period</div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Resolution Rate</span>
                  <span className="metric-icon">✅</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.resolution_rate || 0}%</div>
                <div className="metric-trend positive">+2.1% improvement</div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Avg Response Time</span>
                  <span className="metric-icon">⏱️</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.avg_resolution_time || 0}h</div>
                <div className="metric-trend positive">-15% faster</div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Satisfaction Score</span>
                  <span className="metric-icon">⭐</span>
                </div>
                <div className="metric-value">{analyticsData?.overview?.avg_satisfaction || 0}/5</div>
                <div className="metric-trend positive">+0.3 vs last period</div>
              </div>
            </div>

            {/* Status Breakdown */}
            <div className="status-breakdown">
              <h3>Complaint Status Distribution</h3>
              <div className="status-grid">
                {analyticsData?.status_breakdown && Object.entries(analyticsData.status_breakdown).map(([status, count]) => (
                  <div key={status} className="status-item">
                    <div className="status-indicator" style={{ backgroundColor: getStatusColor(status) }}></div>
                    <div className="status-info">
                      <span className="status-name">{status.charAt(0).toUpperCase() + status.slice(1)}</span>
                      <span className="status-count">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Channel Distribution */}
            <div className="channel-distribution">
              <h3>Channel Distribution</h3>
              <div className="channel-grid">
                {analyticsData?.channel_distribution && Object.entries(analyticsData.channel_distribution).map(([channel, count]) => (
                  <div key={channel} className="channel-item">
                    <div className="channel-icon">
                      {channel === 'whatsapp' && '📱'}
                      {channel === 'telegram' && '📬'}
                      {channel === 'webchat' && '💬'}
                      {channel === 'voice' && '🎤'}
                      {channel === 'email' && '📧'}
                      {channel === 'instagram' && '📸'}
                      {channel === 'linkedin' && '💼'}
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
        )}

        {activeTab === 'realtime' && (
          <div className="realtime-tab">
            <div className="realtime-header">
              <h3>Real-time Metrics</h3>
              <div className="refresh-indicator">
                <span className="pulse"></span>
                Live updates every 30 seconds
              </div>
            </div>

            <div className="realtime-grid">
              <div className="realtime-card">
                <div className="realtime-value">{realTimeData?.today_tickets || 0}</div>
                <div className="realtime-label">Tickets Today</div>
              </div>

              <div className="realtime-card">
                <div className="realtime-value">{realTimeData?.last_hour_tickets || 0}</div>
                <div className="realtime-label">Last Hour</div>
              </div>

              <div className="realtime-card">
                <div className="realtime-value">{realTimeData?.active_conversations || 0}</div>
                <div className="realtime-label">Active Conversations</div>
              </div>

              <div className="realtime-card">
                <div className="realtime-value">{realTimeData?.pending_tickets || 0}</div>
                <div className="realtime-label">Pending Tickets</div>
              </div>
            </div>

            <div className="system-health">
              <h4>System Health</h4>
              <div className="health-indicators">
                <div className="health-item">
                  <span className="health-label">Status:</span>
                  <span className={`health-status ${realTimeData?.system_health?.status || 'unknown'}`}>
                    {realTimeData?.system_health?.status || 'Unknown'}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Error Rate:</span>
                  <span className="health-value">{(realTimeData?.system_health?.error_rate || 0) * 100}%</span>
                </div>
                <div className="health-item">
                  <span className="health-label">Avg Response Time:</span>
                  <span className="health-value">{realTimeData?.system_health?.avg_response_time || 0}ms</span>
                </div>
              </div>
            </div>

            <div className="recent-activity">
              <h4>Recent Activity</h4>
              <div className="activity-list">
                {realTimeData?.recent_activity?.map((activity, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-icon">📝</div>
                    <div className="activity-content">
                      <div className="activity-title">Ticket #{activity.ticket_id}</div>
                      <div className="activity-details">{activity.title}</div>
                      <div className="activity-meta">
                        {activity.channel} • {new Date(activity.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                    <div className={`activity-status ${activity.status}`}>
                      {activity.status}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="trends-tab">
            <h3>Trend Analysis</h3>
            <div className="trends-grid">
              <div className="trend-chart">
                <h4>Daily Ticket Volume</h4>
                <div className="chart-placeholder">
                  <div className="chart-bars">
                    {analyticsData?.trends?.daily_tickets?.slice(-7).map((day, index) => (
                      <div key={index} className="chart-bar">
                        <div 
                          className="bar-fill" 
                          style={{ height: `${(day.count / Math.max(...analyticsData.trends.daily_tickets.map(d => d.count))) * 100}%` }}
                        ></div>
                        <div className="bar-label">{day.count}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="trend-metrics">
                <h4>Growth Metrics</h4>
                <div className="growth-item">
                  <span className="growth-label">Week-over-Week Growth:</span>
                  <span className={`growth-value ${getTrendClass(analyticsData?.trends?.growth_rate || 0)}`}>
                    {getTrendIcon(analyticsData?.trends?.growth_rate || 0)} {analyticsData?.trends?.growth_rate || 0}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'brands' && (
          <div className="brands-tab">
            <h3>Brand Performance</h3>
            <div className="brand-performance-grid">
              {/* This would be populated with brand-specific analytics */}
              <div className="brand-performance-placeholder">
                <p>Brand performance analytics will be displayed here</p>
                <p>Each brand will show their individual metrics and performance trends</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'channels' && (
          <div className="channels-tab">
            <h3>Channel Analysis</h3>
            <div className="channel-analysis-grid">
              {analyticsData?.channel_distribution && Object.entries(analyticsData.channel_distribution).map(([channel, count]) => (
                <div key={channel} className="channel-analysis-card">
                  <div className="channel-header">
                    <span className="channel-icon">
                      {channel === 'whatsapp' && '📱'}
                      {channel === 'telegram' && '📬'}
                      {channel === 'webchat' && '💬'}
                      {channel === 'voice' && '🎤'}
                      {channel === 'email' && '📧'}
                      {channel === 'instagram' && '📸'}
                      {channel === 'linkedin' && '💼'}
                    </span>
                    <span className="channel-name">{channel.charAt(0).toUpperCase() + channel.slice(1)}</span>
                  </div>
                  <div className="channel-stats">
                    <div className="stat-item">
                      <span className="stat-label">Total Tickets:</span>
                      <span className="stat-value">{count}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Resolution Rate:</span>
                      <span className="stat-value">85%</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Avg Response Time:</span>
                      <span className="stat-value">2.3h</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAnalytics; 