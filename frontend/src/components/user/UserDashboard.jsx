import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';

const UserDashboard = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // NOTE: This uses the mocked service for now.
    const fetchTickets = async () => {
      try {
        setLoading(true);
        const userTickets = await ticketService.getTickets();
        setTickets(userTickets);
        setError('');
      } catch (err) {
        setError('Failed to load tickets. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, []);

  const getStatusCounts = () => {
    const counts = { new: 0, 'in-progress': 0, resolved: 0 };
    tickets.forEach(ticket => {
      if (ticket.status in counts) {
        counts[ticket.status]++;
      }
    });
    return counts;
  };
  const statusCounts = getStatusCounts();

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="dashboard-header mb-4">
        <h1 className="mb-3">My Dashboard</h1>
        <div className="btn-group dashboard-actions" role="group" aria-label="Lodge Complaint Actions">
          <Link to="/new-complaint" className="btn btn-outline-secondary dashboard-action-btn">
            Lodge via Form
          </Link>
          <Link to="/lodge-voice" className="btn btn-outline-secondary dashboard-action-btn">
            Lodge via Voice
          </Link>
          <Link to="/chat" className="btn btn-primary dashboard-action-btn">
            Start a Chat
          </Link>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="stats-container">
        <div className="stat-card">
          <h2>{tickets.length}</h2>
          <p>Total Tickets</p>
        </div>
        <div className="stat-card">
          <h2>{statusCounts.new + statusCounts['in-progress']}</h2>
          <p>Active Tickets</p>
        </div>
        <div className="stat-card">
          <h2>{statusCounts.resolved}</h2>
          <p>Resolved Tickets</p>
        </div>
      </div>

      <div className="tickets-section">
        <h2 className="mb-3">My Tickets</h2>
        {tickets.length > 0 ? (
          <div className="tickets-list">
            {tickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} linkPrefix="/tickets" />
            ))}
          </div>
        ) : (
          <div className="card">
            <div className="card-body text-center">
              <p className="mb-0">You haven't submitted any tickets yet.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;