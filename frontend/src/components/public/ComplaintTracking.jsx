import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './ComplaintTracking.css';

export default function ComplaintTracking() {
  const [ticketNumber, setTicketNumber] = useState('');
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Mock complaint data
  const mockComplaint = {
    id: 'COMP-2024-001247',
    title: 'Mobile App Login Issues',
    description: 'Unable to log into the mobile application. Getting error message "Invalid credentials" even with correct username and password.',
    status: 'in-progress',
    priority: 'medium',
    category: 'Technical Issues',
    brand: 'TechCorp Solutions',
    customer: 'John Smith',
    email: 'john.smith@email.com',
    phone: '+1 (555) 123-4567',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-16T14:20:00Z',
    estimatedResolution: '2024-01-18T17:00:00Z',
    timeline: [
      {
        id: 1,
        status: 'created',
        title: 'Complaint Submitted',
        description: 'Your complaint has been successfully submitted and is being reviewed.',
        timestamp: '2024-01-15T10:30:00Z',
        icon: '📝'
      },
      {
        id: 2,
        status: 'assigned',
        title: 'Assigned to Support Team',
        description: 'Your complaint has been assigned to our technical support team for investigation.',
        timestamp: '2024-01-15T11:15:00Z',
        icon: '👥'
      },
      {
        id: 3,
        status: 'in-progress',
        title: 'Under Investigation',
        description: 'Our team is currently investigating the login issue. We have identified a potential server-side problem.',
        timestamp: '2024-01-16T09:00:00Z',
        icon: '🔍'
      },
      {
        id: 4,
        status: 'update',
        title: 'Update Provided',
        description: 'We have identified the issue and are working on a fix. Expected resolution within 48 hours.',
        timestamp: '2024-01-16T14:20:00Z',
        icon: '📢'
      }
    ],
    messages: [
      {
        id: 1,
        sender: 'customer',
        message: 'I\'ve been trying to log in for the past 2 days but keep getting an error. Can you help?',
        timestamp: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        sender: 'support',
        message: 'Thank you for reporting this issue. We are investigating the login problem and will provide an update soon.',
        timestamp: '2024-01-15T11:15:00Z'
      },
      {
        id: 3,
        sender: 'support',
        message: 'We have identified the issue with our authentication server. Our development team is working on a fix. We apologize for the inconvenience.',
        timestamp: '2024-01-16T14:20:00Z'
      }
    ]
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!ticketNumber.trim()) {
      setError('Please enter a ticket number');
      return;
    }

    setLoading(true);
    setError('');
    setComplaint(null);

    // Simulate API call
    setTimeout(() => {
      if (ticketNumber.toUpperCase() === 'COMP-2024-001247') {
        setComplaint(mockComplaint);
      } else {
        setError('No complaint found with this ticket number. Please check the number and try again.');
      }
      setLoading(false);
    }, 1000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'resolved': return '#27ae60';
      case 'in-progress': return '#f39c12';
      case 'pending': return '#95a5a6';
      case 'urgent': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'resolved': return 'Resolved';
      case 'in-progress': return 'In Progress';
      case 'pending': return 'Pending';
      case 'urgent': return 'Urgent';
      default: return 'Unknown';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="complaint-tracking">
      {/* Header */}
      <header className="tracking-header">
        <div className="header-container">
          <div className="logo">
            <Link to="/">ComplaintHub</Link>
          </div>
          <div className="header-nav">
            <Link to="/" className="btn btn-primary">Home</Link>
            <Link to="/complaints" className="btn btn-secondary">View Complaints</Link>
          </div>
        </div>
      </header>

      <div className="main-container">
        {/* Search Section */}
        <div className="search-section">
          <h1 className="search-title">Track Your Complaint</h1>
          <p className="search-subtitle">
            Enter your ticket number to check the status and updates of your complaint
          </p>
          
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              className="search-input"
              placeholder="Enter ticket number (e.g., COMP-2024-001247)"
              value={ticketNumber}
              onChange={(e) => setTicketNumber(e.target.value)}
            />
            <button type="submit" className="search-btn" disabled={loading}>
              {loading ? 'Searching...' : 'Track Complaint'}
            </button>
          </form>

          {error && (
            <div className="alert alert-danger">
              {error}
            </div>
          )}
        </div>

        {/* Complaint Details */}
        {complaint && (
          <div className="complaint-container show">
            {/* Complaint Header */}
            <div className="complaint-header">
              <div className="ticket-number">{complaint.id}</div>
              <div className="complaint-meta">
                <span>Status: <strong>{getStatusText(complaint.status)}</strong></span>
                <span>Priority: <strong>{complaint.priority}</strong></span>
                <span>Category: <strong>{complaint.category}</strong></span>
              </div>
            </div>

            {/* Complaint Info */}
            <div className="complaint-info">
              <div className="info-grid">
                <div className="info-item">
                  <label>Title</label>
                  <div>{complaint.title}</div>
                </div>
                <div className="info-item">
                  <label>Description</label>
                  <div>{complaint.description}</div>
                </div>
                <div className="info-item">
                  <label>Brand</label>
                  <div>{complaint.brand}</div>
                </div>
                <div className="info-item">
                  <label>Customer</label>
                  <div>{complaint.customer}</div>
                </div>
                <div className="info-item">
                  <label>Submitted</label>
                  <div>{formatDate(complaint.createdAt)}</div>
                </div>
                <div className="info-item">
                  <label>Last Updated</label>
                  <div>{formatDate(complaint.updatedAt)}</div>
                </div>
                <div className="info-item">
                  <label>Estimated Resolution</label>
                  <div>{formatDate(complaint.estimatedResolution)}</div>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="timeline-section">
              <h3>Complaint Timeline</h3>
              <div className="timeline">
                {complaint.timeline.map((event, index) => (
                  <div key={event.id} className={`timeline-item ${event.status}`}>
                    <div className="timeline-icon">
                      <span>{event.icon}</span>
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-title">{event.title}</div>
                      <div className="timeline-description">{event.description}</div>
                      <div className="timeline-time">{formatDate(event.timestamp)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Messages */}
            <div className="messages-section">
              <h3>Communication History</h3>
              <div className="messages-list">
                {complaint.messages.map((message) => (
                  <div key={message.id} className={`message-item ${message.sender}`}>
                    <div className="message-header">
                      <span className="message-sender">
                        {message.sender === 'customer' ? 'You' : complaint.brand}
                      </span>
                      <span className="message-time">{formatDate(message.timestamp)}</span>
                    </div>
                    <div className="message-content">{message.message}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="complaint-actions">
              <Link to="/new-complaint" className="btn btn-primary">
                Submit New Complaint
              </Link>
              <Link to="/complaints" className="btn btn-secondary">
                View All Complaints
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 