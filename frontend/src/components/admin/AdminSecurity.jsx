// frontend/src/components/admin/AdminSecurity.jsx

import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import securityService from '../../services/securityService';
import './AdminSecurity.css';

export default function AdminSecurity() {
  const { user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [securityData, setSecurityData] = useState({});
  const [events, setEvents] = useState([]);
  const [blacklistedIPs, setBlacklistedIPs] = useState([]);
  const [wafRules, setWafRules] = useState([]);
  const [ddosStatus, setDdosStatus] = useState({});
  const [complianceStatus, setComplianceStatus] = useState({});
  const [alert, setAlert] = useState({ show: false, type: '', message: '' });

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      setLoading(true);
      const [
        reportRes,
        eventsRes,
        blacklistRes,
        wafRes,
        ddosRes,
        complianceRes
      ] = await Promise.all([
        securityService.getSecurityReport(),
        securityService.getSecurityEvents({ limit: 50 }),
        securityService.getBlacklistedIPs(),
        securityService.getWAFRules(),
        securityService.getDDoSStatus(),
        securityService.getComplianceStatus()
      ]);

      setSecurityData(reportRes);
      setEvents(eventsRes);
      setBlacklistedIPs(blacklistRes.blacklisted_ips || []);
      setWafRules(wafRes.rules || []);
      setDdosStatus(ddosRes);
      setComplianceStatus(complianceRes);
    } catch (error) {
      showAlert('error', 'Failed to load security data');
    } finally {
      setLoading(false);
    }
  };

  const showAlert = (type, message) => {
    setAlert({ show: true, type, message });
    setTimeout(() => setAlert({ show: false, type: '', message: '' }), 5000);
  };

  const handleAddIPToBlacklist = async (ipAddress, reason) => {
    try {
      await securityService.addIPToBlacklist(ipAddress, reason);
      showAlert('success', 'IP added to blacklist');
      loadSecurityData();
    } catch (error) {
      showAlert('error', 'Failed to add IP to blacklist');
    }
  };

  const handleRemoveIPFromBlacklist = async (ipAddress) => {
    try {
      await securityService.removeIPFromBlacklist(ipAddress);
      showAlert('success', 'IP removed from blacklist');
      loadSecurityData();
    } catch (error) {
      showAlert('error', 'Failed to remove IP from blacklist');
    }
  };

  const handleUpdateWAFRules = async (rules) => {
    try {
      await securityService.updateWAFRules(rules);
      showAlert('success', 'WAF rules updated');
      loadSecurityData();
    } catch (error) {
      showAlert('error', 'Failed to update WAF rules');
    }
  };

  const handleUpdateThreatIntelligence = async () => {
    try {
      await securityService.updateThreatIntelligence();
      showAlert('success', 'Threat intelligence updated');
    } catch (error) {
      showAlert('error', 'Failed to update threat intelligence');
    }
  };

  const handleResetRateLimit = async (identifier) => {
    try {
      await securityService.resetRateLimit(identifier);
      showAlert('success', 'Rate limit reset');
    } catch (error) {
      showAlert('error', 'Failed to reset rate limit');
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="admin-security">
      <div className="security-header">
        <h1>Security Management</h1>
        <div className="security-actions">
          <button 
            className="btn btn-primary"
            onClick={handleUpdateThreatIntelligence}
          >
            Update Threat Intelligence
          </button>
          <button 
            className="btn btn-secondary"
            onClick={loadSecurityData}
          >
            Refresh Data
          </button>
        </div>
      </div>

      {alert.show && (
        <div className={`alert alert-${alert.type}`}>
          {alert.message}
        </div>
      )}

      <div className="security-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          Security Events
        </button>
        <button 
          className={`tab-button ${activeTab === 'blacklist' ? 'active' : ''}`}
          onClick={() => setActiveTab('blacklist')}
        >
          IP Blacklist
        </button>
        <button 
          className={`tab-button ${activeTab === 'waf' ? 'active' : ''}`}
          onClick={() => setActiveTab('waf')}
        >
          WAF Rules
        </button>
        <button 
          className={`tab-button ${activeTab === 'ddos' ? 'active' : ''}`}
          onClick={() => setActiveTab('ddos')}
        >
          DDoS Protection
        </button>
        <button 
          className={`tab-button ${activeTab === 'compliance' ? 'active' : ''}`}
          onClick={() => setActiveTab('compliance')}
        >
          Compliance
        </button>
      </div>

      <div className="security-content">
        {loading ? (
          <div className="loading">Loading security data...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="overview-tab">
                <div className="security-metrics">
                  <div className="metric-card">
                    <div className="metric-header">
                      <span className="metric-title">Total Events</span>
                      <span className="metric-icon">📊</span>
                    </div>
                    <div className="metric-value">{securityData.total_events || 0}</div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <span className="metric-title">Threats Detected</span>
                      <span className="metric-icon">⚠️</span>
                    </div>
                    <div className="metric-value">{securityData.threats_detected || 0}</div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <span className="metric-title">Blocked IPs</span>
                      <span className="metric-icon">🚫</span>
                    </div>
                    <div className="metric-value">{securityData.blocked_ips || 0}</div>
                  </div>

                  <div className="metric-card">
                    <div className="metric-header">
                      <span className="metric-title">DDoS Attacks</span>
                      <span className="metric-icon">🛡️</span>
                    </div>
                    <div className="metric-value">{securityData.ddos_attacks || 0}</div>
                  </div>
                </div>

                <div className="compliance-status">
                  <h3>Compliance Status</h3>
                  <div className="compliance-grid">
                    <div className={`compliance-item ${complianceStatus.gdpr_compliant ? 'compliant' : 'non-compliant'}`}>
                      <span className="compliance-label">GDPR</span>
                      <span className="compliance-status">{complianceStatus.gdpr_compliant ? 'Compliant' : 'Non-Compliant'}</span>
                    </div>
                    <div className={`compliance-item ${complianceStatus.data_retention_compliant ? 'compliant' : 'non-compliant'}`}>
                      <span className="compliance-label">Data Retention</span>
                      <span className="compliance-status">{complianceStatus.data_retention_compliant ? 'Compliant' : 'Non-Compliant'}</span>
                    </div>
                    <div className={`compliance-item ${complianceStatus.audit_trail_maintained ? 'compliant' : 'non-compliant'}`}>
                      <span className="compliance-label">Audit Trail</span>
                      <span className="compliance-status">{complianceStatus.audit_trail_maintained ? 'Maintained' : 'Not Maintained'}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'events' && (
              <div className="events-tab">
                <h3>Recent Security Events</h3>
                <div className="events-list">
                  {events.map((event, index) => (
                    <div key={index} className="event-item">
                      <div className="event-header">
                        <span className="event-type">{event.event_type}</span>
                        <span 
                          className="event-severity"
                          style={{ backgroundColor: getSeverityColor(event.severity) }}
                        >
                          {event.severity}
                        </span>
                      </div>
                      <div className="event-details">
                        <div className="event-timestamp">{formatTimestamp(event.timestamp)}</div>
                        <div className="event-info">
                          {Object.entries(event.details).map(([key, value]) => (
                            <div key={key} className="event-detail">
                              <span className="detail-label">{key}:</span>
                              <span className="detail-value">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'blacklist' && (
              <div className="blacklist-tab">
                <h3>IP Blacklist Management</h3>
                <div className="blacklist-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      const ip = prompt('Enter IP address:');
                      const reason = prompt('Enter reason:');
                      if (ip && reason) {
                        handleAddIPToBlacklist(ip, reason);
                      }
                    }}
                  >
                    Add IP to Blacklist
                  </button>
                </div>
                <div className="blacklist-table">
                  <table>
                    <thead>
                      <tr>
                        <th>IP Address</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {blacklistedIPs.map((ip, index) => (
                        <tr key={index}>
                          <td>{ip}</td>
                          <td>
                            <button 
                              className="btn btn-sm btn-danger"
                              onClick={() => handleRemoveIPFromBlacklist(ip)}
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'waf' && (
              <div className="waf-tab">
                <h3>Web Application Firewall Rules</h3>
                <div className="waf-actions">
                  <button 
                    className="btn btn-primary"
                    onClick={() => {
                      const rule = prompt('Enter new WAF rule pattern:');
                      if (rule) {
                        const newRules = [...wafRules, rule];
                        handleUpdateWAFRules(newRules);
                      }
                    }}
                  >
                    Add Rule
                  </button>
                </div>
                <div className="waf-rules">
                  {wafRules.map((rule, index) => (
                    <div key={index} className="waf-rule">
                      <span className="rule-pattern">{rule}</span>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => {
                          const newRules = wafRules.filter((_, i) => i !== index);
                          handleUpdateWAFRules(newRules);
                        }}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'ddos' && (
              <div className="ddos-tab">
                <h3>DDoS Protection Status</h3>
                <div className="ddos-status">
                  <div className="status-item">
                    <span className="status-label">Active Protection:</span>
                    <span className={`status-value ${ddosStatus.active_protection ? 'active' : 'inactive'}`}>
                      {ddosStatus.active_protection ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Blocked IPs:</span>
                    <span className="status-value">{ddosStatus.blocked_ips || 0}</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Threshold:</span>
                    <span className="status-value">{ddosStatus.threshold || 0} requests/minute</span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Window:</span>
                    <span className="status-value">{ddosStatus.window || 0} seconds</span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'compliance' && (
              <div className="compliance-tab">
                <h3>Compliance Management</h3>
                <div className="compliance-details">
                  <div className="compliance-section">
                    <h4>GDPR Compliance</h4>
                    <div className="compliance-status">
                      <span className={`status ${complianceStatus.gdpr_compliant ? 'compliant' : 'non-compliant'}`}>
                        {complianceStatus.gdpr_compliant ? 'Compliant' : 'Non-Compliant'}
                      </span>
                    </div>
                  </div>
                  <div className="compliance-section">
                    <h4>Data Retention</h4>
                    <div className="compliance-status">
                      <span className={`status ${complianceStatus.data_retention_compliant ? 'compliant' : 'non-compliant'}`}>
                        {complianceStatus.data_retention_compliant ? 'Compliant' : 'Non-Compliant'}
                      </span>
                    </div>
                  </div>
                  <div className="compliance-section">
                    <h4>Audit Trail</h4>
                    <div className="compliance-status">
                      <span className={`status ${complianceStatus.audit_trail_maintained ? 'compliant' : 'non-compliant'}`}>
                        {complianceStatus.audit_trail_maintained ? 'Maintained' : 'Not Maintained'}
                      </span>
                    </div>
                  </div>
                  <div className="compliance-section">
                    <h4>Last Audit</h4>
                    <div className="compliance-status">
                      <span className="status">
                        {complianceStatus.last_audit ? new Date(complianceStatus.last_audit).toLocaleString() : 'Never'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 