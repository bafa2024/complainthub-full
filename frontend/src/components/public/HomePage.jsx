import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css'; // We will create this new CSS file next

const HomePage = () => {
  return (
    <div className="homepage-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Your Voice, Amplified.</h1>
          <p className="hero-subtitle">
            The modern platform for resolving customer complaints with brands, powered by AI.
          </p>
          <div className="hero-cta-buttons">
            <Link to="/new-complaint" className="btn btn-primary btn-lg">
              Lodge a Complaint
            </Link>
            <Link to="/complaints" className="btn btn-outline btn-lg">
              View Public Complaints
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>A Better Way to Be Heard</h2>
          <p>Our platform ensures your issues are documented, seen, and resolved.</p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <h3>AI-Powered Bot</h3>
            <p>Our intelligent voice and chatbot captures your complaint details accurately, 24/7.</p>
          </div>
          <div className="feature-card">
            <h3>Public Visibility</h3>
            <p>Unresolved complaints are made public to encourage brands to respond quickly.</p>
          </div>
          <div className="feature-card">
            <h3>Multi-Channel Support</h3>
            <p>Lodge your complaint via Phone Call, WhatsApp, Telegram, and more.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;