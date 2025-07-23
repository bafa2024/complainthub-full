import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import adminService from '../../services/adminService';
import LoadingSpinner from '../shared/LoadingSpinner';
import Modal from '../shared/Modal';
import './Admin.css';

const AdminDashboardEnhanced = () => {
  const [dashboardData, setDashboardData] = useState({
    overview: {},
    realTime: {},
    recentActivity: [],
    systemHealth: {},
    topBrands: [],
    channelStats: {},
    revenueMetrics: {},
    securityOverview: {},
    predictiveAnalytics: {},
    alerts: []
  });
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState('30d');
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [showSystemModal, setShowSystemModal] = useState(false);
  const [systemAction, setSystemAction] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  
  const chartRef = useRef(null);
  const wsRef = useRef(null);

  const fetchComprehensiveDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      console.log('Fetching comprehensive admin dashboard data...');
      
      // Fetch all dashboard data in parallel
      const [
        dashboardRes,
        securityRes,
        healthRes,
        activityRes,
        brandsRes,
        predictiveRes
      ] = await Promise.all([
        adminService.getDashboardData(dateRange),
        adminService.getSecurityOverview(),
        adminService.getSystemHealth(),
        adminService.getRecentActivity(10),
        adminService.getTopBrands(5),
        adminService.getPredictiveAnalytics('tickets', 7)
      ]);

      // Combine all data
      setDashboardData({
        overview: dashboardRes.overview || {},
        realTime: dashboardRes.realTime || {},
        recentActivity: activityRes || [],
        systemHealth: healthRes || {},
        topBrands: brandsRes || [],
        securityOverview: securityRes || {},
        predictiveAnalytics: predictiveRes || {},
        channelStats: dashboardRes.channelStats || {},
        revenueMetrics: dashboardRes.revenueMetrics || {}
      });

      // Check for system alerts
      checkSystemAlerts(healthRes, securityRes, dashboardRes);

    } catch (err) {
      console.error('Enhanced admin dashboard error:', err);
      setError('Failed to load dashboard data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const checkSystemAlerts = (health, security, dashboard) => {
    const newAlerts = [];
    
    // System health alerts
    if (health?.error_rate > 0.05) {
      newAlerts.push({
        id: 'high-error-rate',
        type: 'warning',
        title: 'High Error Rate Detected',
        message: `Error rate is ${(health.error_rate * 100).toFixed(2)}% (threshold: 5%)`,
        timestamp: new Date(),
        action: 'View System Health'
      });
    }
    
    if (health?.avg_response_time > 1000) {
      newAlerts.push({
        id: 'slow-response',
        type: 'warning',
        title: 'Slow Response Times',
        message: `Average response time is ${health.avg_response_time}ms (threshold: 1000ms)`,
        timestamp: new Date(),
        action: 'View Performance'
      });
    }

    // Security alerts
    if (security?.threats_last_7_days > 0) {
      newAlerts.push({
        id: 'security-threats',
        type: 'danger',
        title: 'Security Threats Detected',
        message: `${security.threats_last_7_days} threats detected in the last 7 days`,
        timestamp: new Date(),
        action: 'View Security'
      });
    }

    // Traffic alerts
    if (dashboard?.realTime?.today_tickets > 100) {
      newAlerts.push({
        id: 'high-traffic',
        type: 'info',
        title: 'High Traffic Day',
        message: `${dashboard.realTime.today_tickets} tickets received today`,
        timestamp: new Date(),
        action: 'View Analytics'
      });
    }

    setAlerts(newAlerts);
  };

  const startRealTimeUpdates = () => {
    // Update real-time data every 15 seconds
    const interval = setInterval(async () => {
      try {
        const [realTimeData, healthData, securityData] = await Promise.all([
          adminService.getRealTimeMetrics(),
          adminService.getSystemHealth(),
          adminService.getSecurityOverview()
        ]);
        
        setDashboardData(prev => ({
          ...prev,
          realTime: realTimeData,
          systemHealth: healthData,
          securityOverview: securityData
        }));

        // Check for new alerts
        checkSystemAlerts(healthData, securityData, { realTime: realTimeData });
        
      } catch (err) {
        console.error('Error updating real-time data:', err);
      }
    }, 15000);

    setRefreshInterval(interval);
  };

  const initializeWebSocket = () => {
    // WebSocket for real-time notifications (mock implementation)
    const ws = new WebSocket('ws://localhost:8000/ws/admin');
    
    ws.onopen = () => {
      console.log('WebSocket connected for admin dashboard');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'alert') {
        setAlerts(prev => [...prev, {
          id: `ws-${Date.now()}`,
          type: data.severity,
          title: data.title,
          message: data.message,
          timestamp: new Date(),
          action: data.action
        }]);
      }
      
      if (data.type === 'metrics_update') {
        setDashboardData(prev => ({
          ...prev,
          realTime: { ...prev.realTime, ...data.metrics }
        }));
      }
    };
    
    ws.onerror = (error) => {
      console.log('WebSocket error:', error);
    };
    
    wsRef.current = ws;
  };

  const handleSystemAction = async (action) => {
    setSystemAction(action);
    setShowSystemModal(true);
  };

  const executeSystemAction = async () => {
    setActionLoading(true);
    try {
      switch (systemAction) {
        case 'restart':
          await adminService.restartSystem();
          setAlerts(prev => [...prev, {
            id: 'system-restart',
            type: 'success',
            title: 'System Restart Initiated',
            message: 'System restart has been initiated successfully',
            timestamp: new Date()
          }]);
          break;
        case 'backup':
          await adminService.createBackup();
          setAlerts(prev => [...prev, {
            id: 'backup-created',
            type: 'success',
            title: 'Backup Created',
            message: 'System backup has been created successfully',
            timestamp: new Date()
          }]);
          break;
        default:
          console.log('Unknown system action:', systemAction);
      }
      setShowSystemModal(false);
    } catch (error) {
      setAlerts(prev => [...prev, {
        id: 'action-error',
        type: 'danger',
        title: 'Action Failed',
        message: `Failed to execute ${systemAction}: ${error.message}`,
        timestamp: new Date()
      }]);
    } finally {
      setActionLoading(false);
    }
  };

  const dismissAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'success';
      case 'degraded': return 'warning';
      case 'critical': return 'danger';
      default: return 'secondary';
    }
  };

  useEffect(() => {
    fetchComprehensiveDashboardData();
    startRealTimeUpdates();
    // initializeWebSocket();
    
    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
      if (wsRef.current) wsRef.current.close();
    };
  }, [dateRange]);

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="page-container">
          <div className="page-header">
            <h1 className="page-title">
              <i className="fas fa-tachometer-alt me-2"></i>
              Enhanced Admin Dashboard
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
          <div className="alert alert-danger">
            <i className="fas fa-exclamation-triangle me-2"></i>
            <h5>Dashboard Error</h5>
            <p>{error}</p>
            <button className="btn btn-primary" onClick={fetchComprehensiveDashboardData}>
              <i className="fas fa-redo me-2"></i>Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const overview = dashboardData.overview?.overview || {};
  const realTime = dashboardData.realTime || {};
  const systemHealth = dashboardData.systemHealth || {};
  const securityOverview = dashboardData.securityOverview || {};

  return (
    <div className="admin-dashboard enhanced">
      {/* System Alerts */}
      {alerts.length > 0 && (
        <div className="alerts-container mb-4">
          {alerts.slice(0, 3).map(alert => (
            <div key={alert.id} className={`alert alert-${alert.type} alert-dismissible d-flex align-items-center`}>
              <div className="flex-grow-1">
                <div className="d-flex align-items-center">
                  <i className={`fas ${alert.type === 'danger' ? 'fa-exclamation-triangle' : 
                    alert.type === 'warning' ? 'fa-exclamation-circle' : 
                    alert.type === 'success' ? 'fa-check-circle' : 'fa-info-circle'} me-2`}></i>
                  <strong>{alert.title}</strong>
                </div>
                <small className="d-block mt-1">{alert.message}</small>
              </div>
              {alert.action && (
                <button className="btn btn-sm btn-outline-dark me-2">
                  {alert.action}
                </button>
              )}
              <button
                type="button"
                className="btn-close"
                onClick={() => dismissAlert(alert.id)}
              ></button>
            </div>
          ))}
        </div>
      )}

      <div className="page-container">
        {/* Enhanced Header */}
        <div className="page-header d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 className="page-title">
              <i className="fas fa-tachometer-alt me-2"></i>
              Enhanced Admin Dashboard
            </h1>
            <div className="d-flex align-items-center mt-2">
              <span className={`badge bg-${getStatusColor(systemHealth.status)} me-2`}>
                <i className="fas fa-circle me-1"></i>
                System {systemHealth.status || 'Unknown'}
              </span>
              <small className="text-muted">
                Last updated: {new Date().toLocaleTimeString()}
              </small>
            </div>
          </div>
          <div className="d-flex gap-2">
            <select 
              value={dateRange} 
              onChange={(e) => setDateRange(e.target.value)}
              className="form-select"
              style={{ width: 'auto' }}
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="1y">Last year</option>
            </select>
            <button 
              className="btn btn-outline-primary" 
              onClick={fetchComprehensiveDashboardData}
              disabled={loading}
            >
              <i className="fas fa-sync-alt me-2"></i>Refresh
            </button>
            <div className="dropdown">
              <button className="btn btn-warning dropdown-toggle" data-bs-toggle="dropdown">
                <i className="fas fa-cogs me-2"></i>System
              </button>
              <ul className="dropdown-menu">
                <li>
                  <button className="dropdown-item" onClick={() => handleSystemAction('backup')}>
                    <i className="fas fa-database me-2"></i>Create Backup
                  </button>
                </li>
                <li>
                  <button className="dropdown-item" onClick={() => handleSystemAction('restart')}>
                    <i className="fas fa-power-off me-2"></i>Restart System
                  </button>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                  <Link to="/admin/settings" className="dropdown-item">
                    <i className="fas fa-cog me-2"></i>System Settings
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Enhanced Metrics Grid */}
        <div className="enhanced-metrics-grid mb-4">
          <div className="metric-card primary">
            <div className="metric-header">
              <i className="fas fa-users"></i>
              <span className="metric-trend">+12%</span>
            </div>
            <div className="metric-value">{formatNumber(overview.total_users)}</div>
            <div className="metric-label">Total Users</div>
            <div className="metric-subtitle">Active: {formatNumber(overview.active_users || Math.floor((overview.total_users || 0) * 0.7))}</div>
          </div>

          <div className="metric-card success">
            <div className="metric-header">
              <i className="fas fa-building"></i>
              <span className="metric-trend">+5</span>
            </div>
            <div className="metric-value">{formatNumber(overview.total_brands)}</div>
            <div className="metric-label">Active Brands</div>
            <div className="metric-subtitle">Verified: {formatNumber(Math.floor((overview.total_brands || 0) * 0.9))}</div>
          </div>

          <div className="metric-card info">
            <div className="metric-header">
              <i className="fas fa-ticket-alt"></i>
              <span className="metric-trend">+8%</span>
            </div>
            <div className="metric-value">{formatNumber(overview.total_tickets)}</div>
            <div className="metric-label">Total Complaints</div>
            <div className="metric-subtitle">Today: {formatNumber(realTime.today_tickets)}</div>
          </div>

          <div className="metric-card warning">
            <div className="metric-header">
              <i className="fas fa-chart-line"></i>
              <span className="metric-trend">+2.1%</span>
            </div>
            <div className="metric-value">{overview.resolution_rate || 0}%</div>
            <div className="metric-label">Resolution Rate</div>
            <div className="metric-subtitle">Target: 95%</div>
          </div>

          <div className="metric-card danger">
            <div className="metric-header">
              <i className="fas fa-clock"></i>
              <span className="metric-trend">-15%</span>
            </div>
            <div className="metric-value">{overview.avg_resolution_time || 0}h</div>
            <div className="metric-label">Avg Resolution</div>
            <div className="metric-subtitle">SLA: 24h</div>
          </div>

          <div className="metric-card purple">
            <div className="metric-header">
              <i className="fas fa-rupee-sign"></i>
              <span className="metric-trend">+18%</span>
            </div>
            <div className="metric-value">₹{formatNumber(overview.total_revenue)}</div>
            <div className="metric-label">Total Revenue</div>
            <div className="metric-subtitle">This month</div>
          </div>
        </div>

        {/* Real-time System Status */}
        <div className="row g-4 mb-4">
          <div className="col-lg-8">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h4>
                  <i className="fas fa-pulse me-2"></i>
                  Real-time System Status
                  <span className="pulse-indicator ms-2">
                    <span className="pulse"></span>
                    Live
                  </span>
                </h4>
                <div className="system-actions">
                  <button className="btn btn-sm btn-outline-primary me-2">
                    <i className="fas fa-chart-area me-1"></i>View Details
                  </button>
                </div>
              </div>
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-md-3">
                    <div className="status-metric">
                      <div className="status-value text-primary">{realTime.today_tickets || 0}</div>
                      <div className="status-label">Tickets Today</div>
                      <div className="status-change">+{realTime.last_hour_tickets || 0} last hour</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="status-metric">
                      <div className="status-value text-warning">{realTime.pending_tickets || 0}</div>
                      <div className="status-label">Pending</div>
                      <div className="status-change">SLA: {Math.round(((realTime.pending_tickets || 0) / (realTime.today_tickets || 1)) * 100)}%</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="status-metric">
                      <div className="status-value text-success">{realTime.active_conversations || 0}</div>
                      <div className="status-label">Active Chats</div>
                      <div className="status-change">Peak: {Math.max(realTime.active_conversations || 0, 15)}</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="status-metric">
                      <div className="status-value text-info">{systemHealth.avg_response_time || 0}ms</div>
                      <div className="status-label">Avg Response</div>
                      <div className="status-change">Target: &lt;500ms</div>
                    </div>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span className="small">System Performance</span>
                    <span className="small text-muted">
                      Error Rate: {((systemHealth.error_rate || 0) * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="progress" style={{ height: '8px' }}>
                    <div 
                      className={`progress-bar bg-${systemHealth.error_rate > 0.05 ? 'danger' : 'success'}`}
                      style={{ width: `${Math.min(100 - (systemHealth.error_rate || 0) * 2000, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-4">
            <div className="card h-100">
              <div className="card-header">
                <h4>
                  <i className="fas fa-shield-alt me-2"></i>
                  Security Overview
                </h4>
              </div>
              <div className="card-body">
                <div className="security-metrics">
                  <div className="security-item">
                    <div className="d-flex justify-content-between">
                      <span>Security Score</span>
                      <span className="text-success fw-bold">{securityOverview.security_score || 85}/100</span>
                    </div>
                    <div className="progress mt-1" style={{ height: '6px' }}>
                      <div 
                        className="progress-bar bg-success" 
                        style={{ width: `${securityOverview.security_score || 85}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="security-item">
                    <div className="d-flex justify-content-between">
                      <span>Failed Logins (24h)</span>
                      <span className={`fw-bold ${(securityOverview.failed_login_attempts || 0) > 10 ? 'text-warning' : 'text-success'}`}>
                        {securityOverview.failed_login_attempts || 0}
                      </span>
                    </div>
                  </div>

                  <div className="security-item">
                    <div className="d-flex justify-content-between">
                      <span>Rate Limit Violations</span>
                      <span className={`fw-bold ${(securityOverview.rate_limit_violations || 0) > 5 ? 'text-warning' : 'text-success'}`}>
                        {securityOverview.rate_limit_violations || 0}
                      </span>
                    </div>
                  </div>

                  <div className="security-item">
                    <div className="d-flex justify-content-between">
                      <span>Threats (7 days)</span>
                      <span className={`fw-bold ${(securityOverview.threats_last_7_days || 0) > 0 ? 'text-danger' : 'text-success'}`}>
                        {securityOverview.threats_last_7_days || 0}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-3">
                  <Link to="/admin/security" className="btn btn-outline-primary btn-sm w-100">
                    <i className="fas fa-eye me-2"></i>View Security Details
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions & Recent Activity */}
        <div className="row g-4 mb-4">
          <div className="col-lg-4">
            <div className="card h-100">
              <div className="card-header">
                <h4>
                  <i className="fas fa-bolt me-2"></i>
                  Quick Actions
                </h4>
              </div>
              <div className="card-body p-0">
                <div className="list-group list-group-flush">
                  <Link to="/admin/users" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-users me-3 text-primary"></i>
                    <div>
                      <div>Manage Users</div>
                      <small className="text-muted">{formatNumber(overview.total_users)} total users</small>
                    </div>
                  </Link>
                  <Link to="/admin/brands" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-building me-3 text-success"></i>
                    <div>
                      <div>Manage Brands</div>
                      <small className="text-muted">{formatNumber(overview.total_brands)} active brands</small>
                    </div>
                  </Link>
                  <Link to="/admin/complaints" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-ticket-alt me-3 text-info"></i>
                    <div>
                      <div>View Complaints</div>
                      <small className="text-muted">{formatNumber(realTime.pending_tickets)} pending</small>
                    </div>
                  </Link>
                  <Link to="/admin/reports" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-chart-bar me-3 text-warning"></i>
                    <div>
                      <div>Analytics & Reports</div>
                      <small className="text-muted">Generate insights</small>
                    </div>
                  </Link>
                  <Link to="/admin/settings" className="list-group-item list-group-item-action d-flex align-items-center">
                    <i className="fas fa-cog me-3 text-secondary"></i>
                    <div>
                      <div>System Settings</div>
                      <small className="text-muted">Configure system</small>
                    </div>
                  </Link>
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-8">
            <div className="card h-100">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h4>
                  <i className="fas fa-history me-2"></i>
                  Recent System Activity
                </h4>
                <Link to="/admin/activity" className="btn btn-sm btn-outline-primary">
                  View All
                </Link>
              </div>
              <div className="card-body">
                <div className="activity-timeline">
                  {dashboardData.recentActivity?.slice(0, 8).map((activity, index) => (
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
                    <div className="text-center text-muted py-4">
                      <i className="fas fa-info-circle fa-2x mb-3"></i>
                      <p>No recent activity</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Performing Brands */}
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <h4>
              <i className="fas fa-trophy me-2"></i>
              Top Performing Brands
            </h4>
            <Link to="/admin/brands-analytics" className="btn btn-sm btn-outline-primary">
              View Analytics
            </Link>
          </div>
          <div className="card-body">
            <div className="row">
              {dashboardData.topBrands?.slice(0, 5).map((brand, index) => (
                <div key={index} className="col-md-6 col-lg-4 mb-3">
                  <div className={`top-brand-card rank-${index + 1}`}>
                    <div className="brand-rank">#{index + 1}</div>
                    <div className="brand-info">
                      <div className="brand-name">{brand.name}</div>
                      <div className="brand-metrics">
                        <div className="metric">
                          <span className="metric-value">{brand.resolution_rate}%</span>
                          <span className="metric-label">Resolution</span>
                        </div>
                        <div className="metric">
                          <span className="metric-value">{brand.avg_response_time}h</span>
                          <span className="metric-label">Response</span>
                        </div>
                        <div className="metric">
                          <span className="metric-value">{brand.total_tickets}</span>
                          <span className="metric-label">Tickets</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )) || (
                <div className="col-12 text-center text-muted py-4">
                  <i className="fas fa-info-circle fa-2x mb-3"></i>
                  <p>No brand performance data available</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* System Action Modal */}
      <Modal 
        show={showSystemModal} 
        onClose={() => setShowSystemModal(false)} 
        title={`Confirm System ${systemAction?.charAt(0).toUpperCase() + systemAction?.slice(1)}`}
      >
        <div className="text-center">
          <i className={`fas ${systemAction === 'restart' ? 'fa-power-off' : 'fa-database'} fa-3x text-warning mb-3`}></i>
          <h5>Are you sure?</h5>
          <p className="text-muted">
            This action will {systemAction === 'restart' ? 'restart the entire system' : 'create a system backup'}.
            {systemAction === 'restart' && ' Users may experience temporary downtime.'}
          </p>
          <div className="d-flex gap-2 justify-content-center mt-4">
            <button
              className={`btn btn-${systemAction === 'restart' ? 'danger' : 'warning'}`}
              onClick={executeSystemAction}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin me-2"></i>
                  Processing...
                </>
              ) : (
                <>
                  <i className={`fas ${systemAction === 'restart' ? 'fa-power-off' : 'fa-database'} me-2`}></i>
                  {systemAction === 'restart' ? 'Restart System' : 'Create Backup'}
                </>
              )}
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => setShowSystemModal(false)}
              disabled={actionLoading}
            >
              Cancel
            </button>
          </div>
        </div>
      </Modal>

      <style jsx>{`
        .enhanced-metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }

        .metric-card {
          background: white;
          border-radius: 12px;
          padding: 1.5rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          border-left: 4px solid var(--bs-primary);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .metric-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .metric-card.primary { border-left-color: var(--bs-primary); }
        .metric-card.success { border-left-color: var(--bs-success); }
        .metric-card.info { border-left-color: var(--bs-info); }
        .metric-card.warning { border-left-color: var(--bs-warning); }
        .metric-card.danger { border-left-color: var(--bs-danger); }
        .metric-card.purple { border-left-color: #6f42c1; }

        .metric-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .metric-header i {
          font-size: 1.2rem;
          opacity: 0.7;
        }

        .metric-trend {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--bs-success);
        }

        .metric-value {
          font-size: 2rem;
          font-weight: 700;
          color: #2c3e50;
          margin-bottom: 0.25rem;
        }

        .metric-label {
          font-weight: 600;
          color: #6c757d;
          margin-bottom: 0.25rem;
        }

        .metric-subtitle {
          font-size: 0.8rem;
          color: #adb5bd;
        }

        .status-metric {
          text-align: center;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .status-value {
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }

        .status-label {
          font-weight: 600;
          color: #6c757d;
          margin-bottom: 0.25rem;
        }

        .status-change {
          font-size: 0.8rem;
          color: #adb5bd;
        }

        .security-item {
          padding: 0.75rem 0;
          border-bottom: 1px solid #eee;
        }

        .security-item:last-child {
          border-bottom: none;
        }

        .activity-timeline {
          max-height: 300px;
          overflow-y: auto;
        }

        .activity-item {
          display: flex;
          align-items: center;
          padding: 0.75rem 0;
          border-bottom: 1px solid #eee;
        }

        .activity-item:last-child {
          border-bottom: none;
        }

        .activity-icon {
          width: 40px;
          height: 40px;
          border-radius: 20px;
          background: #f8f9fa;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 1rem;
        }

        .activity-icon i {
          color: var(--bs-primary);
        }

        .activity-title {
          font-weight: 600;
          margin-bottom: 0.25rem;
        }

        .activity-time {
          font-size: 0.8rem;
          color: #6c757d;
        }

        .top-brand-card {
          background: white;
          border-radius: 8px;
          padding: 1rem;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          position: relative;
          transition: transform 0.2s;
        }

        .top-brand-card:hover {
          transform: translateY(-2px);
        }

        .brand-rank {
          position: absolute;
          top: -10px;
          right: -10px;
          width: 30px;
          height: 30px;
          border-radius: 15px;
          background: var(--bs-primary);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          font-size: 0.8rem;
        }

        .rank-1 .brand-rank { background: #ffd700; color: #333; }
        .rank-2 .brand-rank { background: #c0c0c0; color: #333; }
        .rank-3 .brand-rank { background: #cd7f32; }

        .brand-name {
          font-weight: 600;
          margin-bottom: 0.75rem;
        }

        .brand-metrics {
          display: flex;
          justify-content: space-between;
        }

        .metric {
          text-align: center;
        }

        .metric-value {
          display: block;
          font-weight: 700;
          color: var(--bs-primary);
        }

        .metric-label {
          font-size: 0.7rem;
          color: #6c757d;
          text-transform: uppercase;
        }

        .alerts-container {
          position: fixed;
          top: 20px;
          right: 20px;
          z-index: 1050;
          max-width: 400px;
        }

        .pulse-indicator {
          display: inline-flex;
          align-items: center;
        }

        .pulse {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #28a745;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default AdminDashboardEnhanced;