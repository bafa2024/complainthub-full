import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
// We no longer need the custom Layout.css for the header
// import './Layout.css'; 

const Layout = ({ children }) => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const renderAuthLinks = () => {
    if (isAuthenticated) {
      return (
        <ul className="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
          <li className="nav-item">
            <span className="navbar-text me-3">
              Welcome, {user?.full_name || user?.email}
            </span>
          </li>
          {user?.role === 'admin' && <li className="nav-item"><Link to="/admin/dashboard" className="nav-link">Admin</Link></li>}
          {user?.role === 'brand_user' && <li className="nav-item"><Link to="/brand/dashboard" className="nav-link">Brand Dashboard</Link></li>}
          {user?.role === 'user' && <li className="nav-item"><Link to="/dashboard" className="nav-link">My Dashboard</Link></li>}
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
      <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
        <div className="container">
          <Link to="/" className="navbar-brand">ComplaintHub</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#main-nav">
            <span className="navbar-toggler-icon"></span>
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
    </div>
  );
};

export default Layout;