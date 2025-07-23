import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './NewComplaintForm.css';

export default function NewComplaintForm() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    brandName: '',
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    isAnonymous: false
  });
  
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [ticketNumber, setTicketNumber] = useState('');
  const [brands, setBrands] = useState([]);

  const categories = [
    'Product Quality',
    'Customer Service',
    'Delivery Issues',
    'Billing Issues',
    'Order Issues',
    'Technical Problems',
    'Refund Issues',
    'Other'
  ];

  const priorities = [
    { value: 'low', label: 'Low', color: '#28a745' },
    { value: 'medium', label: 'Medium', color: '#ffc107' },
    { value: 'high', label: 'High', color: '#fd7e14' },
    { value: 'critical', label: 'Critical', color: '#dc3545' }
  ];

  useEffect(() => {
    // Fetch brands from backend API
    fetch('http://localhost:8001/api/v1/public/brands')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setBrands(data.map(b => b.name));
        } else {
          setBrands(['Other']);
        }
      })
      .catch(() => setBrands(['Other']));
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    if (!formData.fullName.trim()) {
      setError('Full name is required');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!formData.brandName.trim()) {
      setError('Brand name is required');
      return false;
    }
    if (!formData.title.trim()) {
      setError('Complaint title is required');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return false;
    }
    if (!formData.category) {
      setError('Please select a category');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      // Create a public ticket without authentication
      const response = await fetch('http://localhost:8001/api/v1/public/tickets', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          status: 'open',
          created_at: new Date().toISOString()
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create complaint');
      }

      const result = await response.json();
      setTicketNumber(result.ticket_number);
      setSuccess(true);
      setFormData({
        fullName: '',
        email: '',
        phone: '',
        brandName: '',
        title: '',
        description: '',
        category: '',
        priority: 'medium',
        isAnonymous: false
      });
    } catch (err) {
      setError(err.message || 'An error occurred while creating your complaint');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="new-complaint-container">
        <div className="success-message">
          <div className="success-icon">✅</div>
          <h2>Complaint Submitted Successfully!</h2>
          <p>Your complaint has been received and will be reviewed by our team.</p>
          
          <div className="ticket-info">
            <h3>Ticket Information</h3>
            <p><strong>Ticket Number:</strong> {ticketNumber}</p>
            <p><strong>Status:</strong> <span className="status-open">Open</span></p>
            <p><strong>Submitted:</strong> {new Date().toLocaleString()}</p>
          </div>

          <div className="next-steps">
            <h3>What happens next?</h3>
            <ul>
              <li>You'll receive a confirmation email shortly</li>
              <li>Our team will review your complaint within 24-48 hours</li>
              <li>You can track your complaint using the ticket number above</li>
              <li>We'll keep you updated on any progress</li>
            </ul>
          </div>

          <div className="action-buttons">
            <Link to="/track-complaint" className="btn btn-primary">
              Track My Complaint
            </Link>
            <button 
              onClick={() => setSuccess(false)} 
              className="btn btn-secondary"
            >
              Submit Another Complaint
            </button>
            <Link to="/" className="btn btn-outline">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="new-complaint-container">
      <div className="form-header">
        <h1>Submit a New Complaint</h1>
        <p>Help improve services by reporting issues and sharing your experience</p>
      </div>

      <div className="form-container">
        <form onSubmit={handleSubmit} className="complaint-form">
          {error && (
            <div className="error-message">
              <span>⚠️</span> {error}
            </div>
          )}

          <div className="form-section">
            <h3>Personal Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="fullName">Full Name *</label>
                <input
                  type="text"
                  id="fullName"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleInputChange}
                  placeholder="Enter your full name"
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email address"
                  required
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone">Phone Number (Optional)</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="Enter your phone number"
                />
              </div>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="isAnonymous"
                    checked={formData.isAnonymous}
                    onChange={handleInputChange}
                  />
                  <span className="checkmark"></span>
                  Submit anonymously
                </label>
                <small>Your name will be hidden from public view</small>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Complaint Details</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="brandName">Brand/Company Name *</label>
                <select
                  id="brandName"
                  name="brandName"
                  value={formData.brandName}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a brand or enter custom</option>
                  {brands.map(brand => (
                    <option key={brand} value={brand}>{brand}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select a category</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="title">Complaint Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Brief summary of your complaint"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Detailed Description *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Please provide detailed information about your complaint, including dates, times, and any relevant details..."
                rows="6"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="priority">Priority Level</label>
              <div className="priority-options">
                {priorities.map(priority => (
                  <label key={priority.value} className="priority-option">
                    <input
                      type="radio"
                      name="priority"
                      value={priority.value}
                      checked={formData.priority === priority.value}
                      onChange={handleInputChange}
                    />
                    <span 
                      className="priority-label"
                      style={{ borderColor: priority.color }}
                    >
                      {priority.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="btn btn-primary submit-btn"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Submit Complaint'}
            </button>
            <Link to="/" className="btn btn-outline">
              Cancel
            </Link>
          </div>
        </form>

        <div className="form-sidebar">
          <div className="info-card">
            <h3>📋 Before You Submit</h3>
            <ul>
              <li>Provide accurate and detailed information</li>
              <li>Include relevant dates and times</li>
              <li>Be specific about the issue</li>
              <li>Include any reference numbers</li>
            </ul>
          </div>

          <div className="info-card">
            <h3>🔒 Privacy & Security</h3>
            <ul>
              <li>Your personal information is protected</li>
              <li>We never share your details with third parties</li>
              <li>You can submit anonymously if preferred</li>
              <li>All complaints are reviewed by our team</li>
            </ul>
          </div>

          <div className="info-card">
            <h3>📞 Need Help?</h3>
            <p>If you need assistance or have questions about submitting a complaint, please contact our support team.</p>
            <Link to="/contact" className="btn btn-small">
              Contact Support
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 