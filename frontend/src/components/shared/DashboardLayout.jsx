import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import './DashboardLayout.css';

const DashboardLayout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 769;
      setIsMobile(mobile);
      
      // Auto-close sidebar on mobile when screen gets larger
      if (!mobile && isSidebarOpen) {
        setIsSidebarOpen(false);
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [isSidebarOpen]);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar Toggle Button (Mobile) */}
      {isMobile && (
        <button
          className="sidebar-toggle-btn"
          onClick={toggleSidebar}
          aria-label="Toggle sidebar"
        >
          <i className="bi bi-list"></i>
        </button>
      )}

      {/* Sidebar */}
      <Sidebar isOpen={isSidebarOpen || !isMobile} onClose={closeSidebar} />

      {/* Main Content */}
      <div className={`dashboard-main ${!isMobile ? 'with-sidebar' : ''}`}>
        <div className="dashboard-content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;