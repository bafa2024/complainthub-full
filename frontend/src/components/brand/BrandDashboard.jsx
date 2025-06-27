import React, { useState, useEffect } from 'react';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';
import './BrandDashboard.css';

const BrandDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchBrandTickets = async () => {
      try {
        setLoading(true);
        const brandTickets = await ticketService.getTickets();
        setTickets(brandTickets);
        setError('');
      } catch (err) {
        setError('Failed to load tickets for your brand.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBrandTickets();
  }, []);

  const getStatusCounts = () => {
    const counts = { new: 0, open: 0, in_progress: 0, resolved: 0, closed: 0 };
    tickets.forEach(ticket => {
      const statusKey = ticket.status.replace('-', '_');
      if (counts.hasOwnProperty(statusKey)) {
        counts[statusKey]++;
      }
    });
    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div className="brand-dashboard-container">
      <header className="brand-dashboard-header">
        <h1>Brand Dashboard</h1>
      </header>

      <div className="stats-container">
        <div className="stat-card">
          <h2>{statusCounts.new}</h2>
          <p>New Complaints</p>
        </div>
        <div className="stat-card">
          <h2>{statusCounts.in_progress}</h2>
          <p>In Progress</p>
        </div>
        <div className="stat-card">
          <h2>{statusCounts.resolved}</h2>
          <p>Resolved</p>
        </div>
      </div>

      <div className="tickets-list-container">
        <h2>Recent Tickets</h2>
        {tickets.length > 0 ? (
          <div className="tickets-list">
            {tickets.map((ticket) => (
              // This now correctly links to the brand's ticket detail page
              <TicketCard key={ticket.id} ticket={ticket} linkPrefix="/brand/tickets" />
            ))}
          </div>
        ) : (
          <div className="no-tickets">
            <p>There are no tickets for your brand yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BrandDashboard;