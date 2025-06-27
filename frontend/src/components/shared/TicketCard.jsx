import React from 'react';
import { Link } from 'react-router-dom';
export default function TicketCard({ ticket }) {
  return (
    <div style={{border:'1px solid #ccc',padding:'1rem',marginBottom:'1rem'}}>
      <Link to={\`/brand/tickets/\${ticket.id}\`}>
        #{ticket.id}: {ticket.user_name || 'Anonymous'}
      </Link>
      <div>Status: {ticket.status}</div>
    </div>
  );
}
