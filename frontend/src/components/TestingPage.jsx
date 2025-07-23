import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const TestingPage = () => {
  const { isAuthenticated, user, login, signup, logout, mockupMode, toggleMockupMode } = useAuth();
  const navigate = useNavigate();
  const [testResults, setTestResults] = useState([]);

  const addTestResult = (test, status, message) => {
    setTestResults(prev => [...prev, { test, status, message, timestamp: new Date().toLocaleTimeString() }]);
  };

  const testLogin = async () => {
    try {
      addTestResult('Login Test', 'running', 'Testing login functionality...');
      
      const loginData = {
        email: 'test@example.com',
        password: 'password123'
      };
      
      await login(loginData);
      addTestResult('Login Test', 'success', 'Login successful! User authenticated.');
    } catch (error) {
      addTestResult('Login Test', 'error', `Login failed: ${error.message}`);
    }
  };

  const testSignup = async () => {
    try {
      addTestResult('Signup Test', 'running', 'Testing signup functionality...');
      
      const signupData = {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
        phone: '+1234567890',
        password: 'password123',
        confirmPassword: 'password123'
      };
      
      await signup(signupData);
      addTestResult('Signup Test', 'success', 'Signup successful! User created and authenticated.');
    } catch (error) {
      addTestResult('Signup Test', 'error', `Signup failed: ${error.message}`);
    }
  };

  const testLogout = () => {
    try {
      addTestResult('Logout Test', 'running', 'Testing logout functionality...');
      logout();
      addTestResult('Logout Test', 'success', 'Logout successful! User logged out.');
    } catch (error) {
      addTestResult('Logout Test', 'error', `Logout failed: ${error.message}`);
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-md-8 mx-auto">
          <div className="card">
            <div className="card-header">
              <h3 className="mb-0">Authentication Testing Page</h3>
            </div>
            <div className="card-body">
              {/* Status Information */}
              <div className="alert alert-info">
                <h5>Current Status:</h5>
                <p><strong>Mockup Mode:</strong> {mockupMode ? 'Enabled' : 'Disabled'}</p>
                <p><strong>Authenticated:</strong> {isAuthenticated ? 'Yes' : 'No'}</p>
                {user && (
                  <div>
                    <p><strong>User:</strong> {user.full_name} ({user.email})</p>
                    <p><strong>Role:</strong> {user.role}</p>
                  </div>
                )}
              </div>

              {/* Test Controls */}
              <div className="row mb-4">
                <div className="col-md-4">
                  <button 
                    className="btn btn-primary w-100 mb-2" 
                    onClick={testLogin}
                    disabled={isAuthenticated}
                  >
                    Test Login
                  </button>
                </div>
                <div className="col-md-4">
                  <button 
                    className="btn btn-success w-100 mb-2" 
                    onClick={testSignup}
                    disabled={isAuthenticated}
                  >
                    Test Signup
                  </button>
                </div>
                <div className="col-md-4">
                  <button 
                    className="btn btn-warning w-100 mb-2" 
                    onClick={testLogout}
                    disabled={!isAuthenticated}
                  >
                    Test Logout
                  </button>
                </div>
              </div>

              {/* Mode Toggle */}
              <div className="row mb-4">
                <div className="col-12">
                  <button 
                    className="btn btn-outline-secondary w-100" 
                    onClick={toggleMockupMode}
                  >
                    Toggle Mockup Mode (Currently: {mockupMode ? 'ON' : 'OFF'})
                  </button>
                </div>
              </div>

              {/* Navigation */}
              <div className="row mb-4">
                <div className="col-md-6">
                  <button 
                    className="btn btn-outline-primary w-100" 
                    onClick={() => navigate('/login')}
                  >
                    Go to Login Page
                  </button>
                </div>
                <div className="col-md-6">
                  <button 
                    className="btn btn-outline-success w-100" 
                    onClick={() => navigate('/signup')}
                  >
                    Go to Signup Page
                  </button>
                </div>
              </div>

              {/* Test Results */}
              <div className="mt-4">
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5>Test Results</h5>
                  <button className="btn btn-sm btn-outline-secondary" onClick={clearResults}>
                    Clear Results
                  </button>
                </div>
                
                {testResults.length === 0 ? (
                  <div className="alert alert-light text-center">
                    No test results yet. Run some tests to see results here.
                  </div>
                ) : (
                  <div className="test-results">
                    {testResults.map((result, index) => (
                      <div 
                        key={index} 
                        className={`alert alert-${result.status === 'success' ? 'success' : result.status === 'error' ? 'danger' : 'info'} mb-2`}
                      >
                        <div className="d-flex justify-content-between align-items-start">
                          <div>
                            <strong>{result.test}</strong>
                            <br />
                            <small>{result.message}</small>
                          </div>
                          <small className="text-muted">{result.timestamp}</small>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestingPage; 