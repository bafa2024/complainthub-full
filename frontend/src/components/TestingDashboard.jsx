import React, { useState } from 'react';
import axios from 'axios';

const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const features = [
  { key: 'register', label: 'User Registration/Signup' },
  { key: 'login', label: 'User Login' },
  { key: 'brandLogin', label: 'Brand Login' },
  { key: 'adminLogin', label: 'Admin Login' },
  { key: 'submitComplaint', label: 'Complaint Submission' },
  { key: 'trackComplaint', label: 'Complaint Tracking' },
  { key: 'publicComplaints', label: 'Public Complaints' },
  { key: 'logout', label: 'Logout' },
];

const TestingDashboard = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});

  const handleTest = async (featureKey) => {
    setLoading((prev) => ({ ...prev, [featureKey]: true }));
    setResults((prev) => ({ ...prev, [featureKey]: null }));
    try {
      let response;
      switch (featureKey) {
        case 'register':
          response = await axios.post(`${apiBase}/api/v1/users/register`, {
            email: `testuser_${Date.now()}@test.com`,
            password: 'TestPassword123!',
            full_name: 'Test User',
          });
          break;
        case 'login':
          response = await axios.post(`${apiBase}/api/v1/login`, {
            email: 'testuser@test.com',
            password: 'TestPassword123!',
          });
          break;
        case 'brandLogin':
          response = await axios.post(`${apiBase}/api/v1/login`, {
            email: 'branduser@test.com',
            password: 'TestPassword123!',
          });
          break;
        case 'adminLogin':
          response = await axios.post(`${apiBase}/api/v1/login`, {
            email: 'admin@test.com',
            password: 'TestPassword123!',
          });
          break;
        case 'submitComplaint':
          response = await axios.post(`${apiBase}/api/v1/complaints`, {
            title: 'Test Complaint',
            description: 'This is a test complaint.',
            category: 'General',
          });
          break;
        case 'trackComplaint':
          response = await axios.get(`${apiBase}/api/v1/complaints/track/1`);
          break;
        case 'publicComplaints':
          response = await axios.get(`${apiBase}/api/v1/complaints/public`);
          break;
        case 'logout':
          response = { data: 'Logged out (frontend only)' };
          break;
        default:
          response = { data: 'Not implemented' };
      }
      setResults((prev) => ({ ...prev, [featureKey]: response.data }));
    } catch (error) {
      setResults((prev) => ({ ...prev, [featureKey]: error.response?.data || error.message }));
    } finally {
      setLoading((prev) => ({ ...prev, [featureKey]: false }));
    }
  };

  return (
    <div className="container py-4">
      <h2>Testing Dashboard</h2>
      <p>Unit test and debug each major feature of the system.</p>
      <div className="row">
        {features.map((feature) => (
          <div className="col-md-6 col-lg-4 mb-4" key={feature.key}>
            <div className="card h-100">
              <div className="card-body">
                <h5 className="card-title">{feature.label}</h5>
                <button
                  className="btn btn-primary mb-2"
                  onClick={() => handleTest(feature.key)}
                  disabled={loading[feature.key]}
                >
                  {loading[feature.key] ? 'Testing...' : 'Run Test'}
                </button>
                <pre style={{ fontSize: '0.85em', background: '#f8f9fa', padding: '8px', borderRadius: '4px', minHeight: '60px' }}>
                  {results[feature.key] ? JSON.stringify(results[feature.key], null, 2) : 'No result yet.'}
                </pre>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TestingDashboard; 