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

async function debugBrandAssignment() {
  console.log('🔍 Debugging Brand Assignment Issue');
  console.log('====================================');

  // Step 1: Admin login
  console.log('\n1️⃣ Admin Login...');
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
  console.log('Admin user:', adminLogin.data.user);

  // Step 2: Get all users
  console.log('\n2️⃣ Get All Users...');
  const users = await testEndpoint('GET', '/api/v1/admin/users', null, adminToken);
  
  if (!users.success) {
    console.log('❌ Get users failed:', users.error);
    return;
  }

  console.log(`✅ Found ${users.data.length} users:`);
  users.data.forEach(user => {
    console.log(`   - ${user.email} (${user.role}) - Brand ID: ${user.brand_id || 'None'}`);
  });

  // Step 3: Get all brands
  console.log('\n3️⃣ Get All Brands...');
  const brands = await testEndpoint('GET', '/api/v1/admin/brands', null, adminToken);
  
  if (!brands.success) {
    console.log('❌ Get brands failed:', brands.error);
    return;
  }

  console.log(`✅ Found ${brands.data.length} brands:`);
  brands.data.forEach(brand => {
    console.log(`   - ${brand.name} (ID: ${brand.id})`);
  });

  // Step 4: Find a brand user to assign
  console.log('\n4️⃣ Find Brand User for Assignment...');
  const brandUsers = users.data.filter(user => user.role === 'brand_user');
  console.log(`Found ${brandUsers.length} brand users:`);
  brandUsers.forEach(user => {
    console.log(`   - ${user.email} - Current Brand ID: ${user.brand_id || 'None'}`);
  });

  if (brandUsers.length === 0) {
    console.log('❌ No brand users found. Creating one...');
    
    // Create a brand user
    const newUser = await testEndpoint('POST', '/api/v1/auth/signup', {
      email: 'testbranduser@example.com',
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

  // Step 5: Assign brand to user
  if (brandUsers.length > 0 && brands.data.length > 0) {
    console.log('\n5️⃣ Assign Brand to User...');
    const targetUser = brandUsers[0];
    const targetBrand = brands.data[0];
    
    console.log(`Assigning brand "${targetBrand.name}" (ID: ${targetBrand.id}) to user "${targetUser.email}" (ID: ${targetUser.id})`);
    
    const assignment = await testEndpoint('POST', `/api/v1/admin/users/${targetUser.id}/assign-brand`, {
      brand_id: targetBrand.id
    }, adminToken);

    if (assignment.success) {
      console.log('✅ Brand assignment successful!');
      console.log('Updated user:', assignment.data.user);
    } else {
      console.log('❌ Brand assignment failed:', assignment.error);
    }
  }

  // Step 6: Verify assignment by getting user again
  if (brandUsers.length > 0) {
    console.log('\n6️⃣ Verify Assignment...');
    const targetUser = brandUsers[0];
    const updatedUsers = await testEndpoint('GET', '/api/v1/admin/users', null, adminToken);
    
    if (updatedUsers.success) {
      const updatedUser = updatedUsers.data.find(u => u.id === targetUser.id);
      if (updatedUser) {
        console.log(`User ${updatedUser.email} now has brand_id: ${updatedUser.brand_id || 'None'}`);
      }
    }
  }

  // Step 7: Test brand user login and dashboard access
  console.log('\n7️⃣ Test Brand User Dashboard Access...');
  const brandUserLogin = await testEndpoint('POST', '/api/v1/login/access-token', {
    username: brandUsers[0].email,
    password: 'password123'
  });

  if (brandUserLogin.success) {
    console.log('✅ Brand user login successful');
    console.log('Brand user data:', brandUserLogin.data.user);
    
    // Test getting user's brand info
    const userBrand = await testEndpoint('GET', `/api/v1/brands/${brandUserLogin.data.user.brand_id}`, null, brandUserLogin.data.access_token);
    if (userBrand.success) {
      console.log('✅ Brand user can access their brand info:', userBrand.data);
    } else {
      console.log('❌ Brand user cannot access brand info:', userBrand.error);
    }
  } else {
    console.log('❌ Brand user login failed:', brandUserLogin.error);
  }
}

debugBrandAssignment().catch(console.error); 