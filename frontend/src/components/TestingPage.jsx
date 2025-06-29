import React, { useState, useEffect } from 'react';
import testingService from '../services/testingService';
import './TestingPage.css';

const TestingPage = () => {
  const [testResults, setTestResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [individualTest, setIndividualTest] = useState(null);

  const runAllTests = async () => {
    setIsRunning(true);
    setTestResults(null);
    
    try {
      const results = await testingService.runAllTests();
      setTestResults(results);
    } catch (error) {
      setTestResults({
        error: error.message,
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsRunning(false);
    }
  };

  const runIndividualTest = async (testName, testFunction) => {
    setIndividualTest({ name: testName, status: 'running' });
    
    try {
      const result = await testFunction();
      setIndividualTest({ name: testName, status: 'completed', result });
    } catch (error) {
      setIndividualTest({ name: testName, status: 'error', error: error.message });
    }
  };

  const getStatusColor = (success) => {
    return success ? 'success' : 'error';
  };

  const getStatusIcon = (success) => {
    return success ? '✅' : '❌';
  };

  const formatTestData = (data) => {
    if (typeof data === 'object' && data !== null) {
      return JSON.stringify(data, null, 2);
    }
    return String(data);
  };

  const TestResultCard = ({ title, result, type = 'info' }) => {
    if (!result) return null;

    const isSuccess = result.success !== undefined ? result.success : true;
    const statusColor = getStatusColor(isSuccess);
    const statusIcon = getStatusIcon(isSuccess);

    return (
      <div className={`test-result-card ${statusColor}`}>
        <div className="test-result-header">
          <h4>{title}</h4>
          <span className="status-icon">{statusIcon}</span>
        </div>
        <div className="test-result-content">
          {result.error && (
            <div className="error-message">
              <strong>Error:</strong> {result.error}
            </div>
          )}
          {result.data && (
            <div className="test-data">
              <strong>Data:</strong>
              <pre>{formatTestData(result.data)}</pre>
            </div>
          )}
          {result.status && (
            <div className="test-status">
              <strong>Status:</strong> {result.status}
            </div>
          )}
        </div>
      </div>
    );
  };

  const BackendTests = () => (
    <div className="tests-section">
      <h3>Backend Tests</h3>
      <div className="test-buttons">
        <button 
          onClick={() => runIndividualTest('Health Check', testingService.testBackendHealth)}
          className="test-button"
        >
          Test Health Check
        </button>
        <button 
          onClick={() => runIndividualTest('Database', testingService.testBackendDatabase)}
          className="test-button"
        >
          Test Database
        </button>
        <button 
          onClick={() => runIndividualTest('API Connectivity', testingService.testBackendAPI)}
          className="test-button"
        >
          Test API Connectivity
        </button>
        <button 
          onClick={() => runIndividualTest('Data Flow', testingService.testBackendDataFlow)}
          className="test-button"
        >
          Test Data Flow
        </button>
        <button 
          onClick={() => runIndividualTest('CRUD Operations', testingService.testBackendCRUD)}
          className="test-button"
        >
          Test CRUD
        </button>
        <button 
          onClick={() => runIndividualTest('Mock Data', testingService.testBackendMockData)}
          className="test-button"
        >
          Test Mock Data
        </button>
      </div>
      
      {individualTest && individualTest.name.includes('Backend') && (
        <TestResultCard 
          title={individualTest.name} 
          result={individualTest.result} 
        />
      )}
      
      {testResults?.backend && (
        <div className="test-results">
          {Object.entries(testResults.backend).map(([testName, result]) => (
            <TestResultCard key={testName} title={testName} result={result} />
          ))}
        </div>
      )}
    </div>
  );

  const FrontendTests = () => (
    <div className="tests-section">
      <h3>Frontend Tests</h3>
      <div className="test-buttons">
        <button 
          onClick={() => runIndividualTest('Local Storage', testingService.testFrontendLocalStorage)}
          className="test-button"
        >
          Test Local Storage
        </button>
        <button 
          onClick={() => runIndividualTest('Session Storage', testingService.testFrontendSessionStorage)}
          className="test-button"
        >
          Test Session Storage
        </button>
        <button 
          onClick={() => runIndividualTest('Cookies', testingService.testFrontendCookies)}
          className="test-button"
        >
          Test Cookies
        </button>
        <button 
          onClick={() => runIndividualTest('API Connectivity', testingService.testFrontendAPIConnectivity)}
          className="test-button"
        >
          Test API Connectivity
        </button>
        <button 
          onClick={() => runIndividualTest('Data Validation', testingService.testFrontendDataValidation)}
          className="test-button"
        >
          Test Data Validation
        </button>
        <button 
          onClick={() => runIndividualTest('Responsive Design', testingService.testFrontendResponsiveDesign)}
          className="test-button"
        >
          Test Responsive Design
        </button>
      </div>
      
      {individualTest && !individualTest.name.includes('Backend') && (
        <TestResultCard 
          title={individualTest.name} 
          result={individualTest.result} 
        />
      )}
      
      {testResults?.frontend && (
        <div className="test-results">
          {Object.entries(testResults.frontend).map(([testName, result]) => (
            <TestResultCard key={testName} title={testName} result={result} />
          ))}
        </div>
      )}
    </div>
  );

  const Dashboard = () => (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Testing Dashboard</h2>
        <button 
          onClick={runAllTests} 
          disabled={isRunning}
          className="run-all-tests-btn"
        >
          {isRunning ? 'Running Tests...' : 'Run All Tests'}
        </button>
      </div>

      {testResults?.summary && (
        <div className="test-summary">
          <h3>Test Summary</h3>
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Total Tests:</span>
              <span className="stat-value">{testResults.summary.total}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Passed:</span>
              <span className="stat-value success">{testResults.summary.passed}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Failed:</span>
              <span className="stat-value error">{testResults.summary.failed}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Success Rate:</span>
              <span className="stat-value">
                {testResults.summary.total > 0 
                  ? `${((testResults.summary.passed / testResults.summary.total) * 100).toFixed(1)}%`
                  : '0%'
                }
              </span>
            </div>
          </div>
          <div className="timestamp">
            Last run: {new Date(testResults.timestamp).toLocaleString()}
          </div>
        </div>
      )}

      {testResults?.error && (
        <div className="error-summary">
          <h3>Error Summary</h3>
          <div className="error-message">{testResults.error}</div>
        </div>
      )}

      <div className="quick-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
          <button 
            onClick={() => runIndividualTest('Health Check', testingService.testBackendHealth)}
            className="action-button"
          >
            Quick Health Check
          </button>
          <button 
            onClick={() => runIndividualTest('Database', testingService.testBackendDatabase)}
            className="action-button"
          >
            Database Test
          </button>
          <button 
            onClick={() => runIndividualTest('API Connectivity', testingService.testFrontendAPIConnectivity)}
            className="action-button"
          >
            API Connectivity
          </button>
        </div>
      </div>
    </div>
  );

  const RawResults = () => (
    <div className="raw-results">
      <h3>Raw Test Results</h3>
      {testResults ? (
        <pre className="json-output">
          {JSON.stringify(testResults, null, 2)}
        </pre>
      ) : (
        <p>No test results available. Run tests to see results here.</p>
      )}
    </div>
  );

  return (
    <div className="testing-page">
      <div className="testing-header">
        <h1>🧪 Developer Testing Suite</h1>
        <p>Comprehensive testing tools for backend and frontend validation</p>
      </div>

      <div className="testing-navigation">
        <button 
          className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`nav-tab ${activeTab === 'backend' ? 'active' : ''}`}
          onClick={() => setActiveTab('backend')}
        >
          Backend Tests
        </button>
        <button 
          className={`nav-tab ${activeTab === 'frontend' ? 'active' : ''}`}
          onClick={() => setActiveTab('frontend')}
        >
          Frontend Tests
        </button>
        <button 
          className={`nav-tab ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          Raw Results
        </button>
      </div>

      <div className="testing-content">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'backend' && <BackendTests />}
        {activeTab === 'frontend' && <FrontendTests />}
        {activeTab === 'raw' && <RawResults />}
      </div>

      {isRunning && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Running tests...</p>
        </div>
      )}
    </div>
  );
};

export default TestingPage; 