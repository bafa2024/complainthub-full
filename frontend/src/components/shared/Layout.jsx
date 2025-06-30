import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import MockupIndicator from './MockupIndicator';
import RoleSwitcher from './RoleSwitcher';

const Layout = ({ children }) => {
  const { isAuthenticated, user, logout, mockupMode } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
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
                  <li><Link to="/dashboard" className="dropdown-item">Dashboard</Link></li>
                  <li><Link to="/settings" className="dropdown-item">Settings</Link></li>
                  <li><Link to="/new-complaint" className="dropdown-item">New Complaint</Link></li>
                  <li><Link to="/lodge-voice" className="dropdown-item">Lodge Voice</Link></li>
                  <li><Link to="/chat" className="dropdown-item">Chat</Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  Brand Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/brand/dashboard" className="dropdown-item">Dashboard</Link></li>
                  <li><Link to="/brand/billing" className="dropdown-item">Billing</Link></li>
                  <li><Link to="/brand/team" className="dropdown-item">Team</Link></li>
                </ul>
              </li>
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                  Admin Portal
                </a>
                <ul className="dropdown-menu">
                  <li><Link to="/admin/dashboard" className="dropdown-item">Dashboard</Link></li>
                  <li><Link to="/admin/brands" className="dropdown-item">Brands</Link></li>
                  <li><Link to="/admin/users" className="dropdown-item">Users</Link></li>
                  <li><Link to="/admin/settings" className="dropdown-item">Settings</Link></li>
                  <li><Link to="/admin/billing" className="dropdown-item">Billing</Link></li>
                </ul>
              </li>
            </>
          )}
          
          {/* Show role-specific links in normal mode */}
          {!mockupMode && (
            <>
          {user?.role === 'admin' && <li className="nav-item"><Link to="/admin/dashboard" className="nav-link">Admin</Link></li>}
          {user?.role === 'brand_user' && <li className="nav-item"><Link to="/brand/dashboard" className="nav-link">Brand Dashboard</Link></li>}
          {user?.role === 'user' && (
            <>
              <li className="nav-item"><Link to="/dashboard" className="nav-link">My Dashboard</Link></li>
              <li className="nav-item"><Link to="/settings" className="nav-link">Settings</Link></li>
            </>
          )}
            </>
          )}
          
          <li className="nav-item">
            <button onClick={handleLogout} className="btn btn-danger btn-sm">Logout</button>
          </li>
        </ul>
      );
    } else {
      return (
        <ul className="navbar-nav ms-auto mb-2 mb-lg-0">
          <li className="nav-item"><Link to="/login" className="nav-link">Customer Login</Link></li>
          <li className="nav-item"><Link to="/brand/login" className="nav-link">Brand Login</Link></li>
          <li className="nav-item"><Link to="/signup" className="btn btn-primary">Sign Up</Link></li>
        </ul>
      );
    }
  };

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm navbar-modern">
        <div className="container">
          <Link to="/" className="navbar-brand"><span className="brand-highlight">ComplaintHub</span></Link>
          <button className="navbar-toggler btn btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#main-nav">
            <span className="navbar-toggler-icon">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
          <div className="collapse navbar-collapse" id="main-nav">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <Link to="/complaints" className="nav-link">Public Complaints</Link>
              </li>
            </ul>
            {renderAuthLinks()}
          </div>
        </div>
      </nav>
      <main className="container mt-4">
        {children}
      </main>
      <MockupIndicator />
    </div>
  );
};

export default Layout;