// frontend/src/components/brand/BrandTicketDetail.jsx

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandTicketDetail.css';

const BrandTicketDetail = () => {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);
  const [showTaggingPanel, setShowTaggingPanel] = useState(false);
  
  // Convert ticketId to integer
  const numericTicketId = parseInt(ticketId, 10);
  
  const fetchTicketDetails = async () => {
    try {
      setLoading(true);
      console.log('Fetching ticket with ID:', numericTicketId);
      const ticketData = await ticketService.getTicketById(numericTicketId);
      setTicket(ticketData);
      setError('');
    } catch (err) {
      console.error('Error fetching ticket:', err);
      setError(`Failed to load ticket details: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isNaN(numericTicketId)) {
      setError('Invalid ticket ID');
      setLoading(false);
      return;
    }
    fetchTicketDetails();
  }, [ticketId]);

  const handleStatusUpdate = async (newStatus) => {
    try {
      setUpdating(true);
      console.log('Updating ticket status:', newStatus);
      const result = await ticketService.updateTicket(numericTicketId, { status: newStatus });
      console.log('Status update successful:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Status update failed:', error);
      setError(`Failed to update status: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleAssignTicket = async (assigneeId) => {
    try {
      setUpdating(true);
      console.log('Assigning ticket to:', assigneeId);
      const result = await ticketService.updateTicket(numericTicketId, { assignee_id: assigneeId });
      console.log('Assignment successful:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Assignment failed:', error);
      setError(`Failed to assign ticket: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleEscalateTicket = async () => {
    if (!window.confirm('Are you sure you want to escalate this ticket? This will notify administrators.')) {
      return;
    }
    
    try {
      setUpdating(true);
      console.log('Escalating ticket:', numericTicketId);
      const result = await ticketService.escalateTicket(numericTicketId);
      console.log('Escalation successful:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Escalation failed:', error);
      setError(`Failed to escalate ticket: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleResolveTicket = async () => {
    if (!window.confirm('Are you sure you want to mark this ticket as resolved? This will trigger follow-up verification.')) {
      return;
    }
    
    try {
      setUpdating(true);
      console.log('Resolving ticket:', numericTicketId);
      const result = await ticketService.updateTicket(numericTicketId, { status: 'resolved' });
      console.log('Resolution successful:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Resolution failed:', error);
      setError(`Failed to resolve ticket: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleCloseTicket = async () => {
    if (!window.confirm('Are you sure you want to close this ticket? This action cannot be undone.')) {
      return;
    }
    
    try {
      setUpdating(true);
      console.log('Closing ticket:', numericTicketId);
      const result = await ticketService.updateTicket(numericTicketId, { status: 'closed' });
      console.log('Ticket closed successfully:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Ticket closure failed:', error);
      setError(`Failed to close ticket: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleTaggingUpdate = async (taggingData) => {
    try {
      setUpdating(true);
      console.log('Updating ticket tagging:', taggingData);
      const result = await ticketService.updateTicket(numericTicketId, taggingData);
      console.log('Tagging update successful:', result);
      fetchTicketDetails();
      setShowTaggingPanel(false);
    } catch (error) {
      console.error('Tagging update failed:', error);
      setError(`Failed to update tagging: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const handleAutoTagging = async () => {
    try {
      setUpdating(true);
      console.log('Running auto-tagging for ticket:', numericTicketId);
      const result = await ticketService.autoTagTicket(numericTicketId);
      console.log('Auto-tagging successful:', result);
      fetchTicketDetails();
    } catch (error) {
      console.error('Auto-tagging failed:', error);
      setError(`Failed to auto-tag ticket: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 0: return '#28a745'; // Low - Green
      case 1: return '#ffc107'; // Medium - Yellow
      case 2: return '#fd7e14'; // High - Orange
      case 3: return '#dc3545'; // Critical - Red
      case 4: return '#6f42c1'; // Emergency - Purple
      case 5: return '#000000'; // Abuse - Black
      default: return '#6c757d';
    }
  };

  const getSeverityLabel = (severity) => {
    switch (severity) {
      case 0: return 'Low';
      case 1: return 'Medium';
      case 2: return 'High';
      case 3: return 'Critical';
      case 4: return 'Emergency';
      case 5: return 'Abuse';
      default: return 'Unknown';
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'low': return '#28a745';
      case 'medium': return '#ffc107';
      case 'high': return '#dc3545';
      default: return '#6c757d';
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;
  if (!ticket) return <div>Ticket not found.</div>;

  return (
    <div className="brand-ticket-detail-container">
      <Link to="/brand/dashboard">&larr; Back to Brand Dashboard</Link>
      
      {/* Header */}
      <div className="ticket-detail-header">
        <div>
          <h1>{ticket?.title || 'Loading...'}</h1>
          <div className="ticket-meta">
            <span>Ticket #{ticket?.id}</span>
            <span>Created: {ticket?.created_at ? new Date(ticket.created_at).toLocaleDateString() : 'N/A'}</span>
            <span>Updated: {ticket?.updated_at ? new Date(ticket.updated_at).toLocaleDateString() : 'N/A'}</span>
          </div>
        </div>
        
        <div className="ticket-status-badges">
          <span className={`status-badge status-${ticket?.status || 'new'}`}>
            {ticket?.status?.replace('-', ' ').toUpperCase() || 'NEW'}
          </span>
          <span className={`severity-badge severity-${ticket?.severity_level || 1}`}>
            Severity {ticket?.severity_level || 1}
          </span>
          <span className={`urgency-badge urgency-${ticket?.urgency || 'medium'}`}>
            {ticket?.urgency?.toUpperCase() || 'MEDIUM'}
          </span>
          {ticket?.abuse_level_flag && (
            <span className="abuse-badge">ABUSE FLAG</span>
          )}
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
          <button onClick={() => setError('')} className="close-btn">&times;</button>
        </div>
      )}

      {loading ? (
        <LoadingSpinner />
      ) : ticket ? (
        <div className="ticket-content">
          {/* Quick Actions */}
          <div className="quick-actions-panel">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              <button 
                className={`btn btn-sm ${ticket.status === 'new' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => handleStatusUpdate('new')}
                disabled={updating || ticket.status === 'new'}
              >
                Mark as New
              </button>
              
              <button 
                className={`btn btn-sm ${ticket.status === 'in-progress' ? 'btn-warning' : 'btn-outline-warning'}`}
                onClick={() => handleStatusUpdate('in-progress')}
                disabled={updating || ticket.status === 'in-progress'}
              >
                Mark In Progress
              </button>
              
              <button 
                className="btn btn-sm btn-success"
                onClick={handleResolveTicket}
                disabled={updating || ticket.status === 'resolved'}
              >
                Mark Resolved
              </button>
              
              <button 
                className="btn btn-sm btn-danger"
                onClick={handleEscalateTicket}
                disabled={updating}
              >
                Escalate
              </button>
              
              <button 
                className="btn btn-sm btn-secondary"
                onClick={handleCloseTicket}
                disabled={updating || ticket.status === 'closed'}
              >
                Close Ticket
              </button>
              
              <button 
                className="btn btn-sm btn-info"
                onClick={() => setShowTaggingPanel(!showTaggingPanel)}
                disabled={updating}
              >
                {showTaggingPanel ? 'Hide' : 'Show'} Tagging
              </button>
            </div>
          </div>

          {/* Tagging Panel */}
          {showTaggingPanel && (
            <div className="tagging-panel">
              <h3>AI Tagging & Classification</h3>
              <div className="tagging-actions">
                <button 
                  className="btn btn-primary"
                  onClick={handleAutoTagging}
                  disabled={updating}
                >
                  {updating ? 'Processing...' : 'Run AI Auto-Tagging'}
                </button>
              </div>
              
              <div className="tagging-form">
                <div className="form-group">
                  <label>Severity Level (0-5):</label>
                  <select 
                    value={ticket.severity_level || 1}
                    onChange={(e) => handleTaggingUpdate({ severity_level: parseInt(e.target.value) })}
                    disabled={updating}
                  >
                    <option value={0}>0 - Low (Positive Feedback)</option>
                    <option value={1}>1 - Medium (Standard Complaint)</option>
                    <option value={2}>2 - High (Serious Issue)</option>
                    <option value={3}>3 - Critical (Urgent Problem)</option>
                    <option value={4}>4 - Emergency (Multiple Customers)</option>
                    <option value={5}>5 - Abuse (Toxic Content)</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Urgency:</label>
                  <select 
                    value={ticket.urgency || 'medium'}
                    onChange={(e) => handleTaggingUpdate({ urgency: e.target.value })}
                    disabled={updating}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label>
                    <input 
                      type="checkbox"
                      checked={ticket.abuse_level_flag || false}
                      onChange={(e) => handleTaggingUpdate({ abuse_level_flag: e.target.checked })}
                      disabled={updating}
                    />
                    Abuse Level Flag
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Ticket Details */}
          <div className="ticket-details">
            <div className="detail-section">
              <h3>Description</h3>
              <p>{ticket.description || 'No description provided.'}</p>
            </div>

            {ticket.transcript && (
              <div className="detail-section">
                <h3>Voice Transcript</h3>
                <p>{ticket.transcript}</p>
              </div>
            )}

            <div className="detail-section">
              <h3>Customer Information</h3>
              <p><strong>Name:</strong> {ticket.owner?.full_name || 'Anonymous'}</p>
              <p><strong>Email:</strong> {ticket.owner?.email || 'N/A'}</p>
              <p><strong>Phone:</strong> {ticket.owner?.phone || 'N/A'}</p>
            </div>

            <div className="detail-section">
              <h3>Ticket Information</h3>
              <p><strong>Category:</strong> {ticket.category?.replace('_', ' ').toUpperCase() || 'N/A'}</p>
              <p><strong>Channel:</strong> {ticket.channel?.toUpperCase() || 'N/A'}</p>
              <p><strong>Assignee:</strong> {ticket.assignee?.full_name || 'Unassigned'}</p>
              {ticket.satisfaction_rating && (
                <p><strong>Satisfaction Rating:</strong> {ticket.satisfaction_rating}/5</p>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="alert alert-warning">Ticket not found.</div>
      )}
    </div>
  );
};

export default BrandTicketDetail;