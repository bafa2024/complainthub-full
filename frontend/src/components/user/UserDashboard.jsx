// ==================================================================
// File: frontend/src/components/user/UserDashboard.jsx
// Description: The main dashboard for a logged-in customer. It uses
// Bootstrap for layout and includes all complaint lodging options.
// ==================================================================
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import TicketCard from '../shared/TicketCard';
import { Modal } from 'bootstrap';

// SVG Icons for the buttons
const FormIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-pencil-square" viewBox="0 0 16 16"><path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293z"/><path fillRule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/></svg>
);
const VoiceIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-telephone-fill" viewBox="0 0 16 16"><path fillRule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.28 1.465l-2.138 2.138a.64.64 0 0 0 .045.901l6.206 6.207a.64.64 0 0 0 .901.045l2.138-2.138c.49-.164 1.042-.048 1.465.28l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.6 18.6 0 0 1-7.01-4.42 18.6 18.6 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877z"/></svg>
);
const ChatIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-chat-dots-fill" viewBox="0 0 16 16"><path d="M16 8c0 3.866-3.582 7-8 7a9 9 0 0 1-2.347-.306c-.584.296-1.925.864-4.181 1.234-.2.032-.352-.176-.273-.362.354-.836.674-1.95.77-2.966C.744 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7M5 8a1 1 0 1 0-2 0 1 1 0 0 0 2 0m4 0a1 1 0 1 0-2 0 1 1 0 0 0 2 0m3 1a1 1 0 1 0 0-2 1 1 0 0 0 0 2"/></svg>
);

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

  const handleLodgeByVoice = () => {
    const voiceModal = new Modal(document.getElementById('voiceComplaintModal'));
    voiceModal.show();
  };

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
            <FormIcon /> Lodge via Form
          </Link>
          <button type="button" onClick={handleLodgeByVoice} className="btn btn-outline-secondary d-flex align-items-center gap-2">
            <VoiceIcon /> Lodge via Call
          </button>
          <Link to="/chat" className="btn btn-primary d-flex align-items-center gap-2">
            <ChatIcon /> Start a Chat
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
      
      {/* Bootstrap Modal for Voice Complaint Info */}
      <div className="modal fade" id="voiceComplaintModal" tabIndex="-1" aria-labelledby="voiceModalLabel" aria-hidden="true">
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="voiceModalLabel">Lodge a Complaint by Phone</h5>
              <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div className="modal-body text-center">
              <p className="lead">To speak with our automated AI assistant, please call our 24/7 toll-free hotline at:</p>
              <h2 className="my-3"><a href="tel:1-800-555-0199">1-800-555-0199</a></h2>
              <small className="text-muted">Standard call rates may apply.</small>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;