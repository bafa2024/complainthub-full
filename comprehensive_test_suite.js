const axios = require('axios');

class ComprehensiveTestSuite {
  constructor() {
    this.baseURL = 'http://localhost:8001';
    this.frontendURL = 'http://localhost:5173';
    this.testResults = [];
    this.adminToken = null;
    this.brandToken = null;
    this.userToken = null;
  }

  async log(message, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${message}`);
  }

  async addResult(testName, status, details = '') {
    this.testResults.push({
      test: testName,
      status: status,
      details: details,
      timestamp: new Date().toISOString()
    });
  }

  async testBackendHealth() {
    try {
      await this.log('🧪 Testing Backend Health...');
      const response = await axios.get(`${this.baseURL}/health`);
      
      if (response.status === 200 && response.data.status === 'healthy') {
        await this.addResult('Backend Health Check', 'PASSED');
        await this.log('✅ Backend is healthy', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Backend Health Check', 'FAILED', 'Unexpected response');
        await this.log('❌ Backend health check failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Backend Health Check', 'FAILED', error.message);
      await this.log(`❌ Backend health check failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testFrontendAccessibility() {
    try {
      await this.log('🧪 Testing Frontend Accessibility...');
      const response = await axios.get(this.frontendURL);
      
      if (response.status === 200) {
        await this.addResult('Frontend Accessibility', 'PASSED');
        await this.log('✅ Frontend is accessible', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Frontend Accessibility', 'FAILED', 'Unexpected status code');
        await this.log('❌ Frontend accessibility failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Frontend Accessibility', 'FAILED', error.message);
      await this.log(`❌ Frontend accessibility failed: ${error.message}`, 'ERROR');
      return false;
      return false;
    }
  }

  async testAdminAuthentication() {
    try {
      await this.log('🧪 Testing Admin Authentication...');
      
      // Test admin login
      const loginForm = new URLSearchParams();
      loginForm.append('username', 'admin@complainthub.com');
      loginForm.append('password', 'admin123');

      const response = await axios.post(`${this.baseURL}/api/v1/login/access-token`, loginForm, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      if (response.status === 200 && response.data.access_token) {
        this.adminToken = response.data.access_token;
        await this.addResult('Admin Authentication', 'PASSED');
        await this.log('✅ Admin authentication successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Admin Authentication', 'FAILED', 'No token received');
        await this.log('❌ Admin authentication failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Admin Authentication', 'FAILED', error.message);
      await this.log(`❌ Admin authentication failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testBrandAuthentication() {
    try {
      await this.log('🧪 Testing Brand Authentication...');
      
      // Test brand signup first
      const signupData = {
        email: 'testbrand@example.com',
        full_name: 'Test Brand',
        password: 'brand123',
        brand_name: 'Test Brand Company',
        role: 'brand_user'
      };

      const signupResponse = await axios.post(`${this.baseURL}/api/v1/auth/signup`, signupData);
      
      if (signupResponse.status === 201 && signupResponse.data.access_token) {
        this.brandToken = signupResponse.data.access_token;
        await this.addResult('Brand Signup', 'PASSED');
        await this.log('✅ Brand signup successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Brand Signup', 'FAILED', 'Signup failed');
        await this.log('❌ Brand signup failed', 'ERROR');
        return false;
      }
    } catch (error) {
      if (error.response && error.response.status === 400 && error.response.data.error === 'User already exists') {
        // User exists, try login
        try {
          const loginForm = new URLSearchParams();
          loginForm.append('username', 'testbrand@example.com');
          loginForm.append('password', 'brand123');

          const loginResponse = await axios.post(`${this.baseURL}/api/v1/login/access-token`, loginForm, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          });

          if (loginResponse.status === 200 && loginResponse.data.access_token) {
            this.brandToken = loginResponse.data.access_token;
            await this.addResult('Brand Authentication', 'PASSED');
            await this.log('✅ Brand authentication successful', 'SUCCESS');
            return true;
          }
        } catch (loginError) {
          await this.addResult('Brand Authentication', 'FAILED', loginError.message);
          await this.log(`❌ Brand authentication failed: ${loginError.message}`, 'ERROR');
          return false;
        }
      } else {
        await this.addResult('Brand Authentication', 'FAILED', error.message);
        await this.log(`❌ Brand authentication failed: ${error.message}`, 'ERROR');
        return false;
      }
    }
  }

  async testUserAuthentication() {
    try {
      await this.log('🧪 Testing User Authentication...');
      
      // Test user signup
      const signupData = {
        email: 'testuser@example.com',
        full_name: 'Test User',
        password: 'user123',
        role: 'user'
      };

      const signupResponse = await axios.post(`${this.baseURL}/api/v1/auth/signup`, signupData);
      
      if (signupResponse.status === 201 && signupResponse.data.access_token) {
        this.userToken = signupResponse.data.access_token;
        await this.addResult('User Signup', 'PASSED');
        await this.log('✅ User signup successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('User Signup', 'FAILED', 'Signup failed');
        await this.log('❌ User signup failed', 'ERROR');
        return false;
      }
    } catch (error) {
      if (error.response && error.response.status === 400 && error.response.data.error === 'User already exists') {
        // User exists, try login
        try {
          const loginForm = new URLSearchParams();
          loginForm.append('username', 'testuser@example.com');
          loginForm.append('password', 'user123');

          const loginResponse = await axios.post(`${this.baseURL}/api/v1/login/access-token`, loginForm, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
          });

          if (loginResponse.status === 200 && loginResponse.data.access_token) {
            this.userToken = loginResponse.data.access_token;
            await this.addResult('User Authentication', 'PASSED');
            await this.log('✅ User authentication successful', 'SUCCESS');
            return true;
          }
        } catch (loginError) {
          await this.addResult('User Authentication', 'FAILED', loginError.message);
          await this.log(`❌ User authentication failed: ${loginError.message}`, 'ERROR');
          return false;
        }
      } else {
        await this.addResult('User Authentication', 'FAILED', error.message);
        await this.log(`❌ User authentication failed: ${error.message}`, 'ERROR');
        return false;
      }
    }
  }

  async testAdminCRUDOperations() {
    try {
      await this.log('🧪 Testing Admin CRUD Operations...');
      
      if (!this.adminToken) {
        await this.addResult('Admin CRUD Operations', 'FAILED', 'No admin token');
        return false;
      }

      const headers = { 'Authorization': `Bearer ${this.adminToken}` };

      // Test Create Brand
      const createBrandData = {
        name: 'Test Brand CRUD',
        description: 'Test brand for CRUD operations',
        support_email: 'support@testbrand.com',
        industry: 'Technology',
        logo_url: 'https://example.com/logo.png',
        contact_info: '+1234567890'
      };

      const createResponse = await axios.post(`${this.baseURL}/api/v1/admin/brands`, createBrandData, { headers });
      
      if (createResponse.status === 201) {
        const brandId = createResponse.data.id;
        await this.addResult('Admin Create Brand', 'PASSED');
        await this.log('✅ Admin create brand successful', 'SUCCESS');

        // Test Read Brand
        const readResponse = await axios.get(`${this.baseURL}/api/v1/admin/brands/${brandId}`, { headers });
        
        if (readResponse.status === 200) {
          await this.addResult('Admin Read Brand', 'PASSED');
          await this.log('✅ Admin read brand successful', 'SUCCESS');

          // Test Update Brand
          const updateData = {
            name: 'Updated Test Brand CRUD',
            description: 'Updated description'
          };

          const updateResponse = await axios.put(`${this.baseURL}/api/v1/admin/brands/${brandId}`, updateData, { headers });
          
          if (updateResponse.status === 200) {
            await this.addResult('Admin Update Brand', 'PASSED');
            await this.log('✅ Admin update brand successful', 'SUCCESS');

            // Test Delete Brand
            const deleteResponse = await axios.delete(`${this.baseURL}/api/v1/admin/brands/${brandId}`, { headers });
            
            if (deleteResponse.status === 200) {
              await this.addResult('Admin Delete Brand', 'PASSED');
              await this.log('✅ Admin delete brand successful', 'SUCCESS');
              return true;
            } else {
              await this.addResult('Admin Delete Brand', 'FAILED', 'Delete failed');
              return false;
            }
          } else {
            await this.addResult('Admin Update Brand', 'FAILED', 'Update failed');
            return false;
          }
        } else {
          await this.addResult('Admin Read Brand', 'FAILED', 'Read failed');
          return false;
        }
      } else {
        await this.addResult('Admin Create Brand', 'FAILED', 'Create failed');
        return false;
      }
    } catch (error) {
      await this.addResult('Admin CRUD Operations', 'FAILED', error.message);
      await this.log(`❌ Admin CRUD operations failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testPublicComplaintForm() {
    try {
      await this.log('🧪 Testing Public Complaint Form...');
      
      const complaintData = {
        fullName: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1234567890',
        brandName: 'Test Company',
        title: 'Test Complaint',
        description: 'This is a test complaint for testing purposes',
        category: 'Service',
        priority: 'medium',
        isAnonymous: false
      };

      const response = await axios.post(`${this.baseURL}/api/v1/public/tickets`, complaintData);
      
      if (response.status === 201 && response.data.ticket_number) {
        await this.addResult('Public Complaint Form', 'PASSED');
        await this.log('✅ Public complaint form successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Public Complaint Form', 'FAILED', 'No ticket number received');
        await this.log('❌ Public complaint form failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Public Complaint Form', 'FAILED', error.message);
      await this.log(`❌ Public complaint form failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testAdminDashboard() {
    try {
      await this.log('🧪 Testing Admin Dashboard...');
      
      if (!this.adminToken) {
        await this.addResult('Admin Dashboard', 'FAILED', 'No admin token');
        return false;
      }

      const headers = { 'Authorization': `Bearer ${this.adminToken}` };
      const response = await axios.get(`${this.baseURL}/api/v1/admin/dashboard`, { headers });
      
      if (response.status === 200 && response.data.overview) {
        await this.addResult('Admin Dashboard', 'PASSED');
        await this.log('✅ Admin dashboard successful', 'SUCCESS');
        await this.log(`📊 Dashboard stats: ${JSON.stringify(response.data.overview)}`, 'INFO');
        return true;
      } else {
        await this.addResult('Admin Dashboard', 'FAILED', 'No overview data');
        await this.log('❌ Admin dashboard failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Admin Dashboard', 'FAILED', error.message);
      await this.log(`❌ Admin dashboard failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testAdminAnalytics() {
    try {
      await this.log('🧪 Testing Admin Analytics...');
      
      if (!this.adminToken) {
        await this.addResult('Admin Analytics', 'FAILED', 'No admin token');
        return false;
      }

      const headers = { 'Authorization': `Bearer ${this.adminToken}` };
      const response = await axios.get(`${this.baseURL}/api/v1/admin/analytics`, { headers });
      
      if (response.status === 200) {
        await this.addResult('Admin Analytics', 'PASSED');
        await this.log('✅ Admin analytics successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Admin Analytics', 'FAILED', 'Analytics failed');
        await this.log('❌ Admin analytics failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Admin Analytics', 'FAILED', error.message);
      await this.log(`❌ Admin analytics failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testUserDashboard() {
    try {
      await this.log('🧪 Testing User Dashboard...');
      
      if (!this.userToken) {
        await this.addResult('User Dashboard', 'FAILED', 'No user token');
        return false;
      }

      const headers = { 'Authorization': `Bearer ${this.userToken}` };
      const response = await axios.get(`${this.baseURL}/api/v1/user/dashboard`, { headers });
      
      if (response.status === 200 && response.data.user) {
        await this.addResult('User Dashboard', 'PASSED');
        await this.log('✅ User dashboard successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('User Dashboard', 'FAILED', 'No user data');
        await this.log('❌ User dashboard failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('User Dashboard', 'FAILED', error.message);
      await this.log(`❌ User dashboard failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testBrandDashboard() {
    try {
      await this.log('🧪 Testing Brand Dashboard...');
      
      if (!this.brandToken) {
        await this.addResult('Brand Dashboard', 'FAILED', 'No brand token');
        return false;
      }

      const headers = { 'Authorization': `Bearer ${this.brandToken}` };
      const response = await axios.get(`${this.baseURL}/api/v1/brand/dashboard`, { headers });
      
      if (response.status === 200 && response.data.brand) {
        await this.addResult('Brand Dashboard', 'PASSED');
        await this.log('✅ Brand dashboard successful', 'SUCCESS');
        return true;
      } else {
        await this.addResult('Brand Dashboard', 'FAILED', 'No brand data');
        await this.log('❌ Brand dashboard failed', 'ERROR');
        return false;
      }
    } catch (error) {
      await this.addResult('Brand Dashboard', 'FAILED', error.message);
      await this.log(`❌ Brand dashboard failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async testRoleBasedAccess() {
    try {
      await this.log('🧪 Testing Role-Based Access Control...');
      
      if (!this.adminToken || !this.brandToken || !this.userToken) {
        await this.addResult('Role-Based Access Control', 'FAILED', 'Missing tokens');
        return false;
      }

      // Test admin accessing admin endpoints
      const adminHeaders = { 'Authorization': `Bearer ${this.adminToken}` };
      const adminResponse = await axios.get(`${this.baseURL}/api/v1/admin/brands`, adminHeaders);
      
      if (adminResponse.status === 200) {
        await this.addResult('Admin Access to Admin Endpoints', 'PASSED');
      } else {
        await this.addResult('Admin Access to Admin Endpoints', 'FAILED', 'Access denied');
        return false;
      }

      // Test brand user accessing admin endpoints (should fail)
      try {
        const brandHeaders = { 'Authorization': `Bearer ${this.brandToken}` };
        await axios.get(`${this.baseURL}/api/v1/admin/brands`, brandHeaders);
        await this.addResult('Brand Access to Admin Endpoints', 'FAILED', 'Should be denied');
        return false;
      } catch (error) {
        if (error.response && error.response.status === 403) {
          await this.addResult('Brand Access to Admin Endpoints', 'PASSED', 'Correctly denied');
        } else {
          await this.addResult('Brand Access to Admin Endpoints', 'FAILED', 'Unexpected error');
          return false;
        }
      }

      // Test user accessing admin endpoints (should fail)
      try {
        const userHeaders = { 'Authorization': `Bearer ${this.userToken}` };
        await axios.get(`${this.baseURL}/api/v1/admin/brands`, userHeaders);
        await this.addResult('User Access to Admin Endpoints', 'FAILED', 'Should be denied');
        return false;
      } catch (error) {
        if (error.response && error.response.status === 403) {
          await this.addResult('User Access to Admin Endpoints', 'PASSED', 'Correctly denied');
        } else {
          await this.addResult('User Access to Admin Endpoints', 'FAILED', 'Unexpected error');
          return false;
        }
      }

      await this.log('✅ Role-based access control successful', 'SUCCESS');
      return true;
    } catch (error) {
      await this.addResult('Role-Based Access Control', 'FAILED', error.message);
      await this.log(`❌ Role-based access control failed: ${error.message}`, 'ERROR');
      return false;
    }
  }

  async generateReport() {
    await this.log('\n📊 GENERATING COMPREHENSIVE TEST REPORT', 'REPORT');
    await this.log('=' * 60, 'REPORT');
    
    const passed = this.testResults.filter(r => r.status === 'PASSED').length;
    const failed = this.testResults.filter(r => r.status === 'FAILED').length;
    const total = this.testResults.length;
    const successRate = total > 0 ? ((passed / total) * 100).toFixed(2) : 0;

    await this.log(`\n📈 TEST SUMMARY:`, 'REPORT');
    await this.log(`Total Tests: ${total}`, 'REPORT');
    await this.log(`Passed: ${passed}`, 'REPORT');
    await this.log(`Failed: ${failed}`, 'REPORT');
    await this.log(`Success Rate: ${successRate}%`, 'REPORT');

    await this.log(`\n✅ PASSED TESTS:`, 'REPORT');
    this.testResults.filter(r => r.status === 'PASSED').forEach(result => {
      console.log(`  ✓ ${result.test}`);
    });

    if (failed > 0) {
      await this.log(`\n❌ FAILED TESTS:`, 'REPORT');
      this.testResults.filter(r => r.status === 'FAILED').forEach(result => {
        console.log(`  ✗ ${result.test}: ${result.details}`);
      });
    }

    await this.log(`\n🎯 SRS COMPLIANCE ASSESSMENT:`, 'REPORT');
    await this.log(`✅ IMPLEMENTED FEATURES:`, 'REPORT');
    await this.log(`  • Basic Authentication System`, 'REPORT');
    await this.log(`  • Admin Portal with CRUD operations`, 'REPORT');
    await this.log(`  • Public Complaint Form`, 'REPORT');
    await this.log(`  • Role-based Access Control`, 'REPORT');
    await this.log(`  • Basic Dashboard Analytics`, 'REPORT');
    await this.log(`  • Frontend Routing & Navigation`, 'REPORT');

    await this.log(`\n❌ MISSING CRITICAL SRS FEATURES:`, 'REPORT');
    await this.log(`  • AI-Powered Conversational BOT`, 'REPORT');
    await this.log(`  • Multi-channel Integration (WhatsApp, Telegram, etc.)`, 'REPORT');
    await this.log(`  • Voice Processing (STT/TTS)`, 'REPORT');
    await this.log(`  • Sentiment Analysis & Classification`, 'REPORT');
    await this.log(`  • Self-Learning AI Capability`, 'REPORT');
    await this.log(`  • Telephony Integration`, 'REPORT');
    await this.log(`  • CRM Integration & Webhooks`, 'REPORT');
    await this.log(`  • Billing & Credit Management`, 'REPORT');
    await this.log(`  • Automated Follow-up System`, 'REPORT');
    await this.log(`  • SEO Optimization`, 'REPORT');
    await this.log(`  • Multilingual Support`, 'REPORT');

    await this.log(`\n🚀 RECOMMENDED NEXT STEPS:`, 'REPORT');
    await this.log(`1. Implement AI BOT API with OpenAI integration`, 'REPORT');
    await this.log(`2. Add multi-channel messaging support`, 'REPORT');
    await this.log(`3. Integrate voice processing services`, 'REPORT');
    await this.log(`4. Implement sentiment analysis`, 'REPORT');
    await this.log(`5. Add billing and credit management`, 'REPORT');
    await this.log(`6. Create automated follow-up system`, 'REPORT');
    await this.log(`7. Implement SEO optimization`, 'REPORT');

    await this.log(`\n📋 DETAILED TEST RESULTS:`, 'REPORT');
    this.testResults.forEach((result, index) => {
      const status = result.status === 'PASSED' ? '✅' : '❌';
      console.log(`${index + 1}. ${status} ${result.test}`);
      if (result.details) {
        console.log(`   Details: ${result.details}`);
      }
    });

    await this.log(`\n🏁 TEST SUITE COMPLETED`, 'REPORT');
  }

  async runAllTests() {
    await this.log('🚀 STARTING COMPREHENSIVE TEST SUITE', 'START');
    await this.log('Testing all implemented features against SRS requirements', 'START');

    // Infrastructure Tests
    await this.testBackendHealth();
    await this.testFrontendAccessibility();

    // Authentication Tests
    await this.testAdminAuthentication();
    await this.testBrandAuthentication();
    await this.testUserAuthentication();

    // Feature Tests
    await this.testAdminCRUDOperations();
    await this.testPublicComplaintForm();
    await this.testAdminDashboard();
    await this.testAdminAnalytics();
    await this.testUserDashboard();
    await this.testBrandDashboard();
    await this.testRoleBasedAccess();

    // Generate Report
    await this.generateReport();
  }
}

// Run the comprehensive test suite
const testSuite = new ComprehensiveTestSuite();
testSuite.runAllTests().catch(error => {
  console.error('❌ Test suite failed:', error);
}); 