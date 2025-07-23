import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  const menuItems = [
    {
      path: '/dashboard',
      icon: 'bi-speedometer2',
      label: 'Dashboard',
      active: location.pathname === '/dashboard'
    },
    {
      path: '/my-complaints',
      icon: 'bi-list-ul',
      label: 'My Complaints',
      active: location.pathname === '/my-complaints'
    },
    {
      path: '/new-complaint',
      icon: 'bi-plus-circle',
      label: 'New Complaint',
      active: location.pathname === '/new-complaint'
    }
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      
      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h3 className="sidebar-title">User Portal</h3>
          <button className="sidebar-close" onClick={onClose}>
            <i className="bi bi-x-lg"></i>
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <ul className="sidebar-menu">
            {menuItems.map((item) => (
              <li key={item.path} className="sidebar-item">
                <Link
                  to={item.path}
                  className={`sidebar-link ${item.active ? 'active' : ''}`}
                  onClick={onClose}
                >
                  <i className={item.icon}></i>
                  <span>{item.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user-info">
            <i className="bi bi-person-circle"></i>
            <div className="user-details">
              <span className="user-name">{user?.full_name || user?.name || 'User'}</span>
              <span className="user-role">{user?.role || 'Customer'}</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;