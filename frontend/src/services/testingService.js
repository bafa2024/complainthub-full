import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

class TestingService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
    });
  }

  // Backend API Tests
  async testBackendHealth() {
    try {
      const response = await this.api.get('/health');
      return {
        success: true,
        data: response.data,
        status: response.status,
        responseTime: response.headers['x-response-time'] || 'unknown'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  async testBackendDatabase() {
    try {
      const response = await this.api.get('/api/v1/testing/database');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  async testBackendAPI() {
    try {
      const response = await this.api.get('/api/v1/testing/api');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  async testBackendDataFlow() {
    try {
      const response = await this.api.get('/api/v1/testing/data-flow');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  async testBackendCRUD() {
    try {
      const response = await this.api.get('/api/v1/testing/crud');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  async testBackendMockData() {
    try {
      const response = await this.api.get('/api/v1/testing/mock-data');
      return {
        success: true,
        data: response.data,
        status: response.status
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        status: error.response?.status || 'unknown'
      };
    }
  }

  // Frontend Tests
  testFrontendLocalStorage() {
    try {
      const testKey = 'frontend_test_key';
      const testValue = 'test_value_' + Date.now();
      
      // Test set
      localStorage.setItem(testKey, testValue);
      
      // Test get
      const retrievedValue = localStorage.getItem(testKey);
      
      // Test remove
      localStorage.removeItem(testKey);
      
      // Verify removal
      const afterRemoval = localStorage.getItem(testKey);
      
      return {
        success: true,
        data: {
          set: retrievedValue === testValue,
          get: retrievedValue === testValue,
          remove: afterRemoval === null,
          allTests: retrievedValue === testValue && afterRemoval === null
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  testFrontendSessionStorage() {
    try {
      const testKey = 'frontend_session_test_key';
      const testValue = 'session_test_value_' + Date.now();
      
      // Test set
      sessionStorage.setItem(testKey, testValue);
      
      // Test get
      const retrievedValue = sessionStorage.getItem(testKey);
      
      // Test remove
      sessionStorage.removeItem(testKey);
      
      // Verify removal
      const afterRemoval = sessionStorage.getItem(testKey);
      
      return {
        success: true,
        data: {
          set: retrievedValue === testValue,
          get: retrievedValue === testValue,
          remove: afterRemoval === null,
          allTests: retrievedValue === testValue && afterRemoval === null
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  testFrontendCookies() {
    try {
      const testKey = 'frontend_cookie_test';
      const testValue = 'cookie_test_value_' + Date.now();
      
      // Test set
      document.cookie = `${testKey}=${testValue}; path=/`;
      
      // Test get
      const cookies = document.cookie.split(';');
      const testCookie = cookies.find(cookie => cookie.trim().startsWith(`${testKey}=`));
      const retrievedValue = testCookie ? testCookie.split('=')[1] : null;
      
      // Test remove (set expiration to past)
      document.cookie = `${testKey}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      
      // Verify removal
      const cookiesAfterRemoval = document.cookie.split(';');
      const testCookieAfterRemoval = cookiesAfterRemoval.find(cookie => cookie.trim().startsWith(`${testKey}=`));
      
      return {
        success: true,
        data: {
          set: retrievedValue === testValue,
          get: retrievedValue === testValue,
          remove: !testCookieAfterRemoval,
          allTests: retrievedValue === testValue && !testCookieAfterRemoval
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  testFrontendAPIConnectivity() {
    return new Promise(async (resolve) => {
      const results = {
        apiReachable: false,
        corsEnabled: false,
        responseTime: 0,
        endpoints: {}
      };

      try {
        const startTime = Date.now();
        const response = await this.api.get('/health');
        const endTime = Date.now();
        
        results.apiReachable = response.status === 200;
        results.responseTime = endTime - startTime;
        
        // Test CORS
        try {
          const corsResponse = await this.api.options('/health');
          results.corsEnabled = true;
        } catch (corsError) {
          results.corsEnabled = false;
        }
        
        // Test various endpoints
        const endpoints = ['/api/v1/users', '/api/v1/brands', '/api/v1/tickets'];
        for (const endpoint of endpoints) {
          try {
            const endpointResponse = await this.api.get(endpoint);
            results.endpoints[endpoint] = endpointResponse.status;
          } catch (error) {
            results.endpoints[endpoint] = error.response?.status || 'error';
          }
        }
        
        resolve({
          success: true,
          data: results
        });
      } catch (error) {
        resolve({
          success: false,
          error: error.message,
          data: results
        });
      }
    });
  }

  testFrontendDataValidation() {
    const testCases = [
      {
        name: 'Email Validation',
        test: (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
        validInput: 'test@example.com',
        invalidInput: 'invalid-email'
      },
      {
        name: 'Phone Validation',
        test: (phone) => /^\+?[\d\s\-\(\)]{10,}$/.test(phone),
        validInput: '+1234567890',
        invalidInput: '123'
      },
      {
        name: 'Password Strength',
        test: (password) => password.length >= 8,
        validInput: 'strongpassword123',
        invalidInput: 'weak'
      }
    ];

    const results = {};
    
    testCases.forEach(testCase => {
      const validResult = testCase.test(testCase.validInput);
      const invalidResult = testCase.test(testCase.invalidInput);
      
      results[testCase.name] = {
        validInputTest: validResult,
        invalidInputTest: !invalidResult,
        overall: validResult && !invalidResult
      };
    });

    return {
      success: true,
      data: results
    };
  }

  testFrontendResponsiveDesign() {
    const breakpoints = {
      mobile: 768,
      tablet: 1024,
      desktop: 1200
    };

    const currentWidth = window.innerWidth;
    const currentHeight = window.innerHeight;

    return {
      success: true,
      data: {
        currentWidth,
        currentHeight,
        breakpoints,
        isMobile: currentWidth < breakpoints.mobile,
        isTablet: currentWidth >= breakpoints.mobile && currentWidth < breakpoints.tablet,
        isDesktop: currentWidth >= breakpoints.tablet,
        viewport: {
          width: currentWidth,
          height: currentHeight,
          ratio: (currentWidth / currentHeight).toFixed(2)
        }
      }
    };
  }

  // Comprehensive test runner
  async runAllTests() {
    const results = {
      backend: {},
      frontend: {},
      timestamp: new Date().toISOString(),
      summary: {
        total: 0,
        passed: 0,
        failed: 0
      }
    };

    // Backend tests
    const backendTests = [
      { name: 'Health Check', test: () => this.testBackendHealth() },
      { name: 'Database Connection', test: () => this.testBackendDatabase() },
      { name: 'API Connectivity', test: () => this.testBackendAPI() },
      { name: 'Data Flow', test: () => this.testBackendDataFlow() },
      { name: 'CRUD Operations', test: () => this.testBackendCRUD() },
      { name: 'Mock Data Generation', test: () => this.testBackendMockData() }
    ];

    for (const test of backendTests) {
      try {
        const result = await test.test();
        results.backend[test.name] = result;
        results.summary.total++;
        if (result.success) {
          results.summary.passed++;
        } else {
          results.summary.failed++;
        }
      } catch (error) {
        results.backend[test.name] = {
          success: false,
          error: error.message
        };
        results.summary.total++;
        results.summary.failed++;
      }
    }

    // Frontend tests
    const frontendTests = [
      { name: 'Local Storage', test: () => this.testFrontendLocalStorage() },
      { name: 'Session Storage', test: () => this.testFrontendSessionStorage() },
      { name: 'Cookies', test: () => this.testFrontendCookies() },
      { name: 'API Connectivity', test: () => this.testFrontendAPIConnectivity() },
      { name: 'Data Validation', test: () => this.testFrontendDataValidation() },
      { name: 'Responsive Design', test: () => this.testFrontendResponsiveDesign() }
    ];

    for (const test of frontendTests) {
      try {
        const result = await test.test();
        results.frontend[test.name] = result;
        results.summary.total++;
        if (result.success) {
          results.summary.passed++;
        } else {
          results.summary.failed++;
        }
      } catch (error) {
        results.frontend[test.name] = {
          success: false,
          error: error.message
        };
        results.summary.total++;
        results.summary.failed++;
      }
    }

    return results;
  }
}

export default new TestingService(); 