import React from 'react';
import { Link } from 'react-router-dom';
import './TicketCard.css';

const TicketCard = ({ ticket, linkPrefix = '/tickets' }) => {
  if (!ticket) {
    return null;
  }

  const ticketDetailPath = `${linkPrefix}/${ticket.id}`;

  const getStatusIcon = (status) => {
    switch (status) {
      case 'new': return 'fas fa-plus-circle';
      case 'in-progress': return 'fas fa-clock';
      case 'resolved': return 'fas fa-check-circle';
      case 'closed': return 'fas fa-times-circle';
      default: return 'fas fa-question-circle';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'status-new';
      case 'in-progress': return 'status-progress';
      case 'resolved': return 'status-resolved';
      case 'closed': return 'status-closed';
      default: return 'status-default';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 0: return 'severity-low';
      case 1: return 'severity-medium';
      case 2: return 'severity-high';
      case 3: return 'severity-critical';
      case 4: return 'severity-emergency';
      case 5: return 'severity-abuse';
      default: return 'severity-unknown';
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
      case 'low': return 'urgency-low';
      case 'medium': return 'urgency-medium';
      case 'high': return 'urgency-high';
      default: return 'urgency-unknown';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <Link to={ticketDetailPath} className="ticket-card">
      <div className="ticket-card-header">
        <div className="ticket-title-section">
          <h3 className="ticket-title">{ticket.title || 'No Title'}</h3>
          {ticket.abuse_level_flag && (
            <span className="abuse-flag">
              <i className="fas fa-exclamation-triangle"></i>
              Abuse Flag
            </span>
          )}
        </div>
        <div className="ticket-badges">
          <span className={`status-badge ${getStatusColor(ticket.status)}`}>
            <i className={getStatusIcon(ticket.status)}></i>
            {ticket.status.replace('_', ' ').toUpperCase()}
          </span>
          {ticket.severity_level !== undefined && (
            <span className={`severity-badge ${getSeverityColor(ticket.severity_level)}`}>
              <i className="fas fa-exclamation-circle"></i>
              {getSeverityLabel(ticket.severity_level)}
            </span>
          )}
          {ticket.urgency && (
            <span className={`urgency-badge ${getUrgencyColor(ticket.urgency)}`}>
              <i className="fas fa-bolt"></i>
              {ticket.urgency.toUpperCase()}
            </span>
          )}
        </div>
      </div>
      
      <div className="ticket-card-body">
        <div className="ticket-info">
          <div className="info-item">
            <span className="info-label">
              <i className="fas fa-building"></i> Brand:
            </span>
            <span className="info-value">{ticket.brand?.name || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">
              <i className="fas fa-user"></i> User:
            </span>
            <span className="info-value">{ticket.owner?.full_name || ticket.owner?.email || 'Anonymous'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">
              <i className="fas fa-calendar"></i> Created:
            </span>
            <span className="info-value">{formatDate(ticket.created_at)}</span>
          </div>
          {ticket.updated_at && ticket.updated_at !== ticket.created_at && (
            <div className="info-item">
              <span className="info-label">
                <i className="fas fa-edit"></i> Updated:
              </span>
              <span className="info-value">{formatDate(ticket.updated_at)}</span>
            </div>
          )}
        </div>
        
        {ticket.description && (
          <div className="ticket-description">
            <p>{ticket.description.length > 150 
              ? `${ticket.description.substring(0, 150)}...` 
              : ticket.description}
            </p>
          </div>
        )}
        
        <div className="ticket-meta">
          {ticket.category && (
            <span className="meta-tag">
              <i className="fas fa-tag"></i>
              {ticket.category}
            </span>
          )}
          {ticket.priority && (
            <span className="meta-tag">
              <i className="fas fa-flag"></i>
              {ticket.priority}
            </span>
          )}
          {ticket.has_voice_recording && (
            <span className="meta-tag voice-tag">
              <i className="fas fa-microphone"></i>
              Voice Recording
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default TicketCard;