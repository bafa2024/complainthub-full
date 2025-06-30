// Create this file at: frontend/src/components/user/LodgeVoicePage.jsx

import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import VoiceRecorder from '../shared/VoiceRecorder';
import './LodgeVoicePage.css'; // We will create this CSS file next
import apiClient from '../../services/apiClient';

// SVG Icons for the option cards
const PhoneIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-telephone-outbound-fill mb-3" viewBox="0 0 16 16">
    <path fillRule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.28 1.465l-2.138 2.138a.64.64 0 0 0 .045.901l6.206 6.207a.64.64 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5"/>
  </svg>
);
const WebchatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-mic-fill mb-3" viewBox="0 0 16 16">
        <path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0z"/><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5"/>
    </svg>
);

const LodgeVoicePage = () => {
  const [isVoiceChatActive, setIsVoiceChatActive] = useState(false);
  const [complaintData, setComplaintData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium'
  });
  const [audioBlob, setAudioBlob] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [submittedAudioURL, setSubmittedAudioURL] = useState(null);

  const handleStartWebVoiceChat = () => {
    setIsVoiceChatActive(true);
  };

  const handleBackToOptions = () => {
    setIsVoiceChatActive(false);
    setComplaintData({
      title: '',
      description: '',
      category: '',
      priority: 'medium'
    });
    setAudioBlob(null);
  };

  const handleRecordingComplete = (blob) => {
    setAudioBlob(blob);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setComplaintData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmitComplaint = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg('');
    setSubmissionResult(null);
    setSubmittedAudioURL(null);

    try {
      // Create FormData to send both audio and form data
      const formData = new FormData();
      formData.append('metadata', JSON.stringify(complaintData));
      if (audioBlob) {
        formData.append('audio', audioBlob, 'complaint-recording.wav');
        setSubmittedAudioURL(URL.createObjectURL(audioBlob));
      } else {
        setErrorMsg('Please record your complaint before submitting.');
        setIsSubmitting(false);
        return;
      }

      // Real API call
      const response = await apiClient.post('/tickets_extended/voice', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (!response.data.transcript || response.data.transcript.trim() === "") {
        setErrorMsg('Transcription failed or was empty. Please try again or speak more clearly.');
        setIsSubmitting(false);
        return;
      }
      setSubmissionResult(response.data);
      handleBackToOptions();
    } catch (error) {
      setErrorMsg(error?.message || 'Failed to submit complaint. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submissionResult) {
    return (
      <div className="container lodge-voice-container">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow mt-5">
              <div className="card-header bg-success text-white">
                <h3 className="mb-0">Voice Complaint Submitted!</h3>
              </div>
              <div className="card-body p-4">
                <p><strong>Ticket ID:</strong> {submissionResult.ticket_id}</p>
                <p><strong>Transcript:</strong> {submissionResult.transcript}</p>
                <p><strong>Category:</strong> {submissionResult.category}</p>
                {typeof submissionResult.sentiment !== 'undefined' && (
                  <p><strong>Sentiment Score:</strong> {submissionResult.sentiment}</p>
                )}
                {typeof submissionResult.urgency !== 'undefined' && (
                  <p><strong>Urgency Level:</strong> {submissionResult.urgency}</p>
                )}
                {submittedAudioURL && (
                  <div className="mb-3">
                    <strong>Your Submitted Audio:</strong>
                    <audio src={submittedAudioURL} controls className="w-100 mt-2" />
                    <a href={submittedAudioURL} download="complaint-recording.wav" className="btn btn-outline-secondary btn-sm mt-2">Download Audio</a>
                  </div>
                )}
                <div className="mt-3">
                  <Link to="/dashboard" className="btn btn-primary me-2">Go to Dashboard</Link>
                  <Link to={`/tickets/${submissionResult.ticket_id}`} className="btn btn-outline-primary">View Ticket</Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isVoiceChatActive) {
    return (
      <div className="container lodge-voice-container">
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="card shadow">
              <div className="card-header bg-primary text-white">
                <h3 className="mb-0">
                  <button 
                    className="btn btn-link text-white p-0 me-3" 
                    onClick={handleBackToOptions}
                  >
                    ←
                  </button>
                  Record Your Voice Complaint
                </h3>
              </div>
              <div className="card-body p-4">
                <form onSubmit={handleSubmitComplaint}>
                  {/* Voice Recorder */}
                  <div className="mb-4">
                    <h5 className="mb-3">Step 1: Record Your Complaint</h5>
                    <VoiceRecorder onRecordingComplete={handleRecordingComplete} />
                    {audioBlob && (
                      <div className="alert alert-success mt-2">
                        ✓ Audio recording completed! You can now fill in the details below.
                      </div>
                    )}
                  </div>

                  {/* Complaint Details Form */}
                  <div className="mb-4">
                    <h5 className="mb-3">Step 2: Add Complaint Details</h5>
                    
                    <div className="mb-3">
                      <label htmlFor="title" className="form-label">Complaint Title *</label>
                      <input
                        type="text"
                        className="form-control"
                        id="title"
                        name="title"
                        value={complaintData.title}
                        onChange={handleInputChange}
                        placeholder="Brief title for your complaint"
                        required
                      />
                    </div>

                    <div className="mb-3">
                      <label htmlFor="category" className="form-label">Category *</label>
                      <select
                        className="form-select"
                        id="category"
                        name="category"
                        value={complaintData.category}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="">Select a category</option>
                        <option value="technical">Technical Issue</option>
                        <option value="billing">Billing Problem</option>
                        <option value="service">Service Quality</option>
                        <option value="delivery">Delivery Issue</option>
                        <option value="refund">Refund Request</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div className="mb-3">
                      <label htmlFor="priority" className="form-label">Priority Level</label>
                      <select
                        className="form-select"
                        id="priority"
                        name="priority"
                        value={complaintData.priority}
                        onChange={handleInputChange}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>

                    <div className="mb-4">
                      <label htmlFor="description" className="form-label">Additional Details</label>
                      <textarea
                        className="form-control"
                        id="description"
                        name="description"
                        value={complaintData.description}
                        onChange={handleInputChange}
                        rows="4"
                        placeholder="Provide any additional context or details about your complaint..."
                      />
                    </div>
                  </div>

                  {errorMsg && <div className="alert alert-danger">{errorMsg}</div>}
                  {isSubmitting && (
                    <div className="text-center my-3">
                      <span className="spinner-border text-primary" role="status" aria-hidden="true"></span>
                      <div>Uploading and transcribing your complaint, please wait...</div>
                    </div>
                  )}

                  {/* Submit Button */}
                  <div className="d-grid">
                    <button
                      type="submit"
                      className="btn btn-primary btn-lg"
                      disabled={isSubmitting || !audioBlob}
                    >
                      {isSubmitting ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Submitting Complaint...
                        </>
                      ) : (
                        'Submit Voice Complaint'
                      )}
                    </button>
                  </div>

                  {!audioBlob && (
                    <div className="alert alert-info mt-3">
                      <i className="bi bi-info-circle me-2"></i>
                      Please record your voice complaint first before submitting.
                    </div>
                  )}
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container lodge-voice-container text-center">
      <h1 className="display-5 fw-bold mb-3">Lodge a Complaint Using Your Voice</h1>
      <p className="lead mb-5">Choose your preferred method below to speak with our AI assistant.</p>
      
      <div className="row g-4 justify-content-center">
        {/* Option 1: Phone Call */}
        <div className="col-md-5">
          <div className="card h-100 shadow-sm option-card">
            <div className="card-body">
              <PhoneIcon />
              <h4 className="card-title">Call Our Hotline</h4>
              <p className="card-text">
                Use any phone to call our 24/7 automated system. Ideal for when you're on the go.
              </p>
              <div className="phone-number-box">1-800-555-0199</div>
            </div>
          </div>
        </div>
        
        {/* Option 2: Web Voice Chat */}
        <div className="col-md-5">
          <div className="card h-100 shadow-sm option-card">
            <div className="card-body">
              <WebchatIcon />
              <h4 className="card-title">Start Web Voice Chat</h4>
              <p className="card-text">
                Speak directly through your browser. Requires a working microphone.
              </p>
              <button className="btn btn-primary btn-lg" onClick={handleStartWebVoiceChat}>
                Start Voice Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      <Link to="/dashboard" className="btn btn-link mt-5">← Go Back to Dashboard</Link>
    </div>
  );
};

export default LodgeVoicePage;
