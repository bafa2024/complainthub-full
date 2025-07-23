const axios = require('axios');

const BASE_URL = 'http://localhost:8001';

async function testEndpoint(method, endpoint, data = null, token = null) {
  try {
    const config = {
      method,
      url: `${BASE_URL}${endpoint}`,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (data) {
      config.data = data;
    }

    const response = await axios(config);
    return { success: true, data: response.data, status: response.status };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data || error.message,
      status: error.response?.status
    };
  }
}

async function runQuickTest() {
  console.log('🚀 Quick Brand Assignment Test');
  console.log('================================');

  // Test 1: Health check
  console.log('\n1. Testing backend health...');
  const health = await testEndpoint('GET', '/health');
  console.log(health.success ? '✅ Backend running' : '❌ Backend not running');

  // Test 2: Admin login
  console.log('\n2. Testing admin login...');
  const adminLogin = await testEndpoint('POST', '/api/v1/login/access-token', {
    username: 'admin@complainthub.com',
    password: 'admin123'
  });
  
  if (adminLogin.success) {
    console.log('✅ Admin login successful');
    const adminToken = adminLogin.data.access_token;
    
    // Test 3: Get all users
    console.log('\n3. Testing get all users...');
    const users = await testEndpoint('GET', '/api/v1/admin/users', null, adminToken);
    console.log(users.success ? '✅ Users endpoint works' : '❌ Users endpoint failed');
    if (users.success) {
      console.log(`Found ${users.data.length} users`);
      users.data.forEach(user => {
        console.log(`- ${user.email} (${user.role}) - Brand ID: ${user.brand_id || 'None'}`);
      });
    }

    // Test 4: Get all brands
    console.log('\n4. Testing get all brands...');
    const brands = await testEndpoint('GET', '/api/v1/admin/brands', null, adminToken);
    console.log(brands.success ? '✅ Brands endpoint works' : '❌ Brands endpoint failed');
    if (brands.success) {
      console.log(`Found ${brands.data.length} brands`);
      brands.data.forEach(brand => {
        console.log(`- ${brand.name} (ID: ${brand.id})`);
      });
    }

    // Test 5: Try to assign brand to user
    if (users.success && brands.success && users.data.length > 0 && brands.data.length > 0) {
      console.log('\n5. Testing brand assignment...');
      const userId = users.data[0].id;
      const brandId = brands.data[0].id;
      
      const assignment = await testEndpoint('POST', `/api/v1/admin/users/${userId}/assign-brand`, {
        brand_id: brandId
      }, adminToken);
      
      console.log(assignment.success ? '✅ Brand assignment works' : '❌ Brand assignment failed');
      if (!assignment.success) {
        console.log('Error:', assignment.error);
      }
    }

  } else {
    console.log('❌ Admin login failed:', adminLogin.error);
  }
}

runQuickTest().catch(console.error); 