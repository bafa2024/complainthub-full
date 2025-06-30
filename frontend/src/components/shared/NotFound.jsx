import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // In a real app, this would search the site
      navigate('/complaints');
    }
  };

  const helpfulLinks = [
    {
      icon: '🏠',
      title: 'Home',
      description: 'Return to the main page',
      link: '/'
    },
    {
      icon: '📝',
      title: 'Lodge Complaint',
      description: 'Submit a new complaint',
      link: '/new-complaint'
    },
    {
      icon: '🔍',
      title: 'Track Complaint',
      description: 'Check your complaint status',
      link: '/track-complaint'
    },
    {
      icon: '📋',
      title: 'View Complaints',
      description: 'Browse public complaints',
      link: '/complaints'
    },
    {
      icon: '📞',
      title: 'Contact Support',
      description: 'Get help from our team',
      link: '/contact'
    },
    {
      icon: '❓',
      title: 'Help Center',
      description: 'Find answers to questions',
      link: '/help'
    }
  ];

  return (
    <div className="not-found-page">
      <div className="error-container">
        <div className="error-code">404</div>
        <div className="error-illustration">🔍</div>
        <h1 className="error-title">Page Not Found</h1>
        <p className="error-message">
          Oops! The page you're looking for doesn't exist. It might have been moved, 
          deleted, or you entered the wrong URL. Let's get you back on track.
        </p>

        <div className="action-buttons">
          <Link to="/" className="btn btn-primary">
            Go Home
          </Link>
          <Link to="/complaints" className="btn btn-outline">
            Browse Complaints
          </Link>
        </div>

        <div className="search-container">
          <p>Looking for something specific?</p>
          <form onSubmit={handleSearch} className="search-bar">
            <input
              type="text"
              className="search-input"
              placeholder="Search complaints, brands, or topics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button type="submit" className="btn btn-primary">
              Search
            </button>
          </form>
        </div>

        <div className="helpful-links">
          <h3 className="links-title">Helpful Links</h3>
          <div className="links-grid">
            {helpfulLinks.map((link, index) => (
              <Link key={index} to={link.link} className="link-item">
                <div className="link-icon">{link.icon}</div>
                <div className="link-title">{link.title}</div>
                <div className="link-description">{link.description}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 