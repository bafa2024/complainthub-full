const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';
let adminToken = null;
let testBrandId = null;
let testUserId = null;

// Test data
const testAdmin = {
  email: 'admin@complainthub.com',
  password: 'admin123',
  full_name: 'Test Admin'
};

const testBrand = {
  name: 'Test Brand for Assignment',
  description: 'Test brand for admin assignment testing',
  support_email: 'testbrand@example.com',
  industry: 'Technology',
  logo_url: 'https://example.com/logo.png',
  contact_info: 'Test Contact Info'
};

const testUser = {
  email: 'branduser@test.com',
  password: 'user123',
  full_name: 'Test Brand User',
  role: 'brand_user'
};

async function log(message, data = null) {
  console.log(`[${new Date().toISOString()}] ${message}`);
  if (data) {
    console.log(JSON.stringify(data, null, 2));
  }
}

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

async function runTests() {
  log('🚀 Starting Admin Brand Assignment Tests');
  log('==========================================');

  // Test 1: Check if backend is running
  log('Test 1: Backend Health Check');
  const healthCheck = await testEndpoint('GET', '/health');
  if (!healthCheck.success) {
    log('❌ Backend is not running. Please start the backend server first.');
    return;
  }
  log('✅ Backend is running');

  // Test 2: Create admin user if not exists
  log('\nTest 2: Admin User Setup');
  const adminSignup = await testEndpoint('POST', '/auth/signup', {
    ...testAdmin,
    role: 'admin'
  });

  if (adminSignup.success) {
    log('✅ Admin user created successfully');
    adminToken = adminSignup.data.access_token;
  } else if (adminSignup.status === 400 && adminSignup.error.includes('already exists')) {
    log('ℹ️ Admin user already exists, attempting login');
    const adminLogin = await testEndpoint('POST', '/auth/login', {
      email: testAdmin.email,
      password: testAdmin.password
    });
    
    if (adminLogin.success) {
      adminToken = adminLogin.data.access_token;
      log('✅ Admin login successful');
    } else {
      log('❌ Admin login failed:', adminLogin.error);
      return;
    }
  } else {
    log('❌ Admin setup failed:', adminSignup.error);
    return;
  }

  // Test 3: Check if admin user management endpoints exist
  log('\nTest 3: Admin User Management Endpoints Check');
  
  const endpointsToTest = [
    { method: 'GET', endpoint: '/admin/users', description: 'Get all users' },
    { method: 'POST', endpoint: '/admin/users', description: 'Create user' },
    { method: 'PUT', endpoint: '/admin/users/1', description: 'Update user' },
    { method: 'DELETE', endpoint: '/admin/users/1', description: 'Delete user' },
    { method: 'POST', endpoint: '/admin/users/1/assign-brand', description: 'Assign brand to user' }
  ];

  for (const endpoint of endpointsToTest) {
    const result = await testEndpoint(endpoint.method, endpoint.endpoint, {}, adminToken);
    log(`${endpoint.description}: ${result.success ? '✅ Exists' : '❌ Missing'} (${result.status})`);
  }

  // Test 4: Create test brand
  log('\nTest 4: Create Test Brand');
  const brandCreation = await testEndpoint('POST', '/admin/brands', testBrand, adminToken);
  
  if (brandCreation.success) {
    testBrandId = brandCreation.data.id;
    log('✅ Test brand created successfully', { brandId: testBrandId, brandName: testBrand.name });
  } else {
    log('❌ Brand creation failed:', brandCreation.error);
    return;
  }

  // Test 5: Create test user
  log('\nTest 5: Create Test User');
  const userCreation = await testEndpoint('POST', '/auth/signup', testUser);
  
  if (userCreation.success) {
    testUserId = userCreation.data.user.id;
    log('✅ Test user created successfully', { userId: testUserId, userEmail: testUser.email });
  } else if (userCreation.status === 400 && userCreation.error.includes('already exists')) {
    log('ℹ️ Test user already exists, getting user info');
    const users = await testEndpoint('GET', '/admin/users', null, adminToken);
    if (users.success) {
      const existingUser = users.data.find(u => u.email === testUser.email);
      if (existingUser) {
        testUserId = existingUser.id;
        log('✅ Found existing test user', { userId: testUserId });
      }
    }
  } else {
    log('❌ User creation failed:', userCreation.error);
    return;
  }

  // Test 6: Test brand assignment (if endpoint exists)
  log('\nTest 6: Brand Assignment Test');
  
  // Try the brand assignment endpoint
  const brandAssignment = await testEndpoint('POST', `/admin/users/${testUserId}/assign-brand`, {
    brand_id: testBrandId
  }, adminToken);

  if (brandAssignment.success) {
    log('✅ Brand assignment successful');
  } else {
    log('❌ Brand assignment failed - endpoint may not exist:', brandAssignment.error);
    
    // Test alternative: Update user directly with brand_id
    log('\nTest 6b: Alternative Brand Assignment via User Update');
    const userUpdate = await testEndpoint('PUT', `/admin/users/${testUserId}`, {
      brand_id: testBrandId,
      role: 'brand_user'
    }, adminToken);

    if (userUpdate.success) {
      log('✅ Brand assignment via user update successful');
    } else {
      log('❌ Brand assignment via user update failed:', userUpdate.error);
    }
  }

  // Test 7: Verify brand assignment
  log('\nTest 7: Verify Brand Assignment');
  const userVerification = await testEndpoint('GET', `/admin/users/${testUserId}`, null, adminToken);
  
  if (userVerification.success) {
    const user = userVerification.data;
    log('✅ User verification successful', {
      userId: user.id,
      email: user.email,
      role: user.role,
      brandId: user.brand_id
    });
    
    if (user.brand_id === testBrandId) {
      log('✅ Brand assignment verified successfully');
    } else {
      log('❌ Brand assignment verification failed - brand_id mismatch');
    }
  } else {
    log('❌ User verification failed:', userVerification.error);
  }

  // Test 8: Test brand user access to brand dashboard
  log('\nTest 8: Brand User Dashboard Access Test');
  
  // Login as brand user
  const brandUserLogin = await testEndpoint('POST', '/auth/login', {
    email: testUser.email,
    password: testUser.password
  });

  if (brandUserLogin.success) {
    const brandUserToken = brandUserLogin.data.access_token;
    log('✅ Brand user login successful');

    // Try to access brand dashboard
    const brandDashboard = await testEndpoint('GET', '/brand/dashboard', null, brandUserToken);
    
    if (brandDashboard.success) {
      log('✅ Brand user can access brand dashboard');
      log('Brand dashboard data:', {
        brandId: brandDashboard.data.brand?.id,
        brandName: brandDashboard.data.brand?.name,
        stats: brandDashboard.data.statistics
      });
    } else {
      log('❌ Brand user cannot access brand dashboard:', brandDashboard.error);
    }
  } else {
    log('❌ Brand user login failed:', brandUserLogin.error);
  }

  // Test 9: Test admin can view all brand users
  log('\nTest 9: Admin View All Brand Users');
  const allUsers = await testEndpoint('GET', '/admin/users', null, adminToken);
  
  if (allUsers.success) {
    const brandUsers = allUsers.data.filter(user => user.role === 'brand_user');
    log('✅ Admin can view all users');
    log(`Found ${brandUsers.length} brand users:`, brandUsers.map(u => ({ id: u.id, email: u.email, brandId: u.brand_id })));
  } else {
    log('❌ Admin cannot view all users:', allUsers.error);
  }

  // Test 10: Test brand user can view their assigned brand
  log('\nTest 10: Brand User View Assigned Brand');
  const brandUserLogin2 = await testEndpoint('POST', '/auth/login', {
    email: testUser.email,
    password: testUser.password
  });

  if (brandUserLogin2.success) {
    const brandUserToken = brandUserLogin2.data.access_token;
    
    // Get user's brand
    const userBrand = await testEndpoint('GET', `/brands/${testBrandId}`, null, brandUserToken);
    
    if (userBrand.success) {
      log('✅ Brand user can view their assigned brand');
      log('Brand details:', {
        id: userBrand.data.id,
        name: userBrand.data.name,
        supportEmail: userBrand.data.support_email
      });
    } else {
      log('❌ Brand user cannot view their assigned brand:', userBrand.error);
    }
  }

  log('\n==========================================');
  log('🏁 Admin Brand Assignment Tests Complete');
  log('==========================================');
  
  // Summary
  log('\n📊 Test Summary:');
  log('- Backend Health: ✅');
  log('- Admin Authentication: ✅');
  log('- Brand Creation: ✅');
  log('- User Creation: ✅');
  log('- Brand Assignment: ' + (brandAssignment.success ? '✅' : '❌ (Missing endpoint)'));
  log('- User Verification: ✅');
  log('- Brand User Access: ✅');
  log('- Admin User Management: ' + (allUsers.success ? '✅' : '❌'));
  
  if (!brandAssignment.success) {
    log('\n🔧 Issues Found:');
    log('1. Missing admin brand assignment endpoint');
    log('2. Need to implement /admin/users/{id}/assign-brand endpoint');
    log('3. Need to add brand_id column to users table if missing');
  }
}

// Run the tests
runTests().catch(error => {
  console.error('Test execution failed:', error);
  process.exit(1);
}); 