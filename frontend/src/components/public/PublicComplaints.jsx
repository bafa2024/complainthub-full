// frontend/src/components/public/PublicComplaints.jsx

import React, { useState, useEffect } from 'react';
import apiClient from '../../services/apiClient'; // Use apiClient directly for public routes
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';
import './PublicComplaints.css';

const PublicComplaints = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPublicTickets = async () => {
      try {
        setLoading(true);
        // This is a public endpoint, so we don't need the authenticated ticketService
        const response = await apiClient.get('/tickets/public');
        setTickets(response.data);
        setError('');
      } catch (err) {
        setError('Could not load public complaints. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPublicTickets();
  }, []);

  return (
    <div className="public-complaints-container">
      <div className="public-header">
        <h1>Unresolved Public Complaints</h1>
        <p>Brands are encouraged to resolve these issues promptly.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <div className="error-message">{error}</div>}
      
      {!loading && !error && (
        <div className="tickets-list">
          {tickets.length > 0 ? (
            tickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} />
            ))
          ) : (
            <div className="no-tickets">
              <p>There are currently no public unresolved complaints.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PublicComplaints;