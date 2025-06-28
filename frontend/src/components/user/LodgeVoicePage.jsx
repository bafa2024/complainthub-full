// Create this file at: frontend/src/components/user/LodgeVoicePage.jsx

import React from 'react';
import { Link } from 'react-router-dom';
import './LodgeVoicePage.css'; // We will create this CSS file next

// SVG Icons for the option cards
const PhoneIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-telephone-outbound-fill mb-3" viewBox="0 0 16 16">
    <path fillRule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.28 1.465l-2.138 2.138a.64.64 0 0 0 .045.901l6.206 6.207a.64.64 0 0 0 .901.045l2.138-2.138c.49-.164 1.042-.048 1.465.28l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.6 18.6 0 0 1-7.01-4.42 18.6 18.6 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877zM11 .5a.5.5 0 0 1 .5.5V4a.5.5 0 0 1-1 0V1.707l-4.146 4.147a.5.5 0 0 1-.708-.708L9.293 1H6.5a.5.5 0 0 1 0-1z"/>
  </svg>
);
const WebchatIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-mic-fill mb-3" viewBox="0 0 16 16">
        <path d="M5 3a3 3 0 0 1 6 0v5a3 3 0 0 1-6 0z"/><path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5"/>
    </svg>
);


const LodgeVoicePage = () => {
  const handleStartWebVoiceChat = () => {
    alert("Real-time web voice chat functionality is coming soon!");
  };

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
