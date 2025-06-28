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
      <div className="d-flex justify-content-between align-items-center mb-4 pb-2 border-bottom">
        <h1 className="mb-0">My Dashboard</h1>
        <div className="btn-group shadow-sm" role="group" aria-label="Lodge Complaint Actions">
          <Link to="/new-complaint" className="btn btn-outline-secondary d-flex align-items-center gap-2">
            Lodge via Form
          </Link>
          <Link to="/lodge-voice" className="btn btn-outline-secondary d-flex align-items-center gap-2">
            Lodge via Voice
          </Link>
          <Link to="/chat" className="btn btn-primary d-flex align-items-center gap-2">
            Start a Chat
          </Link>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row text-center mb-4 g-3">
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body d-flex flex-column justify-content-center">
              <h2 className="display-4 fw-bold">{tickets.length}</h2>
              <p className="text-muted mb-0">Total Tickets</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body d-flex flex-column justify-content-center">
              <h2 className="display-4 fw-bold">{statusCounts.new + statusCounts['in-progress']}</h2>
              <p className="text-muted mb-0">Active Tickets</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card h-100">
            <div className="card-body d-flex flex-column justify-content-center">
              <h2 className="display-4 fw-bold">{statusCounts.resolved}</h2>
              <p className="text-muted mb-0">Resolved Tickets</p>
            </div>
          </div>
        </div>
      </div>

      <h2>My Tickets</h2>
      {tickets.length > 0 ? (
        <div className="list-group">
          {tickets.map((ticket) => (
            <TicketCard key={ticket.id} ticket={ticket} linkPrefix="/tickets" />
          ))}
        </div>
      ) : (
        <div className="card card-body text-center">
          <p className="mb-0">You haven't submitted any tickets yet.</p>
        </div>
      )}
    </div>
  );
};

export default UserDashboard;