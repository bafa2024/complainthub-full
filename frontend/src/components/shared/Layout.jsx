import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Header from './Header';
import MockupIndicator from './MockupIndicator';
import RoleSwitcher from './RoleSwitcher';
import './Layout.css';

const Layout = ({ children }) => {
  const { mockupMode } = useAuth();

  return (
    <div className="app-layout">
      <Header />
      
      {mockupMode && (
        <div className="mockup-indicator-container">
          <MockupIndicator />
          <RoleSwitcher />
        </div>
      )}
      
      <main className="main-content">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;