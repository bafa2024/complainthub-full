// Create this file at: frontend/src/components/user/LodgeVoicePage.jsx

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './LodgeVoicePage.css'; // We will create this CSS file next
import LoadingSpinner from '../shared/LoadingSpinner';

// SVG Icons for the option cards
const PhoneIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" className="bi bi-telephone-outbound-fill mb-3" viewBox="0 0 16 16">
    <path fillRule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.28 1.465l-2.138 2.138a.64.64 0 0 0 .045.901l6.206 6.207a.64.64 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5"/>
  </svg>
);

const LodgeVoicePage = () => {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    // No need to fetch brands since we only show the hotline option
  }, []);

  if (loading) {
    return (
      <div className="container lodge-voice-container text-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="container lodge-voice-container text-center">
      <h1 className="display-5 fw-bold mb-3">Lodge a Complaint or Suggestion Using Your Voice</h1>
      <p className="lead mb-5">Call our 24/7 automated system to speak with our AI assistant.</p>
      
      <div className="row g-4 justify-content-center">
        {/* Phone Call Option */}
        <div className="col-md-6">
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
      </div>

      <Link to="/dashboard" className="btn btn-link mt-5">← Go Back to Dashboard</Link>
    </div>
  );
};

export default LodgeVoicePage;
