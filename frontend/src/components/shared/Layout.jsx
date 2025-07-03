import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import MockupIndicator from './MockupIndicator';
import RoleSwitcher from './RoleSwitcher';

const Layout = ({ children }) => {
  const { isAuthenticated, user, logout, mockupMode } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
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
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  User Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/dashboard" className={`dropdown-item ${isActive('/dashboard') ? 'active' : ''}`}>Dashboard</Link></li>
                  <li><Link to="/settings" className={`dropdown-item ${isActive('/settings') ? 'active' : ''}`}>Settings</Link></li>
                  <li><Link to="/new-complaint" className={`dropdown-item ${isActive('/new-complaint') ? 'active' : ''}`}>New Complaint</Link></li>
                  <li><Link to="/lodge-voice" className={`dropdown-item ${isActive('/lodge-voice') ? 'active' : ''}`}>Lodge Voice</Link></li>
                  <li><Link to="/chat" className={`dropdown-item ${isActive('/chat') ? 'active' : ''}`}>Chat</Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  Brand Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/brand/dashboard" className={`dropdown-item ${isActive('/brand/dashboard') ? 'active' : ''}`}>Dashboard</Link></li>
                  <li><Link to="/brand/billing" className={`dropdown-item ${isActive('/brand/billing') ? 'active' : ''}`}>Billing</Link></li>
                  <li><Link to="/brand/team" className={`dropdown-item ${isActive('/brand/team') ? 'active' : ''}`}>Team</Link></li>
                  <li><Link to="/brand/analytics" className={`dropdown-item ${isActive('/brand/analytics') ? 'active' : ''}`}>Analytics</Link></li>
                  <li><Link to="/brand/settings" className={`dropdown-item ${isActive('/brand/settings') ? 'active' : ''}`}>Settings</Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  Admin Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/admin/dashboard" className={`dropdown-item ${isActive('/admin/dashboard') ? 'active' : ''}`}>Dashboard</Link></li>
                  <li><Link to="/admin/brands" className={`dropdown-item ${isActive('/admin/brands') ? 'active' : ''}`}>Brands</Link></li>
                  <li><Link to="/admin/users" className={`dropdown-item ${isActive('/admin/users') ? 'active' : ''}`}>Users</Link></li>
                  <li><Link to="/admin/complaints" className={`dropdown-item ${isActive('/admin/complaints') ? 'active' : ''}`}>Complaints</Link></li>
                  <li><Link to="/admin/reports" className={`dropdown-item ${isActive('/admin/reports') ? 'active' : ''}`}>Reports</Link></li>
                  <li><Link to="/admin/settings" className={`dropdown-item ${isActive('/admin/settings') ? 'active' : ''}`}>Settings</Link></li>
                  <li><Link to="/admin/billing" className={`dropdown-item ${isActive('/admin/billing') ? 'active' : ''}`}>Billing</Link></li>
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
                    <Link to="/admin/dashboard" className={`nav-link ${isActive('/admin/dashboard') ? 'active' : ''}`}>
                      <i className="fas fa-tachometer-alt me-1"></i>Admin
                    </Link>
                  </li>
                </>
              )}
              {user?.role === 'brand_user' && (
                <>
                  <li className="nav-item">
                    <Link to="/brand/dashboard" className={`nav-link ${isActive('/brand/dashboard') ? 'active' : ''}`}>
                      <i className="fas fa-building me-1"></i>Brand Dashboard
                    </Link>
                  </li>
                </>
              )}
              {user?.role === 'user' && (
                <>
                  <li className="nav-item">
                    <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}>
                      <i className="fas fa-home me-1"></i>My Dashboard
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link to="/settings" className={`nav-link ${isActive('/settings') ? 'active' : ''}`}>
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
            <Link to="/login" className={`nav-link ${isActive('/login') ? 'active' : ''}`}>
              <i className="fas fa-user me-1"></i>Customer Login
            </Link>
          </li>
          <li className="nav-item d-flex align-items-center">
            <Link to="/brand/login" className={`nav-link ${isActive('/brand/login') ? 'active' : ''}`}>
              <i className="fas fa-building me-1"></i>Brand Login
            </Link>
          </li>
          <li className="nav-item d-flex align-items-center">
            <Link to="/signup" className="btn btn-primary">
              <i className="fas fa-user-plus me-1"></i>Sign Up
            </Link>
          </li>
        </ul>
      );
    }
  };

  return (
    <div className="app-layout">
      <nav className="navbar navbar-expand-lg navbar-modern">
        <div className="container">
          <Link to="/" className="navbar-brand">
            <i className="fas fa-shield-alt me-2"></i>
            <span className="brand-highlight">ComplaintHub</span>
          </Link>
          
          <button 
            className="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#main-nav"
            aria-controls="main-nav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
          
          <div className="collapse navbar-collapse" id="main-nav">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <Link to="/complaints" className={`nav-link ${isActive('/complaints') ? 'active' : ''}`}>
                  <i className="fas fa-list me-1"></i>Public Complaints
                </Link>
              </li>
              <li className="nav-item">
                <Link to="/track-complaint" className={`nav-link ${isActive('/track-complaint') ? 'active' : ''}`}>
                  <i className="fas fa-search me-1"></i>Track Complaint
                </Link>
              </li>
              <li className="nav-item">
                <Link to="/help" className={`nav-link ${isActive('/help') ? 'active' : ''}`}>
                  <i className="fas fa-question-circle me-1"></i>Help Center
                </Link>
              </li>
              <li className="nav-item">
                <Link to="/contact" className={`nav-link ${isActive('/contact') ? 'active' : ''}`}>
                  <i className="fas fa-envelope me-1"></i>Contact
                </Link>
              </li>
            </ul>
            {renderAuthLinks()}
          </div>
        </div>
      </nav>
      
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
      
      <MockupIndicator />
    </div>
  );
};

export default Layout;