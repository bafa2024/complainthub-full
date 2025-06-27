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
        {/* Correctly accesses the nested owner's name, provides a fallback */}
        <h3>{ticket.title || 'No Title'}</h3>
        <span className={`status-badge status-${ticket.status}`}>{ticket.status.replace('_', ' ')}</span>
      </div>
      <div className="ticket-card-body">
        <p>
          Brand: {ticket.brand?.name || 'N/A'}
        </p>
        <p>
          User: {ticket.owner?.full_name || ticket.owner?.email || 'Anonymous'}
        </p>
        <p>
          Date: {new Date(ticket.created_at).toLocaleDateString()}
        </p>
      </div>
    </Link>
  );
};

export default TicketCard;