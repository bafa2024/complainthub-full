import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Header = () => {
  const { isAuthenticated, user, logout, mockupMode } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [isNavExpanded, setIsNavExpanded] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsNavExpanded(false);
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const handleNavToggle = () => {
    setIsNavExpanded(!isNavExpanded);
  };

  const handleNavLinkClick = () => {
    setIsNavExpanded(false);
  };

  const renderAuthLinks = () => {
    if (isAuthenticated || mockupMode) {
      return (
        <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
          <li className="nav-item">
            <span className="navbar-text me-3">
              Welcome, {user?.full_name || user?.email || 'Demo User'}
            </span>
          </li>
          
          {/* Show all role-based links in mockup mode */}
          {mockupMode && (
            <>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  <i className="fas fa-user me-1"></i>User Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/dashboard" className={`dropdown-item ${isActive('/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-home me-2"></i>Dashboard
                  </Link></li>
                  <li><Link to="/settings" className={`dropdown-item ${isActive('/settings') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-cog me-2"></i>Settings
                  </Link></li>
                  <li><Link to="/new-complaint" className={`dropdown-item ${isActive('/new-complaint') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-plus me-2"></i>New Complaint
                  </Link></li>
                  <li><Link to="/lodge-voice" className={`dropdown-item ${isActive('/lodge-voice') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-microphone me-2"></i>Lodge Voice
                  </Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  <i className="fas fa-building me-1"></i>Brand Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/brand/dashboard" className={`dropdown-item ${isActive('/brand/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-tachometer-alt me-2"></i>Dashboard
                  </Link></li>
                  <li><Link to="/brand/billing" className={`dropdown-item ${isActive('/brand/billing') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-credit-card me-2"></i>Billing
                  </Link></li>
                  <li><Link to="/brand/team" className={`dropdown-item ${isActive('/brand/team') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-users me-2"></i>Team
                  </Link></li>
                  <li><Link to="/brand/analytics" className={`dropdown-item ${isActive('/brand/analytics') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-chart-bar me-2"></i>Analytics
                  </Link></li>
                  <li><Link to="/brand/settings" className={`dropdown-item ${isActive('/brand/settings') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-cog me-2"></i>Settings
                  </Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  <i className="fas fa-shield-alt me-1"></i>Admin Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/admin/dashboard" className={`dropdown-item ${isActive('/admin/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-tachometer-alt me-2"></i>Dashboard
                  </Link></li>
                  <li><Link to="/admin/brands" className={`dropdown-item ${isActive('/admin/brands') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-building me-2"></i>Brands
                  </Link></li>
                  <li><Link to="/admin/users" className={`dropdown-item ${isActive('/admin/users') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-users me-2"></i>Users
                  </Link></li>
                  <li><Link to="/admin/complaints" className={`dropdown-item ${isActive('/admin/complaints') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-ticket-alt me-2"></i>Complaints
                  </Link></li>
                  <li><Link to="/admin/reports" className={`dropdown-item ${isActive('/admin/reports') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-chart-line me-2"></i>Reports
                  </Link></li>
                  <li><Link to="/admin/settings" className={`dropdown-item ${isActive('/admin/settings') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-cog me-2"></i>Settings
                  </Link></li>
                  <li><Link to="/admin/billing" className={`dropdown-item ${isActive('/admin/billing') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                    <i className="fas fa-credit-card me-2"></i>Billing
                  </Link></li>
                </ul>
              </li>
            </>
          )}
          
          {/* Show role-specific links in normal mode */}
          {!mockupMode && (
            <>
              {user?.role === 'admin' && (
                <>
                  <li className="nav-item">
                    <Link to="/admin/dashboard" className={`nav-link ${isActive('/admin/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                      <i className="fas fa-tachometer-alt me-1"></i>Admin
                    </Link>
                  </li>
                </>
              )}
              {user?.role === 'brand_user' && (
                <>
                  <li className="nav-item">
                    <Link to="/brand/dashboard" className={`nav-link ${isActive('/brand/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                      <i className="fas fa-building me-1"></i>Brand Dashboard
                    </Link>
                  </li>
                </>
              )}
              {user?.role === 'user' && (
                <>
                  <li className="nav-item">
                    <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                      <i className="fas fa-home me-1"></i>My Dashboard
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/settings" className={`nav-link ${isActive('/settings') ? 'active' : ''}`} onClick={handleNavLinkClick}>
                      <i className="fas fa-cog me-1"></i>Settings
                    </Link>
                  </li>
                </>
              )}
            </>
          )}
          
          <li className="nav-item d-flex align-items-center">
            <button onClick={handleLogout} className="btn btn-danger btn-sm">
              <i className="fas fa-sign-out-alt me-1"></i>Logout
            </button>
          </li>
        </ul>
      );
    } else {
      return (
        <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
          <li className="nav-item d-flex align-items-center">
            <Link to="/login" className={`nav-link ${isActive('/login') ? 'active' : ''}`} onClick={handleNavLinkClick}>
              <i className="fas fa-user me-1"></i>Customer Login
            </Link>
          </li>
          <li className="nav-item d-flex align-items-center">
            <Link to="/brand/login" className={`nav-link ${isActive('/brand/login') ? 'active' : ''}`} onClick={handleNavLinkClick}>
              <i className="fas fa-building me-1"></i>Brand Login
            </Link>
          </li>
          <li className="nav-item d-flex align-items-center">
            <Link to="/signup" className="btn btn-primary" onClick={handleNavLinkClick}>
              <i className="fas fa-user-plus me-1"></i>Sign Up
            </Link>
          </li>
        </ul>
      );
    }
  };

  return (
    <header className="bg-white shadow-sm border-bottom">
      <nav className="navbar navbar-expand-lg navbar-light">
        <div className="container">
          <Link to="/" className="navbar-brand fw-bold text-primary" onClick={handleNavLinkClick}>
            <i className="fas fa-shield-alt me-2"></i>
            ComplaintHub
          </Link>
          
          <button 
            className="navbar-toggler" 
            type="button" 
            onClick={handleNavToggle}
            aria-controls="main-nav"
            aria-expanded={isNavExpanded}
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className={`collapse navbar-collapse ${isNavExpanded ? 'show' : ''}`} id="main-nav">
            {renderAuthLinks()}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
