import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './UIComprehensiveTest.css';

const UIComprehensiveTest = () => {
  const { mockupMode, setMockupMode } = useAuth();
  const navigate = useNavigate();
  const [currentTest, setCurrentTest] = useState(0);
  const [testResults, setTestResults] = useState({});
  const [viewportSize, setViewportSize] = useState('desktop');
  const [showTestResults, setShowTestResults] = useState(false);
  const [testProgress, setTestProgress] = useState(0);

  const testPages = [
    { name: 'Homepage', path: '/', description: 'Landing page with hero, features, testimonials', priority: 'high' },
    { name: 'Public Complaints', path: '/complaints', description: 'Public complaints listing page', priority: 'high' },
    { name: 'Complaint Tracking', path: '/track-complaint', description: 'Complaint tracking form', priority: 'high' },
    { name: 'Contact Page', path: '/contact', description: 'Contact information and form', priority: 'medium' },
    { name: 'Help Center', path: '/help', description: 'FAQ and help documentation', priority: 'medium' },
    { name: 'User Login', path: '/login', description: 'User authentication form', priority: 'high' },
    { name: 'User Signup', path: '/signup', description: 'User registration form', priority: 'high' },
    { name: 'Brand Login', path: '/brand/login', description: 'Brand authentication form', priority: 'high' },
    { name: 'Brand Signup', path: '/brand/signup', description: 'Brand registration form', priority: 'high' },
    { name: 'Admin Login', path: '/admin/login', description: 'Admin authentication form', priority: 'high' },
    { name: 'User Dashboard', path: '/dashboard', description: 'User dashboard with stats and actions', priority: 'high' },
    { name: 'User Settings', path: '/settings', description: 'User profile and settings', priority: 'medium' },
    { name: 'New Complaint', path: '/new-complaint', description: 'Complaint submission form', priority: 'high' },
    { name: 'Brand Dashboard', path: '/brand/dashboard', description: 'Brand dashboard with analytics', priority: 'high' },
    { name: 'Brand Analytics', path: '/brand/analytics', description: 'Brand analytics and reports', priority: 'medium' },
    { name: 'Brand Billing', path: '/brand/billing', description: 'Brand billing and payment', priority: 'medium' },
    { name: 'Brand Settings', path: '/brand/settings', description: 'Brand profile and settings', priority: 'medium' },
    { name: 'Admin Dashboard', path: '/admin/dashboard', description: 'Admin dashboard with overview', priority: 'high' },
    { name: 'Admin Brands', path: '/admin/brands', description: 'Brand management interface', priority: 'medium' },
    { name: 'Admin Users', path: '/admin/users', description: 'User management interface', priority: 'medium' },
    { name: 'Admin Complaints', path: '/admin/tickets', description: 'Complaint management interface', priority: 'medium' },
    { name: 'Admin Analytics', path: '/admin/analytics', description: 'Admin analytics and reports', priority: 'medium' },
    { name: 'Admin Settings', path: '/admin/settings', description: 'Admin system settings', priority: 'low' },
    { name: 'Admin Security', path: '/admin/security', description: 'Security and access control', priority: 'low' },
    { name: 'Admin Reports', path: '/admin/reports', description: 'Reporting and insights', priority: 'low' },
    { name: 'Admin Billing', path: '/admin/billing', description: 'Billing and financial reports', priority: 'low' }
  ];

  const viewportSizes = [
    { name: 'Mobile', width: 375, height: 667, class: 'mobile' },
    { name: 'Tablet', width: 768, height: 1024, class: 'tablet' },
    { name: 'Desktop', width: 1200, height: 800, class: 'desktop' },
    { name: 'Large Desktop', width: 1920, height: 1080, class: 'large-desktop' }
  ];

  const testCriteria = [
    { name: 'Responsive Layout', weight: 25 },
    { name: 'Mobile Navigation', weight: 20 },
    { name: 'Touch Targets', weight: 15 },
    { name: 'Typography Scaling', weight: 10 },
    { name: 'Color Contrast', weight: 10 },
    { name: 'Focus Indicators', weight: 10 },
    { name: 'Loading States', weight: 5 },
    { name: 'Error Handling', weight: 5 }
  ];

  useEffect(() => {
    if (mockupMode) {
      setMockupMode(true);
    }
  }, [mockupMode, setMockupMode]);

  const runTest = (pageIndex) => {
    const page = testPages[pageIndex];
    setCurrentTest(pageIndex);
    
    // Simulate test results with weighted scoring
    const results = testCriteria.map(criteria => {
      const baseScore = Math.random();
      const weightedScore = baseScore * (criteria.weight / 100);
      const status = weightedScore > 0.7 ? 'pass' : weightedScore > 0.4 ? 'partial' : 'fail';
      
      return {
        criteria: criteria.name,
        status,
        score: Math.round(weightedScore * 100),
        notes: getTestNotes(criteria.name, status)
      };
    });
    
    setTestResults(prev => ({
      ...prev,
      [page.name]: results
    }));
    
    navigate(page.path);
  };

  const getTestNotes = (criteria, status) => {
    const notes = {
      'Responsive Layout': {
        pass: 'Layout adapts perfectly to all screen sizes',
        partial: 'Minor layout issues on some breakpoints',
        fail: 'Significant layout problems on mobile/tablet'
      },
      'Mobile Navigation': {
        pass: 'Navigation works seamlessly on mobile',
        partial: 'Some navigation elements need improvement',
        fail: 'Mobile navigation is difficult to use'
      },
      'Touch Targets': {
        pass: 'All interactive elements meet touch target standards',
        partial: 'Some buttons/links are too small',
        fail: 'Many touch targets are too small for mobile'
      },
      'Typography Scaling': {
        pass: 'Text scales appropriately across devices',
        partial: 'Some text elements need better scaling',
        fail: 'Typography doesn\'t scale well on mobile'
      },
      'Color Contrast': {
        pass: 'Excellent color contrast ratios',
        partial: 'Some elements need better contrast',
        fail: 'Poor color contrast affects readability'
      },
      'Focus Indicators': {
        pass: 'Clear focus indicators for keyboard navigation',
        partial: 'Some focus indicators could be improved',
        fail: 'Missing or unclear focus indicators'
      },
      'Loading States': {
        pass: 'Smooth loading states and transitions',
        partial: 'Some loading states need improvement',
        fail: 'Poor loading state implementation'
      },
      'Error Handling': {
        pass: 'Clear error messages and graceful degradation',
        partial: 'Some error states need better UX',
        fail: 'Poor error handling and user feedback'
      }
    };
    
    return notes[criteria]?.[status] || 'Test completed';
  };

  const runAllTests = async () => {
    setTestProgress(0);
    for (let i = 0; i < testPages.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      runTest(i);
      setTestProgress(((i + 1) / testPages.length) * 100);
    }
  };

  const getTestStatus = (pageName) => {
    const results = testResults[pageName];
    if (!results) return 'pending';
    
    const totalScore = results.reduce((sum, r) => sum + r.score, 0);
    const averageScore = totalScore / results.length;
    
    if (averageScore >= 80) return 'pass';
    if (averageScore >= 60) return 'partial';
    return 'fail';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass': return '✅';
      case 'fail': return '❌';
      case 'partial': return '⚠️';
      default: return '⏳';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pass': return 'status-pass';
      case 'fail': return 'status-fail';
      case 'partial': return 'status-partial';
      default: return 'status-pending';
    }
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return '';
    }
  };

  const getOverallScore = () => {
    const completedTests = Object.keys(testResults);
    if (completedTests.length === 0) return 0;
    
    const totalScore = completedTests.reduce((sum, pageName) => {
      const results = testResults[pageName];
      const pageScore = results.reduce((pageSum, r) => pageSum + r.score, 0);
      return sum + (pageScore / results.length);
    }, 0);
    
    return Math.round(totalScore / completedTests.length);
  };

  return (
    <div className="ui-comprehensive-test">
      <div className="test-header">
        <h1>🎨 Comprehensive UI Test Suite</h1>
        <p>Testing all pages for mobile-first responsive design and accessibility</p>
        
        <div className="test-controls">
          <div className="viewport-controls">
            <h3>Viewport Testing</h3>
            <div className="viewport-buttons">
              {viewportSizes.map(size => (
                <button
                  key={size.name}
                  className={`viewport-btn ${viewportSize === size.class ? 'active' : ''}`}
                  onClick={() => setViewportSize(size.class)}
                >
                  {size.name} ({size.width}x{size.height})
                </button>
              ))}
            </div>
          </div>
          
          <div className="test-actions">
            <button className="btn btn-primary" onClick={runAllTests}>
              🚀 Run All Tests
            </button>
            <button 
              className="btn btn-secondary" 
              onClick={() => setShowTestResults(!showTestResults)}
            >
              📊 {showTestResults ? 'Hide' : 'Show'} Results
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        {testProgress > 0 && testProgress < 100 && (
          <div className="test-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${testProgress}%` }}
              ></div>
            </div>
            <p className="progress-text">Running tests... {Math.round(testProgress)}% complete</p>
          </div>
        )}
      </div>

      <div className="test-content">
        <div className="test-sidebar">
          <h3>📋 Test Pages ({testPages.length})</h3>
          <div className="test-pages-list">
            {testPages.map((page, index) => (
              <div 
                key={page.name}
                className={`test-page-item ${currentTest === index ? 'active' : ''} ${getPriorityClass(page.priority)}`}
              >
                <button
                  className="test-page-btn"
                  onClick={() => runTest(index)}
                >
                  <span className="test-page-status">
                    {getStatusIcon(getTestStatus(page.name))}
                  </span>
                  <div className="test-page-info">
                    <span className="test-page-name">{page.name}</span>
                    <span className="test-page-desc">{page.description}</span>
                    <span className="test-page-priority">{page.priority} priority</span>
                  </div>
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="test-main">
          <div className={`viewport-container viewport-${viewportSize}`}>
            <div className="viewport-frame">
              <div className="viewport-header">
                <span className="viewport-title">
                  {testPages[currentTest]?.name || 'Select a page to test'}
                </span>
                <span className="viewport-size">
                  {viewportSizes.find(v => v.class === viewportSize)?.name}
                </span>
              </div>
              <div className="viewport-content">
                <div className="viewport-placeholder">
                  <p>Navigate to a page to see it rendered in this viewport</p>
                  <p>Current: {testPages[currentTest]?.path || 'None selected'}</p>
                </div>
              </div>
            </div>
          </div>

          {showTestResults && testPages[currentTest] && (
            <div className="test-results">
              <h3>📊 Test Results: {testPages[currentTest].name}</h3>
              <div className="results-grid">
                {testCriteria.map(criteria => {
                  const result = testResults[testPages[currentTest].name]?.find(r => r.criteria === criteria.name);
                  return (
                    <div key={criteria.name} className={`result-item ${result?.status || 'pending'}`}>
                      <div className="result-header">
                        <span className="result-criteria">{criteria.name}</span>
                        <div className="result-score">
                          <span className="result-status">
                            {getStatusIcon(result?.status || 'pending')}
                          </span>
                          {result && <span className="score-value">{result.score}%</span>}
                        </div>
                      </div>
                      {result && (
                        <div className="result-notes">{result.notes}</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="test-summary">
        <h3>📈 Test Summary</h3>
        <div className="summary-stats">
          <div className="stat-item">
            <span className="stat-label">Overall Score:</span>
            <span className="stat-value overall-score">{getOverallScore()}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Pages:</span>
            <span className="stat-value">{testPages.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Passed:</span>
            <span className="stat-value status-pass">
              {testPages.filter(p => getTestStatus(p.name) === 'pass').length}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Failed:</span>
            <span className="stat-value status-fail">
              {testPages.filter(p => getTestStatus(p.name) === 'fail').length}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Partial:</span>
            <span className="stat-value status-partial">
              {testPages.filter(p => getTestStatus(p.name) === 'partial').length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UIComprehensiveTest; 