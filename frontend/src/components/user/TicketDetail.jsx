import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './TicketDetail.css';

const TicketDetail = () => {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // State for voice recording
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [audioBlob, setAudioBlob] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const fetchTicketDetails = async () => {
    try {
      setLoading(true);
      const ticketData = await ticketService.getTicketById(ticketId);
      setTicket(ticketData);
      setError('');
    } catch (err) {
      setError('Failed to load ticket details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTicketDetails();
  }, [ticketId]);

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = event => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = () => {
        const newAudioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(newAudioBlob);
        setAudioBlob(newAudioBlob);
        setAudioURL(audioUrl);
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Could not access microphone. Please check permissions.");
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  const handleSendVoiceNote = async () => {
    if (!audioBlob) return;
    
    try {
      // In demo mode, just show a success message
      alert("Your voice note has been successfully added to the ticket!");
      setAudioURL('');
      setAudioBlob(null);
    } catch (err) {
      setError("Failed to upload voice note. Please try again.");
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!ticket) return <div>Ticket not found.</div>;

  return (
    <div className="ticket-detail-container">
      <Link to="/dashboard">&larr; Back to Dashboard</Link>
      
      <div className="ticket-detail-header">
        <h1>{ticket.title}</h1>
        <span className={`status-badge status-${ticket.status}`}>{ticket.status}</span>
      </div>

      <div className="ticket-info">
        <p><strong>Brand:</strong> {ticket.brand?.name || 'N/A'}</p>
        <p><strong>Created:</strong> {new Date(ticket.created_at).toLocaleString()}</p>
        <p><strong>Channel:</strong> {ticket.channel}</p>
      </div>

      <div className="ticket-body">
        <h3>Description</h3>
        <p>{ticket.description}</p>
      </div>

      <div className="card mt-4">
        <div className="card-header">
          <h5>Add Voice Update</h5>
        </div>
        <div className="card-body text-center">
          {!isRecording ? (
            <button className="btn btn-primary" onClick={handleStartRecording}>
              Start Recording
            </button>
          ) : (
            <button className="btn btn-danger" onClick={handleStopRecording}>
              Stop Recording
            </button>
          )}
          
          {isRecording && <p className="text-danger mt-2">Recording...</p>}

          {audioURL && (
            <div className="mt-3">
              <p>Your recorded message:</p>
              <audio src={audioURL} controls />
              <button onClick={handleSendVoiceNote} className="btn btn-success ms-3">
                Send Voice Note
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;