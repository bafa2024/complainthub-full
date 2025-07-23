import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const DebugAuth = () => {
  const { isAuthenticated, user, loading, token, mockupMode } = useAuth();

  return (
    <div className="container mt-5">
      <h2>🔍 Authentication Debug Info</h2>
      
      <div className="card">
        <div className="card-body">
          <h5>Current State:</h5>
          <ul>
            <li><strong>Loading:</strong> {loading ? 'Yes' : 'No'}</li>
            <li><strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</li>
            <li><strong>Mockup Mode:</strong> {mockupMode ? 'Yes' : 'No'}</li>
            <li><strong>Token:</strong> {token ? 'Present' : 'None'}</li>
          </ul>

          {user && (
            <>
              <h5>User Data:</h5>
              <pre className="bg-light p-3 rounded">
                {JSON.stringify(user, null, 2)}
              </pre>
            </>
          )}

          <h5>Token Details:</h5>
          <pre className="bg-light p-3 rounded">
            {token || 'No token'}
          </pre>

          <h5>Local Storage:</h5>
          <pre className="bg-light p-3 rounded">
            Token: {localStorage.getItem('token') || 'None'}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default DebugAuth; 