import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Handle scroll effect
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close menu on route change
  useEffect(() => {
    setIsMenuOpen(false);
  }, [location]);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className={`header-wrapper ${isScrolled ? 'scrolled' : ''}`}>
        <div className="container">
        <nav className="navbar">
          {/* Logo */}
          <Link to={isAuthenticated && user?.role === 'user' ? "/dashboard" : "/"} className="logo" onClick={closeMenu}>
            <span className="logo-text">ComplaintHub</span>
          </Link>
          
          {/* Mobile Menu Toggle */}
          <button 
            className={`menu-toggle ${isMenuOpen ? 'active' : ''}`}
            onClick={toggleMenu}
            aria-label="Toggle menu"
          >
              <span></span>
              <span></span>
              <span></span>
          </button>
          
          {/* Navigation Wrapper */}
          <div className={`nav-wrapper ${isMenuOpen ? 'active' : ''}`}> 
            <ul className="nav-menu">
              {/* Landing navigation if not logged in */}
              {!isAuthenticated || user?.role !== 'user' ? (
                <>
                  <li className="nav-item">
                    <Link 
                      to="/" 
                      className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Home
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/complaints" 
                      className={`nav-link ${location.pathname.startsWith('/complaints') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Public Complaints
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/track-complaint" 
                      className={`nav-link ${location.pathname.startsWith('/track-complaint') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Track Complaint
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/help" 
                      className={`nav-link ${location.pathname.startsWith('/help') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Help Center
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/contact" 
                      className={`nav-link ${location.pathname.startsWith('/contact') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Contact
                    </Link>
                  </li>
                </>
              ) : (
                // Dashboard navigation for logged-in user
                <>
                  <li className="nav-item">
                    <Link 
                      to="/dashboard" 
                      className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Dashboard
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/my-complaints" 
                      className={`nav-link ${location.pathname.startsWith('/my-complaints') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      My Complaints
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/new-complaint" 
                      className={`nav-link ${location.pathname.startsWith('/new-complaint') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      New Complaint
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link 
                      to="/profile" 
                      className={`nav-link ${location.pathname.startsWith('/profile') ? 'active' : ''}`}
                      onClick={closeMenu}
                    >
                      Profile
                    </Link>
                  </li>
                </>
              )}
            </ul>

            {/* Auth Section */}
            <div className="auth-section">
              {!isAuthenticated ? (
                <>
                  <Link 
                    to="/login" 
                    className="auth-link login-link"
                    onClick={closeMenu}
                  >
                    Customer Login
                  </Link>
                  <Link 
                    to="/brand/login" 
                    className="auth-link brand-login-link"
                    onClick={closeMenu}
                  >
                    Brand Login
                  </Link>
                  <Link 
                    to="/signup" 
                    className="auth-link signup-link primary-btn"
                    onClick={closeMenu}
                  >
                    Sign Up
                  </Link>
                </>
              ) : user?.role === 'user' ? (
                <div className="user-menu">
                  <span className="user-name">Hi, {user?.full_name || user?.name || 'User'}</span>
                  <button 
                    className="logout-btn"
                    onClick={() => {
                      logout();
                      closeMenu();
                    }}
                  >
                    Logout
                  </button>
                </div>
              ) : (
                // For other roles, fallback to landing auth links
                <>
                  <Link 
                    to="/login" 
                    className="auth-link login-link"
                    onClick={closeMenu}
                  >
                    Customer Login
                  </Link>
                  <Link 
                    to="/brand/login" 
                    className="auth-link brand-login-link"
                    onClick={closeMenu}
                  >
                    Brand Login
                  </Link>
                  <Link 
                    to="/signup" 
                    className="auth-link signup-link primary-btn"
                    onClick={closeMenu}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </nav>
        </div>
    </header>
  );
};

export default Header;