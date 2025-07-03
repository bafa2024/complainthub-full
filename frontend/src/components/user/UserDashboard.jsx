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
    <div className="user-dashboard">
      {/* Dashboard Header */}
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">
            <i className="fas fa-tachometer-alt me-2"></i>
            My Dashboard
          </h1>
          <p className="page-subtitle">Manage your complaints and track their progress</p>
        </div>

        {error && (
          <div className="alert alert-danger">
            <i className="fas fa-exclamation-triangle me-2"></i>
            {error}
          </div>
        )}

        {/* Quick Actions */}
        <div className="dashboard-actions mb-4">
          <Link to="/new-complaint" className="btn btn-outline-secondary dashboard-action-btn">
            <i className="fas fa-file-alt me-2"></i>
            Lodge via Form
          </Link>
          <Link to="/lodge-voice" className="btn btn-outline-secondary dashboard-action-btn">
            <i className="fas fa-microphone me-2"></i>
            Lodge via Voice
          </Link>
          <Link to="/chat" className="btn btn-primary dashboard-action-btn">
            <i className="fas fa-comments me-2"></i>
            Start a Chat
          </Link>
        </div>

        {/* Statistics Cards */}
        <div className="stats-grid mb-4">
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-ticket-alt"></i>
              </div>
              <h2 className="stat-number">{tickets.length}</h2>
              <p className="stat-label">Total Tickets</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-clock"></i>
              </div>
              <h2 className="stat-number">{statusCounts.new + statusCounts['in-progress']}</h2>
              <p className="stat-label">Active Tickets</p>
            </div>
          </div>
          <div className="stat-card card">
            <div className="card-body text-center">
              <div className="stat-icon">
                <i className="fas fa-check-circle"></i>
              </div>
              <h2 className="stat-number">{statusCounts.resolved}</h2>
              <p className="stat-label">Resolved Tickets</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tickets Section */}
      <div className="page-container">
        <div className="page-header">
          <h2 className="page-title">
            <i className="fas fa-list me-2"></i>
            My Tickets
          </h2>
          <p className="page-subtitle">Track the status of your complaints</p>
        </div>

        {tickets.length > 0 ? (
          <div className="tickets-list">
            {tickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} linkPrefix="/tickets" />
            ))}
          </div>
        ) : (
          <div className="card">
            <div className="card-body text-center">
              <div className="empty-state">
                <i className="fas fa-inbox fa-3x text-muted mb-3"></i>
                <h3>No Tickets Yet</h3>
                <p className="text-muted">You haven't submitted any complaints yet. Start by lodging your first complaint!</p>
                <Link to="/new-complaint" className="btn btn-primary">
                  <i className="fas fa-plus me-2"></i>
                  Lodge Your First Complaint
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserDashboard;