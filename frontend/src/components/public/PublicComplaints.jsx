// frontend/src/components/public/PublicComplaints.jsx

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './PublicComplaints.css';

export default function PublicComplaints() {
  const [complaints, setComplaints] = useState([]);
  const [filteredComplaints, setFilteredComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    brand: '',
    category: '',
    status: '',
    dateRange: 'all',
    searchQuery: ''
  });
  const [sortBy, setSortBy] = useState('date');
  const [viewMode, setViewMode] = useState('grid'); // grid or list

  useEffect(() => {
    // Simulate API call for public complaints
    setTimeout(() => {
      const mockComplaints = [
        {
          id: 1,
          ticketNumber: 'TKT-000001',
          title: 'Defective smartphone received with cracked screen',
          description: 'I received a smartphone that has several issues including a cracked screen, non-functional camera, and battery that drains within 2 hours.',
          brand: 'TechCorp',
          category: 'Product Quality',
          status: 'unresolved',
          urgency: 'high',
          createdAt: '2024-01-15T10:30:00Z',
          daysOpen: 5,
          userAlias: 'Anonymous',
          hasVoiceRecording: true,
          voiceUrl: '/audio/complaint-1.mp3',
          upvotes: 12,
          comments: 3,
          isAnonymous: true
        },
        {
          id: 2,
          ticketNumber: 'TKT-000002',
          title: 'Wrong order delivered - received different product',
          description: 'Ordered a specific model but received a completely different product. Customer service was unhelpful.',
          brand: 'FoodExpress',
          category: 'Order Issues',
          status: 'in-progress',
          urgency: 'medium',
          createdAt: '2024-01-12T14:20:00Z',
          daysOpen: 8,
          userAlias: 'John D.',
          hasVoiceRecording: false,
          upvotes: 8,
          comments: 1,
          isAnonymous: false
        },
        {
          id: 3,
          ticketNumber: 'TKT-000003',
          title: 'Poor customer service and rude staff',
          description: 'Extremely disappointed with the customer service. Staff was rude and unprofessional.',
          brand: 'FashionHub',
          category: 'Customer Service',
          status: 'unresolved',
          urgency: 'high',
          createdAt: '2024-01-10T09:15:00Z',
          daysOpen: 10,
          userAlias: 'Sarah M.',
          hasVoiceRecording: true,
          voiceUrl: '/audio/complaint-3.mp3',
          upvotes: 25,
          comments: 7,
          isAnonymous: false
        },
        {
          id: 4,
          ticketNumber: 'TKT-000004',
          title: 'Delayed delivery - package lost in transit',
          description: 'Package was supposed to arrive 3 days ago but still not delivered. Tracking shows lost in transit.',
          brand: 'HomeGoods',
          category: 'Delivery Issues',
          status: 'resolved',
          urgency: 'medium',
          createdAt: '2024-01-08T16:45:00Z',
          daysOpen: 12,
          userAlias: 'Anonymous',
          hasVoiceRecording: false,
          upvotes: 15,
          comments: 4,
          isAnonymous: true
        }
      ];
      setComplaints(mockComplaints);
      setFilteredComplaints(mockComplaints);
      setLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    // Apply filters
    let filtered = complaints.filter(complaint => {
      const matchesBrand = !filters.brand || complaint.brand.toLowerCase().includes(filters.brand.toLowerCase());
      const matchesCategory = !filters.category || complaint.category === filters.category;
      const matchesStatus = !filters.status || complaint.status === filters.status;
      const matchesSearch = !filters.searchQuery || 
        complaint.title.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
        complaint.description.toLowerCase().includes(filters.searchQuery.toLowerCase()) ||
        complaint.brand.toLowerCase().includes(filters.searchQuery.toLowerCase());

      // Date range filtering
      let matchesDate = true;
      if (filters.dateRange !== 'all') {
        const complaintDate = new Date(complaint.createdAt);
        const now = new Date();
        const daysDiff = Math.floor((now - complaintDate) / (1000 * 60 * 60 * 24));
        
        switch (filters.dateRange) {
          case 'today':
            matchesDate = daysDiff === 0;
            break;
          case 'week':
            matchesDate = daysDiff <= 7;
            break;
          case 'month':
            matchesDate = daysDiff <= 30;
            break;
          default:
            matchesDate = true;
        }
      }

      return matchesBrand && matchesCategory && matchesStatus && matchesSearch && matchesDate;
    });

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'urgency':
          const urgencyOrder = { high: 3, medium: 2, low: 1 };
          return urgencyOrder[b.urgency] - urgencyOrder[a.urgency];
        case 'upvotes':
          return b.upvotes - a.upvotes;
        case 'daysOpen':
          return b.daysOpen - a.daysOpen;
        default:
          return 0;
      }
    });

    setFilteredComplaints(filtered);
  }, [complaints, filters, sortBy]);

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
  };

  const handleUpvote = (complaintId) => {
    setComplaints(prev => prev.map(complaint => 
      complaint.id === complaintId 
        ? { ...complaint, upvotes: complaint.upvotes + 1 }
        : complaint
    ));
  };

  const handleShare = (complaint) => {
    const shareText = `Check out this complaint about ${complaint.brand}: ${complaint.title}`;
    const shareUrl = `${window.location.origin}/complaint/${complaint.id}`;
    
    if (navigator.share) {
      navigator.share({
        title: `Complaint about ${complaint.brand}`,
        text: shareText,
        url: shareUrl
      });
    } else {
      // Fallback to copying to clipboard
      navigator.clipboard.writeText(`${shareText}\n${shareUrl}`);
      alert('Link copied to clipboard!');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'unresolved': 'status-unresolved',
      'in-progress': 'status-progress',
      'resolved': 'status-resolved'
    };
    return colors[status] || 'status-unresolved';
  };

  const getUrgencyColor = (urgency) => {
    const colors = {
      'high': 'urgency-high',
      'medium': 'urgency-medium',
      'low': 'urgency-low'
    };
    return colors[urgency] || 'urgency-medium';
  };

  const brands = [...new Set(complaints.map(c => c.brand))];
  const categories = [...new Set(complaints.map(c => c.category))];

  if (loading) {
    return (
      <div className="public-complaints-loading">
        <div className="loading-spinner"></div>
        <p>Loading complaints...</p>
      </div>
    );
  }

  return (
    <div className="public-complaints-page">
      {/* SEO-optimized header */}
      <div className="complaints-header">
        <div className="header-content">
          <h1>Public Complaints & Reviews</h1>
          <p>Browse and track customer complaints across various brands. Hold companies accountable for their service quality.</p>
          <div className="header-stats">
            <div className="stat">
              <span className="stat-number">{complaints.length}</span>
              <span className="stat-label">Total Complaints</span>
            </div>
            <div className="stat">
              <span className="stat-number">{complaints.filter(c => c.status === 'unresolved').length}</span>
              <span className="stat-label">Unresolved</span>
            </div>
            <div className="stat">
              <span className="stat-number">{brands.length}</span>
              <span className="stat-label">Brands</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="filters-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search complaints, brands, or issues..."
            value={filters.searchQuery}
            onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
            className="search-input"
          />
          <button className="search-btn">🔍</button>
        </div>

        <div className="filter-controls">
          <div className="filter-group">
            <select 
              value={filters.brand} 
              onChange={(e) => handleFilterChange('brand', e.target.value)}
              className="filter-select"
            >
              <option value="">All Brands</option>
              {brands.map(brand => (
                <option key={brand} value={brand}>{brand}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <select 
              value={filters.category} 
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="filter-select"
            >
              <option value="">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <select 
              value={filters.status} 
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="filter-select"
            >
              <option value="">All Status</option>
              <option value="unresolved">Unresolved</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>

          <div className="filter-group">
            <select 
              value={filters.dateRange} 
              onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              className="filter-select"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>

          <div className="filter-group">
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="filter-select"
            >
              <option value="date">Sort by Date</option>
              <option value="urgency">Sort by Urgency</option>
              <option value="upvotes">Sort by Popularity</option>
              <option value="daysOpen">Sort by Days Open</option>
            </select>
          </div>

          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              📊
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              📋
            </button>
          </div>
        </div>
      </div>

      {/* Complaints List */}
      <div className="complaints-container">
        {filteredComplaints.length === 0 ? (
          <div className="no-complaints">
            <div className="no-complaints-icon">🔍</div>
            <h3>No complaints found</h3>
            <p>Try adjusting your filters or search terms.</p>
          </div>
        ) : (
          <div className={`complaints-grid ${viewMode}`}>
            {filteredComplaints.map((complaint) => (
              <div key={complaint.id} className="complaint-card">
                <div className="complaint-header">
                  <div className="complaint-meta">
                    <span className={`status-badge ${getStatusColor(complaint.status)}`}>
                      {complaint.status.replace('-', ' ')}
                    </span>
                    <span className={`urgency-badge ${getUrgencyColor(complaint.urgency)}`}>
                      {complaint.urgency}
                    </span>
                  </div>
                  <div className="complaint-actions">
                    <button 
                      className="action-btn upvote-btn"
                      onClick={() => handleUpvote(complaint.id)}
                    >
                      👍 {complaint.upvotes}
                    </button>
                    <button 
                      className="action-btn share-btn"
                      onClick={() => handleShare(complaint)}
                    >
                      📤 Share
                    </button>
                  </div>
                </div>

                <div className="complaint-content">
                  <h3 className="complaint-title">
                    <Link to={`/complaint/${complaint.id}`}>
                      {complaint.title}
                    </Link>
                  </h3>
                  <p className="complaint-description">
                    {complaint.description.length > 150 
                      ? `${complaint.description.substring(0, 150)}...` 
                      : complaint.description
                    }
                  </p>
                </div>

                <div className="complaint-details">
                  <div className="brand-info">
                    <span className="brand-name">{complaint.brand}</span>
                    <span className="category">{complaint.category}</span>
                  </div>
                  
                  <div className="complaint-stats">
                    <span className="days-open">
                      {complaint.daysOpen} day{complaint.daysOpen !== 1 ? 's' : ''} open
                    </span>
                    <span className="comments">
                      💬 {complaint.comments}
                    </span>
                  </div>
                </div>

                <div className="complaint-footer">
                  <div className="user-info">
                    <span className="user-alias">
                      {complaint.isAnonymous ? '👤 Anonymous' : `👤 ${complaint.userAlias}`}
                    </span>
                    <span className="complaint-date">{formatDate(complaint.createdAt)}</span>
                  </div>
                  
                  {complaint.hasVoiceRecording && (
                    <div className="voice-indicator">
                      🎤 Voice Recording Available
                    </div>
                  )}
                </div>

                <div className="complaint-actions-bottom">
                  <Link 
                    to={`/complaint/${complaint.id}`} 
                    className="btn btn-primary"
                  >
                    View Details
                  </Link>
                  <Link 
                    to={`/track-complaint?ticket=${complaint.ticketNumber}`} 
                    className="btn btn-outline"
                  >
                    Track Progress
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Call to Action */}
      <div className="cta-section">
        <div className="cta-content">
          <h2>Have a complaint? Make your voice heard!</h2>
          <p>Join thousands of consumers who are holding brands accountable for their service quality.</p>
          <div className="cta-buttons">
            <Link to="/new-complaint" className="btn btn-primary">
              📝 Lodge a Complaint
            </Link>
            <Link to="/voice-complaint" className="btn btn-secondary">
              🎤 Voice Complaint
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}