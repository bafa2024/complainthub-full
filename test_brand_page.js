const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';

// Test data
const testUser = {
  email: 'test@example.com',
  password: 'testpassword123',
  full_name: 'Test User'
};

const testBrand = {
  name: 'Test Brand',
  description: 'A test brand for testing purposes',
  support_email: 'test@example.com',
  industry: 'Technology',
  logo_url: 'https://example.com/logo.png',
  contact_info: 'Contact us at test@example.com'
};

let authToken = null;
let createdBrandId = null;

// Helper function to make authenticated requests
const makeAuthRequest = async (method, endpoint, data = null) => {
  const config = {
    method,
    url: `${BASE_URL}${endpoint}`,
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    },
    ...(data && { data })
  };
  
  try {
    const response = await axios(config);
    return response.data;
  } catch (error) {
    console.error(`Error in ${method} ${endpoint}:`, error.response?.data || error.message);
    throw error;
  }
};

// Test functions
const testHealthCheck = async () => {
  console.log('🔍 Testing health check...');
  try {
    const response = await axios.get('http://localhost:8001/health');
    console.log('✅ Health check passed:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
};

const testUserSignup = async () => {
  console.log('🔍 Testing user signup...');
  try {
    const response = await makeAuthRequest('POST', '/signup', {
      email: testUser.email,
      full_name: testUser.full_name,
      password: testUser.password,
      role: 'brand_user'
    });
    
    authToken = response.access_token;
    console.log('✅ User signup successful');
    return true;
  } catch (error) {
    if (error.response?.status === 400 && error.response?.data?.error?.includes('already exists')) {
      console.log('⚠️ User already exists, proceeding with login...');
      return await testUserLogin();
    }
    console.error('❌ User signup failed:', error.response?.data || error.message);
    return false;
  }
};

const testUserLogin = async () => {
  console.log('🔍 Testing user login...');
  try {
    const response = await makeAuthRequest('POST', '/login/access-token', {
      username: testUser.email,
      password: testUser.password
    });
    
    authToken = response.access_token;
    console.log('✅ User login successful');
    return true;
  } catch (error) {
    console.error('❌ User login failed:', error.response?.data || error.message);
    return false;
  }
};

const testGetCurrentUser = async () => {
  console.log('🔍 Testing get current user...');
  try {
    const user = await makeAuthRequest('GET', '/auth/me');
    console.log('✅ Get current user successful:', user);
    return true;
  } catch (error) {
    console.error('❌ Get current user failed:', error.response?.data || error.message);
    return false;
  }
};

const testCreateBrand = async () => {
  console.log('🔍 Testing brand creation...');
  try {
    const brand = await makeAuthRequest('POST', '/admin/brands', testBrand);
    createdBrandId = brand.id;
    console.log('✅ Brand creation successful:', brand);
    return true;
  } catch (error) {
    console.error('❌ Brand creation failed:', error.response?.data || error.message);
    return false;
  }
};

const testGetBrands = async () => {
  console.log('🔍 Testing get brands...');
  try {
    const brands = await makeAuthRequest('GET', '/brands');
    console.log('✅ Get brands successful:', brands);
    return true;
  } catch (error) {
    console.error('❌ Get brands failed:', error.response?.data || error.message);
    return false;
  }
};

const testGetBrandById = async () => {
  if (!createdBrandId) {
    console.log('⚠️ No brand ID available, skipping get brand by ID test');
    return false;
  }
  
  console.log('🔍 Testing get brand by ID...');
  try {
    const brand = await makeAuthRequest('GET', `/brands/${createdBrandId}`);
    console.log('✅ Get brand by ID successful:', brand);
    return true;
  } catch (error) {
    console.error('❌ Get brand by ID failed:', error.response?.data || error.message);
    return false;
  }
};

const testUpdateBrand = async () => {
  if (!createdBrandId) {
    console.log('⚠️ No brand ID available, skipping update brand test');
    return false;
  }
  
  console.log('🔍 Testing brand update...');
  try {
    const updateData = {
      name: 'Updated Test Brand',
      description: 'Updated description',
      industry: 'Updated Technology'
    };
    
    const brand = await makeAuthRequest('PUT', `/brands/${createdBrandId}`, updateData);
    console.log('✅ Brand update successful:', brand);
    return true;
  } catch (error) {
    console.error('❌ Brand update failed:', error.response?.data || error.message);
    return false;
  }
};

const testGetBrandDashboard = async () => {
  console.log('🔍 Testing brand dashboard...');
  try {
    const dashboard = await makeAuthRequest('GET', '/brand/dashboard');
    console.log('✅ Brand dashboard successful:', dashboard);
    return true;
  } catch (error) {
    console.error('❌ Brand dashboard failed:', error.response?.data || error.message);
    return false;
  }
};

const testBillingEndpoints = async () => {
  console.log('🔍 Testing billing endpoints...');
  
  try {
    const summary = await makeAuthRequest('GET', '/billing/summary');
    console.log('✅ Billing summary successful:', summary);
    
    const transactions = await makeAuthRequest('GET', '/billing/transactions');
    console.log('✅ Billing transactions successful:', transactions);
    
    const plans = await makeAuthRequest('GET', '/billing/plans');
    console.log('✅ Billing plans successful:', plans);
    
    return true;
  } catch (error) {
    console.error('❌ Billing endpoints failed:', error.response?.data || error.message);
    return false;
  }
};

const testAdminEndpoints = async () => {
  console.log('🔍 Testing admin endpoints...');
  
  try {
    const adminBrands = await makeAuthRequest('GET', '/admin/brands');
    console.log('✅ Admin brands successful:', adminBrands);
    
    const adminDashboard = await makeAuthRequest('GET', '/admin/dashboard');
    console.log('✅ Admin dashboard successful:', adminDashboard);
    
    return true;
  } catch (error) {
    if (error.response?.status === 403) {
      console.log('⚠️ Admin access denied (expected for non-admin user)');
      return true;
    }
    console.error('❌ Admin endpoints failed:', error.response?.data || error.message);
    return false;
  }
};

const testDeleteBrand = async () => {
  if (!createdBrandId) {
    console.log('⚠️ No brand ID available, skipping delete brand test');
    return false;
  }
  
  console.log('🔍 Testing brand deletion...');
  try {
    await makeAuthRequest('DELETE', `/admin/brands/${createdBrandId}`);
    console.log('✅ Brand deletion successful');
    return true;
  } catch (error) {
    console.error('❌ Brand deletion failed:', error.response?.data || error.message);
    return false;
  }
};

// Main test runner
const runTests = async () => {
  console.log('🚀 Starting Brand Page Tests...\n');
  
  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'User Signup/Login', fn: testUserSignup },
    { name: 'Get Current User', fn: testGetCurrentUser },
    { name: 'Create Brand', fn: testCreateBrand },
    { name: 'Get Brands', fn: testGetBrands },
    { name: 'Get Brand by ID', fn: testGetBrandById },
    { name: 'Update Brand', fn: testUpdateBrand },
    { name: 'Brand Dashboard', fn: testGetBrandDashboard },
    { name: 'Billing Endpoints', fn: testBillingEndpoints },
    { name: 'Admin Endpoints', fn: testAdminEndpoints },
    { name: 'Delete Brand', fn: testDeleteBrand }
  ];
  
  const results = [];
  
  for (const test of tests) {
    console.log(`\n📋 Running: ${test.name}`);
    console.log('─'.repeat(50));
    
    try {
      const success = await test.fn();
      results.push({ name: test.name, success });
      
      if (success) {
        console.log(`✅ ${test.name}: PASSED`);
      } else {
        console.log(`❌ ${test.name}: FAILED`);
      }
    } catch (error) {
      console.log(`❌ ${test.name}: ERROR - ${error.message}`);
      results.push({ name: test.name, success: false, error: error.message });
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('='.repeat(60));
  
  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(`Total Tests: ${results.length}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Success Rate: ${((passed / results.length) * 100).toFixed(1)}%`);
  
  if (failed > 0) {
    console.log('\n❌ Failed Tests:');
    results.filter(r => !r.success).forEach(r => {
      console.log(`  - ${r.name}${r.error ? `: ${r.error}` : ''}`);
    });
  }
  
  console.log('\n🎯 Brand Page Test Complete!');
  
  if (passed === results.length) {
    console.log('🎉 All tests passed! The brand page is working correctly.');
  } else {
    console.log('⚠️ Some tests failed. Please check the errors above.');
  }
};

// Run tests
runTests().catch(console.error); 