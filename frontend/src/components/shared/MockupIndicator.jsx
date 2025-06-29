import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const MockupIndicator = () => {
  const { mockupMode, user, switchMockRole, toggleMockupMode } = useAuth();

  if (!mockupMode) {
    return null; // Don't show anything if not in mockup mode
  }

  const handleRoleSwitch = (newRole) => {
    switchMockRole(newRole);
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: 20,
      right: 20,
      background: '#fff',
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      border: '2px solid #007bff',
      zIndex: 1000,
      minWidth: '250px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ 
        marginBottom: '10px', 
        fontWeight: 'bold',
        color: '#007bff',
        fontSize: '14px',
        textAlign: 'center',
        borderBottom: '1px solid #eee',
        paddingBottom: '8px'
      }}>
        🎭 MOCKUP MODE
      </div>
      
      <div style={{ 
        marginBottom: '10px', 
        fontSize: '12px',
        color: '#666'
      }}>
        Current Role: <strong>{user?.role || 'user'}</strong>
      </div>
      
      <div style={{ 
        marginBottom: '15px',
        fontSize: '12px',
        color: '#666'
      }}>
        User: {user?.full_name || 'Demo User'}
      </div>

      <div style={{ marginBottom: '10px' }}>
        <div style={{ fontSize: '11px', color: '#888', marginBottom: '5px' }}>
          Switch Role:
        </div>
        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
          <button 
            onClick={() => handleRoleSwitch('user')} 
            className={`btn btn-sm ${user?.role === 'user' ? 'btn-primary' : 'btn-outline-primary'}`}
            style={{ fontSize: '10px', padding: '4px 8px' }}
          >
            User
          </button>
          <button 
            onClick={() => handleRoleSwitch('brand_user')} 
            className={`btn btn-sm ${user?.role === 'brand_user' ? 'btn-primary' : 'btn-outline-primary'}`}
            style={{ fontSize: '10px', padding: '4px 8px' }}
          >
            Brand
          </button>
          <button 
            onClick={() => handleRoleSwitch('admin')} 
            className={`btn btn-sm ${user?.role === 'admin' ? 'btn-primary' : 'btn-outline-primary'}`}
            style={{ fontSize: '10px', padding: '4px 8px' }}
          >
            Admin
          </button>
        </div>
      </div>

      <div style={{ textAlign: 'center' }}>
        <button 
          onClick={toggleMockupMode}
          className="btn btn-warning btn-sm"
          style={{ fontSize: '10px', padding: '4px 8px' }}
        >
          Disable Mockup
        </button>
      </div>

      <div style={{ 
        marginTop: '10px',
        fontSize: '10px',
        color: '#999',
        textAlign: 'center',
        fontStyle: 'italic'
      }}>
        All authentication bypassed
      </div>
    </div>
  );
};

export default MockupIndicator; 