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

  const handleStatusChange = async (newStatus) => {
    try {
      console.log('Attempting to update ticket status:', { numericTicketId, newStatus });
      const result = await ticketService.updateTicket(numericTicketId, { status: newStatus });
      console.log('Status update successful:', result);
      // Refresh ticket data after update
      fetchTicketDetails();
    } catch (error) {
      console.error('Status update failed:', error);
      setError(`Failed to update status: ${error.message}`);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;
  if (!ticket) return <div>Ticket not found.</div>;

  return (
    <div className="brand-ticket-detail-container">
      <Link to="/brand/dashboard">&larr; Back to Brand Dashboard</Link>
      <header className="ticket-detail-header">
        <h1>{ticket.title}</h1>
        <span className={`status-badge status-${ticket.status}`}>{ticket.status}</span>
      </header>

      <div className="ticket-management-panel">
        <h3>Manage Ticket</h3>
        <div className="status-updater">
            <p>Change Status:</p>
            <button onClick={() => handleStatusChange('in-progress')} className="btn btn-warning">In Progress</button>
            <button onClick={() => handleStatusChange('resolved')} className="btn btn-success">Resolved</button>
            <button onClick={() => handleStatusChange('closed')} className="btn btn-secondary">Closed</button>
        </div>
      </div>

      <div className="ticket-info">
        <p><strong>Customer:</strong> {ticket.owner.full_name || 'N/A'} ({ticket.owner.email})</p>
        <p><strong>Reported on:</strong> {new Date(ticket.created_at).toLocaleString()}</p>
        <p><strong>Channel:</strong> {ticket.channel}</p>
      </div>

      <div className="ticket-body">
        <h3>Complaint Details</h3>
        <p>{ticket.description}</p>
      </div>
    </div>
  );
};

export default BrandTicketDetail;