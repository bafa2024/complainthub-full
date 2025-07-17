import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandAnalytics.css';
import brandService from '../../services/brandService';

export default function BrandAnalytics() {
  const [dateRange, setDateRange] = useState('30d');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [realTimeData, setRealTimeData] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(null);

  const { user } = useAuth();

  useEffect(() => {
    fetchAnalyticsData();
    startRealTimeUpdates();
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [dateRange, startDate, endDate]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [overviewData, realTimeMetrics, tatData, abuseData, teamData] = await Promise.all([
        brandService.getBrandAnalytics(dateRange, startDate, endDate),
        brandService.getRealTimeMetrics(),
        brandService.getTATAnalytics(dateRange),
        brandService.getAbusePatternAnalytics(dateRange),
        brandService.getTeamPerformanceAnalytics(dateRange)
      ]);

      setAnalyticsData({
        overview: overviewData,
        tat: tatData,
        abuse: abuseData,
        team: teamData
      });
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
        const realTimeMetrics = await brandService.getRealTimeMetrics();
        setRealTimeData(realTimeMetrics);
      } catch (err) {
        console.error('Error updating real-time data:', err);
      }
    }, 30000);

    setRefreshInterval(interval);
  };

  const handleDateRangeChange = (range) => {
    setDateRange(range);
    if (range !== 'custom') {
      setStartDate('');
      setEndDate('');
    }
  };

  const handleExport = async (format) => {
    try {
      const result = await brandService.exportAnalyticsReport(activeTab, format, {
        dateRange,
        startDate,
        endDate
      });
      
      if (result.success) {
        // Create download link
        const blob = new Blob([result.data], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-${activeTab}-${new Date().toISOString().split('T')[0]}.${format.toLowerCase()}`;
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

  const formatDuration = (hours) => {
    if (hours < 1) {
      return `${Math.round(hours * 60)} minutes`;
    } else if (hours < 24) {
      return `${Math.round(hours)} hours`;
    } else {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${Math.round(remainingHours)}h`;
    }
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getSeverityColor = (level) => {
    const colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545', '#6f42c1', '#e83e8c'];
    return colors[level] || colors[0];
  };

  // Render Overview Tab Content
  const renderOverviewTab = () => (
    <div className="overview-tab">
      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <h3>Total Complaints</h3>
            <div className="metric-value">{analyticsData?.overview?.total_complaints || 0}</div>
            <div className="metric-change positive">+12.5% vs last period</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">✅</div>
          <div className="metric-content">
            <h3>Resolution Rate</h3>
            <div className="metric-value">{formatPercentage(analyticsData?.overview?.resolution_rate || 0)}</div>
            <div className="metric-change positive">+2.1% vs last period</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <h3>Avg Resolution Time</h3>
            <div className="metric-value">{formatDuration(analyticsData?.overview?.avg_resolution_time || 0)}</div>
            <div className="metric-change negative">+0.5h vs last period</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">⭐</div>
          <div className="metric-content">
            <h3>Customer Satisfaction</h3>
            <div className="metric-value">{analyticsData?.overview?.avg_satisfaction || 0}/5</div>
            <div className="metric-change positive">+0.2 vs last period</div>
          </div>
        </div>
      </div>

      {/* Real-time Metrics */}
      {realTimeData && (
        <div className="realtime-section">
          <h3>Real-time Activity</h3>
          <div className="realtime-grid">
            <div className="realtime-item">
              <span>Today's Complaints:</span>
              <span className="value">{realTimeData.today_complaints || 0}</span>
            </div>
            <div className="realtime-item">
              <span>Last Hour:</span>
              <span className="value">{realTimeData.last_hour_complaints || 0}</span>
            </div>
            <div className="realtime-item">
              <span>Active Conversations:</span>
              <span className="value">{realTimeData.active_conversations || 0}</span>
            </div>
            <div className="realtime-item">
              <span>Pending Tickets:</span>
              <span className="value">{realTimeData.pending_tickets || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Channel Performance */}
      <div className="channel-performance">
        <h3>Channel Performance</h3>
        <div className="channel-grid">
          {analyticsData?.overview?.channel_performance?.map((channel) => (
            <div key={channel.name} className="channel-card">
              <div className="channel-header">
                <h4>{channel.name}</h4>
                <span className="channel-count">{channel.count}</span>
              </div>
              <div className="channel-metrics">
                <div className="metric">
                  <span>Resolution Rate:</span>
                  <span>{formatPercentage(channel.resolution_rate)}</span>
                </div>
                <div className="metric">
                  <span>Avg Time:</span>
                  <span>{formatDuration(channel.avg_resolution_time)}</span>
                </div>
                <div className="metric">
                  <span>Satisfaction:</span>
                  <span>{channel.avg_satisfaction}/5</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Render TAT Analysis Tab Content
  const renderTATTab = () => (
    <div className="tat-tab">
      <div className="tat-overview">
        <h3>Turnaround Time Analysis</h3>
        
        <div className="tat-metrics">
          <div className="tat-metric">
            <h4>Average TAT</h4>
            <div className="tat-value">{formatDuration(analyticsData?.tat?.avg_tat || 0)}</div>
          </div>
          <div className="tat-metric">
            <h4>Median TAT</h4>
            <div className="tat-value">{formatDuration(analyticsData?.tat?.median_tat || 0)}</div>
          </div>
          <div className="tat-metric">
            <h4>90th Percentile</h4>
            <div className="tat-value">{formatDuration(analyticsData?.tat?.percentile_90 || 0)}</div>
          </div>
          <div className="tat-metric">
            <h4>24h Resolution Rate</h4>
            <div className="tat-value">{formatPercentage(analyticsData?.tat?.resolution_24h_rate || 0)}</div>
          </div>
        </div>

        <div className="tat-breakdown">
          <h4>TAT by Category</h4>
          <div className="tat-categories">
            {analyticsData?.tat?.category_breakdown?.map((category) => (
              <div key={category.name} className="tat-category">
                <div className="category-info">
                  <span className="category-name">{category.name}</span>
                  <span className="category-count">{category.count} complaints</span>
                </div>
                <div className="category-tat">
                  <span className="tat-time">{formatDuration(category.avg_tat)}</span>
                  <div className="tat-bar">
                    <div 
                      className="tat-progress" 
                      style={{ 
                        width: `${Math.min((category.avg_tat / 48) * 100, 100)}%`,
                        backgroundColor: category.avg_tat > 24 ? '#dc3545' : '#28a745'
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="tat-trends">
          <h4>TAT Trends</h4>
          <div className="trend-chart">
            {analyticsData?.tat?.daily_trends?.map((day) => (
              <div key={day.date} className="trend-day">
                <div className="trend-bar" style={{ height: `${(day.avg_tat / 48) * 100}%` }}></div>
                <span className="trend-date">{new Date(day.date).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Render Abuse Patterns Tab Content
  const renderAbuseTab = () => (
    <div className="abuse-tab">
      <div className="abuse-overview">
        <h3>Abuse Pattern Analysis</h3>
        
        <div className="abuse-summary">
          <div className="abuse-metric">
            <h4>Total Abuse Cases</h4>
            <div className="abuse-value">{analyticsData?.abuse?.total_cases || 0}</div>
          </div>
          <div className="abuse-metric">
            <h4>Abuse Rate</h4>
            <div className="abuse-value">{formatPercentage(analyticsData?.abuse?.abuse_rate || 0)}</div>
          </div>
          <div className="abuse-metric">
            <h4>Auto-Detection Rate</h4>
            <div className="abuse-value">{formatPercentage(analyticsData?.abuse?.auto_detection_rate || 0)}</div>
          </div>
        </div>

        <div className="abuse-patterns">
          <h4>Abuse Patterns by Severity</h4>
          <div className="severity-breakdown">
            {analyticsData?.abuse?.severity_breakdown?.map((severity) => (
              <div key={severity.level} className="severity-item">
                <div className="severity-header">
                  <span className="severity-level" style={{ backgroundColor: getSeverityColor(severity.level) }}>
                    Level {severity.level}
                  </span>
                  <span className="severity-count">{severity.count} cases</span>
                </div>
                <div className="severity-details">
                  <div className="detail">
                    <span>Percentage:</span>
                    <span>{formatPercentage(severity.percentage)}</span>
                  </div>
                  <div className="detail">
                    <span>Avg Toxicity Score:</span>
                    <span>{(severity.avg_toxicity_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="detail">
                    <span>Common Keywords:</span>
                    <span>{severity.common_keywords?.join(', ')}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="abuse-trends">
          <h4>Abuse Trends Over Time</h4>
          <div className="trend-chart">
            {analyticsData?.abuse?.daily_trends?.map((day) => (
              <div key={day.date} className="trend-day">
                <div className="trend-bar" style={{ height: `${(day.abuse_rate * 100)}%` }}></div>
                <span className="trend-date">{new Date(day.date).toLocaleDateString()}</span>
                <span className="trend-count">{day.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Render Team Performance Tab Content
  const renderTeamTab = () => (
    <div className="team-tab">
      <div className="team-overview">
        <h3>Team Performance Analytics</h3>
        
        <div className="team-summary">
          <div className="team-metric">
            <h4>Active Team Members</h4>
            <div className="team-value">{analyticsData?.team?.active_members || 0}</div>
          </div>
          <div className="team-metric">
            <h4>Avg Response Time</h4>
            <div className="team-value">{formatDuration(analyticsData?.team?.avg_response_time || 0)}</div>
          </div>
          <div className="team-metric">
            <h4>Team Efficiency</h4>
            <div className="team-value">{formatPercentage(analyticsData?.team?.efficiency_score || 0)}</div>
          </div>
        </div>

        <div className="team-members">
          <h4>Individual Performance</h4>
          <div className="members-table">
            <table>
              <thead>
                <tr>
                  <th>Team Member</th>
                  <th>Tickets Handled</th>
                  <th>Avg Resolution Time</th>
                  <th>Customer Satisfaction</th>
                  <th>Efficiency Score</th>
                </tr>
              </thead>
              <tbody>
                {analyticsData?.team?.member_performance?.map((member) => (
                  <tr key={member.id}>
                    <td>{member.name}</td>
                    <td>{member.tickets_handled}</td>
                    <td>{formatDuration(member.avg_resolution_time)}</td>
                    <td>{member.avg_satisfaction}/5</td>
                    <td>
                      <div className="efficiency-bar">
                        <div 
                          className="efficiency-progress" 
                          style={{ width: `${member.efficiency_score * 100}%` }}
                        ></div>
                      </div>
                      {formatPercentage(member.efficiency_score)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="team-insights">
          <h4>Performance Insights</h4>
          <div className="insights-grid">
            {analyticsData?.team?.insights?.map((insight, index) => (
              <div key={index} className="insight-card">
                <div className="insight-icon">💡</div>
                <div className="insight-content">
                  <h5>{insight.title}</h5>
                  <p>{insight.description}</p>
                </div>
              </div>
            ))}
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
    <div className="brand-analytics-container">
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

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'tat' ? 'active' : ''}`}
          onClick={() => setActiveTab('tat')}
        >
          TAT Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'abuse' ? 'active' : ''}`}
          onClick={() => setActiveTab('abuse')}
        >
          Abuse Patterns
        </button>
        <button 
          className={`tab-btn ${activeTab === 'team' ? 'active' : ''}`}
          onClick={() => setActiveTab('team')}
        >
          Team Performance
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'tat' && renderTATTab()}
      {activeTab === 'abuse' && renderAbuseTab()}
      {activeTab === 'team' && renderTeamTab()}
    </div>
  );
};

export default BrandAnalytics;
