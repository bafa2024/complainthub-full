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

async function testBrandProfile() {
  console.log('🔍 Testing Brand Profile Functionality');
  console.log('=====================================');

  // Step 1: Test backend health
  console.log('\n1️⃣ Backend Health Check...');
  const health = await testEndpoint('GET', '/health');
  console.log(health.success ? '✅ Backend running' : '❌ Backend not running');
  if (!health.success) return;

  // Step 2: Admin login
  console.log('\n2️⃣ Admin Login...');
  const adminLogin = await testEndpoint('POST', '/api/v1/login/access-token', {
    username: 'admin@complainthub.com',
    password: 'admin123'
  });

  if (!adminLogin.success) {
    console.log('❌ Admin login failed:', adminLogin.error);
    return;
  }

  console.log('✅ Admin login successful');
  const adminToken = adminLogin.data.access_token;

  // Step 3: Get all users
  console.log('\n3️⃣ Get All Users...');
  const users = await testEndpoint('GET', '/api/v1/admin/users', null, adminToken);
  
  if (!users.success) {
    console.log('❌ Get users failed:', users.error);
    return;
  }

  console.log(`✅ Found ${users.data.length} users:`);
  users.data.forEach(user => {
    console.log(`   - ${user.email} (${user.role}) - Brand ID: ${user.brand_id || 'None'}`);
  });

  // Step 4: Get all brands
  console.log('\n4️⃣ Get All Brands...');
  const brands = await testEndpoint('GET', '/api/v1/admin/brands', null, adminToken);
  
  if (!brands.success) {
    console.log('❌ Get brands failed:', brands.error);
    return;
  }

  console.log(`✅ Found ${brands.data.length} brands:`);
  brands.data.forEach(brand => {
    console.log(`   - ${brand.name} (ID: ${brand.id})`);
  });

  // Step 5: Find a brand user and assign a brand
  console.log('\n5️⃣ Brand Assignment Test...');
  const brandUsers = users.data.filter(user => user.role === 'brand_user');
  
  if (brandUsers.length === 0) {
    console.log('❌ No brand users found. Creating one...');
    
    const newUser = await testEndpoint('POST', '/api/v1/auth/signup', {
      email: 'branduser@test.com',
      password: 'password123',
      full_name: 'Test Brand User',
      role: 'brand_user'
    });

    if (newUser.success) {
      console.log('✅ Created new brand user');
      brandUsers.push(newUser.data.user);
    } else {
      console.log('❌ Failed to create brand user:', newUser.error);
      return;
    }
  }

  // Assign brand to first brand user
  if (brandUsers.length > 0 && brands.data.length > 0) {
    const targetUser = brandUsers[0];
    const targetBrand = brands.data[0];
    
    console.log(`Assigning brand "${targetBrand.name}" to user "${targetUser.email}"`);
    
    const assignment = await testEndpoint('POST', `/api/v1/admin/users/${targetUser.id}/assign-brand`, {
      brand_id: targetBrand.id
    }, adminToken);

    if (assignment.success) {
      console.log('✅ Brand assignment successful!');
      console.log('Updated user:', assignment.data.user);
    } else {
      console.log('❌ Brand assignment failed:', assignment.error);
      return;
    }
  }

  // Step 6: Test brand user login and profile access
  console.log('\n6️⃣ Test Brand User Profile Access...');
  const brandUserLogin = await testEndpoint('POST', '/api/v1/login/access-token', {
    username: brandUsers[0].email,
    password: 'password123'
  });

  if (brandUserLogin.success) {
    console.log('✅ Brand user login successful');
    console.log('Brand user data:', brandUserLogin.data.user);
    
    const brandUserToken = brandUserLogin.data.access_token;
    
    // Test /auth/me endpoint
    console.log('\n7️⃣ Test /auth/me endpoint...');
    const userMe = await testEndpoint('GET', '/api/v1/auth/me', null, brandUserToken);
    
    if (userMe.success) {
      console.log('✅ /auth/me successful');
      console.log('User data:', userMe.data);
      
      if (userMe.data.brand_id) {
        console.log(`✅ User has brand_id: ${userMe.data.brand_id}`);
        
        // Test getting brand details
        console.log('\n8️⃣ Test Brand Details Access...');
        const brandDetails = await testEndpoint('GET', `/api/v1/brands/${userMe.data.brand_id}`, null, brandUserToken);
        
        if (brandDetails.success) {
          console.log('✅ Brand details access successful');
          console.log('Brand data:', brandDetails.data);
        } else {
          console.log('❌ Brand details access failed:', brandDetails.error);
        }
      } else {
        console.log('❌ User does not have brand_id assigned');
      }
    } else {
      console.log('❌ /auth/me failed:', userMe.error);
    }
  } else {
    console.log('❌ Brand user login failed:', brandUserLogin.error);
  }

  // Step 7: Test brand profile update
  console.log('\n9️⃣ Test Brand Profile Update...');
  if (brandUserLogin.success && brandUserLogin.data.user.brand_id) {
    const updateData = {
      name: 'Updated Brand Name',
      support_email: 'updated@brand.com',
      industry: 'Technology',
      logo_url: 'https://updated-logo.com/logo.png'
    };
    
    const updateBrand = await testEndpoint('PUT', `/api/v1/brands/${brandUserLogin.data.user.brand_id}`, updateData, brandUserToken);
    
    if (updateBrand.success) {
      console.log('✅ Brand profile update successful');
      console.log('Updated brand:', updateBrand.data);
    } else {
      console.log('❌ Brand profile update failed:', updateBrand.error);
    }
  }
}

testBrandProfile().catch(console.error); 