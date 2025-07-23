import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const BrandAuthTest = () => {
  const { login, user, isAuthenticated, token } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('🔍 Attempting brand login with:', formData);
      const userData = await login(formData);
      console.log('✅ Login successful:', userData);
      
      // Try to navigate to brand dashboard
      navigate('/brand/dashboard');
    } catch (err) {
      console.error('❌ Login failed:', err);
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h2>🧪 Brand Authentication Test</h2>
      
      <div className="row">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>Current State</h5>
            </div>
            <div className="card-body">
              <ul>
                <li><strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</li>
                <li><strong>Token:</strong> {token ? 'Present' : 'None'}</li>
                <li><strong>User Role:</strong> {user?.role || 'None'}</li>
                <li><strong>User Email:</strong> {user?.email || 'None'}</li>
              </ul>
              
              {user && (
                <div>
                  <h6>User Data:</h6>
                  <pre className="bg-light p-2 rounded" style={{ fontSize: '0.8rem' }}>
                    {JSON.stringify(user, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h5>Brand Login Test</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleLogin}>
                {error && (
                  <div className="alert alert-danger">{error}</div>
                )}
                
                <div className="mb-3">
                  <label className="form-label">Email:</label>
                  <input
                    type="email"
                    name="email"
                    className="form-control"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />
                </div>
                
                <div className="mb-3">
                  <label className="form-label">Password:</label>
                  <input
                    type="password"
                    name="password"
                    className="form-control"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Logging in...' : 'Test Brand Login'}
                </button>
              </form>
              
              <div className="mt-3">
                <small className="text-muted">
                  Use a brand account created from the backend tests
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BrandAuthTest; 