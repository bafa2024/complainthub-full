import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './UserComplaintDetail.css';

export default function UserComplaintDetail() {
  const { id } = useParams();
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('details');

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setComplaint({
        id: id,
        ticketNumber: `TKT-${id.padStart(6, '0')}`,
        status: 'in-progress',
        priority: 'medium',
        category: 'Product Quality',
        brand: 'TechCorp',
        brandLogo: 'TC',
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-16T14:20:00Z',
        subject: 'Defective smartphone received',
        description: 'I received a smartphone that has several issues including a cracked screen, non-functional camera, and battery that drains within 2 hours. The device was purchased brand new and should be in perfect condition.',
        audioUrl: '/audio/complaint-recording.mp3',
        attachments: [
          { name: 'phone_damage.jpg', type: 'image', size: '2.3 MB' },
          { name: 'receipt.pdf', type: 'document', size: '1.1 MB' }
        ],
        responses: [
          {
            id: 1,
            from: 'TechCorp Support',
            message: 'Thank you for bringing this to our attention. We sincerely apologize for the inconvenience. Our team is reviewing your complaint and will get back to you within 24 hours.',
            timestamp: '2024-01-15T11:00:00Z',
            type: 'brand'
          },
          {
            id: 2,
            from: 'You',
            message: 'Thank you for the quick response. I have attached photos of the damage and the original receipt for your reference.',
            timestamp: '2024-01-15T14:30:00Z',
            type: 'user'
          }
        ],
        timeline: [
          {
            date: '2024-01-15',
            events: [
              { time: '10:30 AM', action: 'Complaint submitted', status: 'completed' },
              { time: '11:00 AM', action: 'Brand notified', status: 'completed' },
              { time: '11:05 AM', action: 'Brand acknowledged', status: 'completed' }
            ]
          },
          {
            date: '2024-01-16',
            events: [
              { time: '09:00 AM', action: 'Under investigation', status: 'completed' },
              { time: '02:20 PM', action: 'Resolution in progress', status: 'current' }
            ]
          }
        ]
      });
      setLoading(false);
    }, 1000);
  }, [id]);

  const getStatusColor = (status) => {
    const statusColors = {
      'new': 'status-new',
      'in-progress': 'status-in-progress',
      'resolved': 'status-resolved',
      'reopened': 'status-reopened'
    };
    return statusColors[status] || 'status-new';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="complaint-detail-loading">
        <div className="loading-spinner"></div>
        <p>Loading complaint details...</p>
      </div>
    );
  }

  if (!complaint) {
    return (
      <div className="complaint-detail-error">
        <h2>Complaint Not Found</h2>
        <p>The complaint you're looking for doesn't exist or has been removed.</p>
        <Link to="/dashboard" className="btn btn-primary">Back to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="complaint-detail-page">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <Link to="/" className="logo">ComplaintHub</Link>
          <div className="user-menu">
            <div className="notification-bell">
              🔔
              <span className="notification-badge">3</span>
            </div>
            <div className="user-avatar">👤</div>
          </div>
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="breadcrumb">
        <Link to="/dashboard">Dashboard</Link> &gt; 
        <Link to="/my-complaints">My Complaints</Link> &gt; 
        <span>Complaint #{complaint.ticketNumber}</span>
      </div>

      <div className="container">
        {/* Complaint Header */}
        <div className="complaint-header">
          <div className="ticket-info">
            <div>
              <div className="ticket-id">{complaint.ticketNumber}</div>
              <div className="ticket-meta">
                <span>Created: {formatDate(complaint.createdAt)}</span>
                <span>Updated: {formatDate(complaint.updatedAt)}</span>
                <span>Priority: {complaint.priority}</span>
              </div>
            </div>
            <div className={`status-badge ${getStatusColor(complaint.status)}`}>
              {complaint.status.replace('-', ' ').toUpperCase()}
            </div>
          </div>

          <div className="brand-section">
            <div className="brand-logo">{complaint.brandLogo}</div>
            <div>
              <div className="brand-name">{complaint.brand}</div>
              <div className="brand-category">{complaint.category}</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'details' ? 'active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Details
          </button>
          <button 
            className={`tab ${activeTab === 'responses' ? 'active' : ''}`}
            onClick={() => setActiveTab('responses')}
          >
            Responses ({complaint.responses.length})
          </button>
          <button 
            className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
            onClick={() => setActiveTab('timeline')}
          >
            Timeline
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'details' && (
            <div className="content-section">
              <h3 className="section-title">Complaint Details</h3>
              <div className="complaint-text">
                <h4>{complaint.subject}</h4>
                <p>{complaint.description}</p>
              </div>

              {complaint.audioUrl && (
                <div className="audio-section">
                  <h4>Voice Recording</h4>
                  <div className="audio-player">
                    <audio controls>
                      <source src={complaint.audioUrl} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                </div>
              )}

              {complaint.attachments.length > 0 && (
                <div className="attachments-section">
                  <h4>Attachments</h4>
                  <div className="attachments-list">
                    {complaint.attachments.map((file, index) => (
                      <div key={index} className="attachment-item">
                        <span className="attachment-icon">
                          {file.type === 'image' ? '🖼️' : '📄'}
                        </span>
                        <div className="attachment-info">
                          <div className="attachment-name">{file.name}</div>
                          <div className="attachment-size">{file.size}</div>
                        </div>
                        <button className="btn btn-outline">Download</button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'responses' && (
            <div className="responses-section">
              <div className="responses-list">
                {complaint.responses.map((response) => (
                  <div key={response.id} className={`response-item ${response.type}`}>
                    <div className="response-header">
                      <div className="response-author">{response.from}</div>
                      <div className="response-time">{formatDate(response.timestamp)}</div>
                    </div>
                    <div className="response-message">{response.message}</div>
                  </div>
                ))}
              </div>
              
              <div className="add-response">
                <h4>Add Response</h4>
                <textarea 
                  placeholder="Type your response..."
                  className="response-input"
                ></textarea>
                <button className="btn btn-primary">Send Response</button>
              </div>
            </div>
          )}

          {activeTab === 'timeline' && (
            <div className="timeline-section">
              <div className="timeline">
                {complaint.timeline.map((day, dayIndex) => (
                  <div key={dayIndex} className="timeline-day">
                    <div className="timeline-date">{day.date}</div>
                    <div className="timeline-events">
                      {day.events.map((event, eventIndex) => (
                        <div key={eventIndex} className={`timeline-event ${event.status}`}>
                          <div className="event-time">{event.time}</div>
                          <div className="event-action">{event.action}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="action-buttons">
          <button className="btn btn-outline">Download Report</button>
          <button className="btn btn-primary">Update Complaint</button>
          <button className="btn btn-danger">Close Complaint</button>
        </div>
      </div>
    </div>
  );
} 