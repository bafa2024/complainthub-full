import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';

const TicketDetail = () => {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // State for voice recording
  const [isRecording, setIsRecording] = useState(false);
  const [audioURL, setAudioURL] = useState('');
  const [audioBlob, setAudioBlob] = useState(null); // Store the audio blob
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const fetchTicketDetails = async () => {
      // ... (this function remains the same)
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
            setAudioBlob(newAudioBlob); // Save the blob to state
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
          await ticketService.uploadVoiceNote(ticketId, audioBlob);
          alert("Your voice note has been successfully added to the ticket!");
          // Clear the recording
          setAudioURL('');
          setAudioBlob(null);
          // Optionally, refresh ticket details to show the new recording URL
          fetchTicketDetails();
      } catch (err) {
          setError("Failed to upload voice note. Please try again.");
      }
  };

  // ... (the rest of the component's JSX remains the same)
  
  return (
    <div className="container mt-4">
      {/* ... (ticket details JSX) ... */}
      
      <div className="card mt-4">
        <div className="card-header">
            <h5>Add Voice Update</h5>
        </div>
        <div className="card-body text-center">
            {!isRecording ? (
                <button className="btn btn-primary" onClick={handleStartRecording}>Start Recording</button>
            ) : (
                <button className="btn btn-danger" onClick={handleStopRecording}>Stop Recording</button>
            )}
            
            {isRecording && <p className="text-danger mt-2">Recording...</p>}

            {audioURL && (
                <div className="mt-3">
                    <p>Your recorded message:</p>
                    <audio src={audioURL} controls />
                    <button onClick={handleSendVoiceNote} className="btn btn-success ms-3">Send Voice Note</button>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default TicketDetail;