import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Header.css';

const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
    <header style={{
      background: 'white',
      padding: '20px 0',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      position: 'fixed',
      width: '100%',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 20px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link to={isAuthenticated && user?.role === 'user' ? "/dashboard" : "/"} style={{
          fontSize: '24px',
          fontWeight: '700',
          color: '#3498db',
          textDecoration: 'none'
        }} onClick={closeMenu}>
          ComplaintHub
        </Link>
        
        <div style={{
          display: 'flex',
          gap: '15px',
          alignItems: 'center'
        }}>
          {!isAuthenticated ? (
            <>
              <Link to="/login" style={{
                padding: '10px 20px',
                border: '2px solid #3498db',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                textDecoration: 'none',
                display: 'inline-block',
                background: 'transparent',
                color: '#3498db'
              }} onMouseOver={(e) => {
                e.target.style.background = '#3498db';
                e.target.style.color = 'white';
              }} onMouseOut={(e) => {
                e.target.style.background = 'transparent';
                e.target.style.color = '#3498db';
              }} onClick={closeMenu}>Login</Link>
              
              <Link to="/signup" style={{
                padding: '10px 20px',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                textDecoration: 'none',
                display: 'inline-block',
                background: '#3498db',
                color: 'white'
              }} onMouseOver={(e) => {
                e.target.style.background = '#2980b9';
                e.target.style.transform = 'translateY(-1px)';
              }} onMouseOut={(e) => {
                e.target.style.background = '#3498db';
                e.target.style.transform = 'translateY(0)';
              }} onClick={closeMenu}>Sign Up</Link>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <span style={{ color: '#2c3e50' }}>Hi, {user?.full_name || user?.name || 'User'}</span>
              <button 
                style={{
                  padding: '8px 16px',
                  border: '2px solid #e74c3c',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  background: 'transparent',
                  color: '#e74c3c'
                }}
                onMouseOver={(e) => {
                  e.target.style.background = '#e74c3c';
                  e.target.style.color = 'white';
                }}
                onMouseOut={(e) => {
                  e.target.style.background = 'transparent';
                  e.target.style.color = '#e74c3c';
                }}
                onClick={() => {
                  logout();
                  closeMenu();
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
