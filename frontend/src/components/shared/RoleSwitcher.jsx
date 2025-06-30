import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const RoleSwitcher = () => {
  const { user, switchMockRole, mockupMode } = useAuth();
  
  // Only show in mockup mode
  if (!mockupMode) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      background: '#f8f9fa',
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      zIndex: 1000
    }}>
      <div style={{ marginBottom: '10px', fontWeight: 'bold' }}>
        Demo Mode - Current Role: {user?.role || 'user'}
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => switchMockRole('user')} 
          className={`btn btn-sm ${user?.role === 'user' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          User
        </button>
        <button 
          onClick={() => switchMockRole('brand_user')} 
          className={`btn btn-sm ${user?.role === 'brand_user' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          Brand
        </button>
        <button 
          onClick={() => switchMockRole('admin')} 
          className={`btn btn-sm ${user?.role === 'admin' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          Admin
        </button>
      </div>
    </div>
  );
};

export default RoleSwitcher;