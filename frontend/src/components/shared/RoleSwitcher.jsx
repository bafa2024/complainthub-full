import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const RoleSwitcher = () => {
  const { user } = useAuth();
  
  const switchRole = (newRole) => {
    // In the real implementation, you'd update the context
    // For now, just reload the page after updating localStorage
    localStorage.setItem('demoRole', newRole);
    window.location.reload();
  };

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
        Demo Mode - Current Role: {user.role}
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button 
          onClick={() => switchRole('user')} 
          className={`btn btn-sm ${user.role === 'user' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          User
        </button>
        <button 
          onClick={() => switchRole('brand_user')} 
          className={`btn btn-sm ${user.role === 'brand_user' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          Brand
        </button>
        <button 
          onClick={() => switchRole('admin')} 
          className={`btn btn-sm ${user.role === 'admin' ? 'btn-primary' : 'btn-outline-primary'}`}
        >
          Admin
        </button>
      </div>
    </div>
  );
};

export default RoleSwitcher;