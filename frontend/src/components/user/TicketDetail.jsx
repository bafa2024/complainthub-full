import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import SatisfactionRating from './SatisfactionRating'; // Import the new component

const TicketDetail = () => {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isRated, setIsRated] = useState(false); // To hide the form after submission

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        setLoading(true);
        // This uses the mocked service for now
        const ticketData = await ticketService.getTicketById(ticketId);
        setTicket(ticketData);
      } catch (err) {
        setError('Failed to load ticket details.');
      } finally {
        setLoading(false);
      }
    };
    fetchTicket();
  }, [ticketId]);
  
  const handleRatingSubmit = (rating, comment) => {
      console.log("Submitting rating:", { rating, comment });
      alert(`Thank you for your feedback! You gave a rating of ${rating} stars. (Mocked)`);
      setIsRated(true); // Hide the form after submission
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!ticket) return <div>Ticket not found.</div>;

  return (
    <div className="container mt-4">
      <Link to="/dashboard">&larr; Back to Dashboard</Link>
      <div className="card mt-2">
        <div className="card-header d-flex justify-content-between align-items-center">
            <h2 className="mb-0">{ticket.title}</h2>
            <span className={`badge bg-primary p-2`}>{ticket.status}</span>
        </div>
        <div className="card-body">
            <p><strong>Brand:</strong> {ticket.brand?.name}</p>
            <p><strong>Description:</strong> {ticket.description || 'No description provided.'}</p>
        </div>
      </div>
      
      {/* Conditionally render the rating section */}
      {ticket.status === 'resolved' && !isRated && (
           <div className="card mt-4">
                <div className="card-header">
                    <h5>How was our service?</h5>
                </div>
                <div className="card-body text-center">
                    <p>Please rate your satisfaction with the resolution of this ticket.</p>
                    <SatisfactionRating onSubmit={handleRatingSubmit} />
                </div>
            </div>
      )}

      {ticket.status === 'resolved' && isRated && (
          <div className="alert alert-success mt-4">
              Thank you for your feedback!
          </div>
      )}

    </div>
  );
};

export default TicketDetail;