import React, { useState, useEffect } from 'react';
import axios from 'axios';

// API base URL - pointing to our running backend
const API_BASE_URL = 'http://localhost:8000';

function TestApp() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);

  // Test backend connectivity
  const testBackendHealth = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setBackendStatus(response.data);
    } catch (error) {
      setBackendStatus({ status: 'error', message: error.message });
    }
    setLoading(false);
  };

  // Test backend endpoints
  const testEndpoints = async () => {
    setLoading(true);
    const endpoints = [
      { name: 'Root', url: '/' },
      { name: 'Health Check', url: '/health' },
      { name: 'Test Endpoint', url: '/test' },
      { name: 'Testing Dashboard', url: '/api/v1/testing/' },
      { name: 'Database Test', url: '/api/v1/testing/database' },
      { name: 'CRUD Test', url: '/api/v1/testing/crud' },
      { name: 'Mock Data Test', url: '/api/v1/testing/mock-data' }
    ];

    const results = {};
    
    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${API_BASE_URL}${endpoint.url}`);
        results[endpoint.name] = {
          status: 'success',
          statusCode: response.status,
          data: response.data
        };
      } catch (error) {
        results[endpoint.name] = {
          status: 'error',
          statusCode: error.response?.status || 'N/A',
          message: error.message
        };
      }
    }
    
    setTestResults(results);
    setLoading(false);
  };

  // Auto-test on component mount
  useEffect(() => {
    testBackendHealth();
  }, []);

  return (
    <div className="container-fluid p-4">
      <div className="row">
        <div className="col-12">
          <h1 className="mb-4">Frontend-Backend Integration Test</h1>
          
          {/* Backend Status Card */}
          <div className="card mb-4">
            <div className="card-header">
              <h3>Backend Status</h3>
            </div>
            <div className="card-body">
              {loading && <div className="spinner-border me-2" role="status"></div>}
              {backendStatus ? (
                <div>
                  <div className={`alert ${backendStatus.status === 'healthy' ? 'alert-success' : 'alert-danger'}`}>
                    <strong>Status:</strong> {backendStatus.status}
                    {backendStatus.message && (
                      <div><strong>Message:</strong> {backendStatus.message}</div>
                    )}
                    {backendStatus.timestamp && (
                      <div><small>Timestamp: {backendStatus.timestamp}</small></div>
                    )}
                  </div>
                  
                  {backendStatus.status === 'healthy' && (
                    <div className="row">
                      <div className="col-md-4">
                        <strong>API Version:</strong> {backendStatus.api_version}
                      </div>
                      <div className="col-md-4">
                        <strong>Database:</strong> {backendStatus.database}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p>Testing backend connection...</p>
              )}
              
              <div className="mt-3">
                <button 
                  className="btn btn-primary me-2" 
                  onClick={testBackendHealth}
                  disabled={loading}
                >
                  Refresh Status
                </button>
                <button 
                  className="btn btn-success" 
                  onClick={testEndpoints}
                  disabled={loading}
                >
                  Test All Endpoints
                </button>
              </div>
            </div>
          </div>

          {/* Test Results */}
          {Object.keys(testResults).length > 0 && (
            <div className="card">
              <div className="card-header">
                <h3>Endpoint Test Results</h3>
              </div>
              <div className="card-body">
                <div className="row">
                  {Object.entries(testResults).map(([name, result]) => (
                    <div key={name} className="col-md-6 mb-3">
                      <div className={`card border-${result.status === 'success' ? 'success' : 'danger'}`}>
                        <div className="card-header">
                          <strong>{name}</strong>
                          <span className={`badge ms-2 ${result.status === 'success' ? 'bg-success' : 'bg-danger'}`}>
                            {result.statusCode}
                          </span>
                        </div>
                        <div className="card-body">
                          {result.status === 'success' ? (
                            <div>
                              <div className="text-success mb-2">✓ Success</div>
                              {result.data && (
                                <details>
                                  <summary>Response Data</summary>
                                  <pre className="mt-2 small">{JSON.stringify(result.data, null, 2)}</pre>
                                </details>
                              )}
                            </div>
                          ) : (
                            <div>
                              <div className="text-danger mb-2">✗ Failed</div>
                              <small>{result.message}</small>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Quick Links */}
          <div className="card mt-4">
            <div className="card-header">
              <h3>Quick Links</h3>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h5>Backend URLs:</h5>
                  <ul className="list-unstyled">
                    <li><a href="http://localhost:8000" target="_blank" rel="noopener noreferrer">Backend Root</a></li>
                    <li><a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">API Documentation</a></li>
                    <li><a href="http://localhost:8000/health" target="_blank" rel="noopener noreferrer">Health Check</a></li>
                    <li><a href="http://localhost:8000/api/v1/testing/" target="_blank" rel="noopener noreferrer">Testing Dashboard</a></li>
                  </ul>
                </div>
                <div className="col-md-6">
                  <h5>Frontend Info:</h5>
                  <ul className="list-unstyled">
                    <li><strong>Frontend URL:</strong> {window.location.origin}</li>
                    <li><strong>React Version:</strong> {React.version}</li>
                    <li><strong>Environment:</strong> Development</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TestApp;