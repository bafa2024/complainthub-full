import React from 'react';
import { Link } from 'react-router-dom';
import './TicketCard.css'; // Make sure the CSS is imported

const TicketCard = ({ ticket, linkPrefix = '/tickets' }) => {
  if (!ticket) {
    return null;
  }

  // Correctly constructs the path without the extra backslash
  const ticketDetailPath = `${linkPrefix}/${ticket.id}`;

  return (
    <Link to={ticketDetailPath} className="ticket-card">
      <div className="ticket-card-header">
        <h3 className="ticket-title">{ticket.title || 'No Title'}</h3>
        <span className={`status-badge status-${ticket.status}`}>
          {ticket.status.replace('_', ' ')}
        </span>
      </div>
      <div className="ticket-card-body">
        <div className="ticket-info">
          <div className="info-item">
            <span className="info-label">Brand:</span>
            <span className="info-value">{ticket.brand?.name || 'N/A'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">User:</span>
            <span className="info-value">{ticket.owner?.full_name || ticket.owner?.email || 'Anonymous'}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Date:</span>
            <span className="info-value">{new Date(ticket.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default TicketCard;