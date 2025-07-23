const axios = require('axios');

const API_BASE_URL = 'http://localhost:8001/api/v1';

async function testBrandAuth() {
  console.log('🧪 Testing Brand Signup and Login...\n');

  try {
    // Test 1: Brand Signup
    console.log('1️⃣ Testing brand signup...');
    const signupData = {
      email: `brand_${Date.now()}@test.com`,
      full_name: 'Test Brand User',
      password: 'testpass123',
      brand_name: 'Test Brand Company',
      role: 'brand_user'
    };
    
    const signupResponse = await axios.post(`${API_BASE_URL}/auth/signup`, signupData);
    console.log('✅ Brand signup successful:', {
      user_id: signupResponse.data.user.id,
      email: signupResponse.data.user.email,
      role: signupResponse.data.user.role,
      has_token: !!signupResponse.data.access_token
    });
    console.log('');

    // Test 2: Brand Login
    console.log('2️⃣ Testing brand login...');
    const loginForm = new URLSearchParams();
    loginForm.append('username', signupData.email);
    loginForm.append('password', signupData.password);
    
    const loginResponse = await axios.post(`${API_BASE_URL}/login/access-token`, loginForm, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    console.log('✅ Brand login successful:', {
      user_id: loginResponse.data.user.id,
      email: loginResponse.data.user.email,
      role: loginResponse.data.user.role,
      has_token: !!loginResponse.data.access_token
    });
    console.log('');

    // Test 3: Get Current User (Brand User)
    console.log('3️⃣ Testing get current user (brand user)...');
    const token = loginResponse.data.access_token;
    const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Get current user successful:', {
      id: userResponse.data.id,
      email: userResponse.data.email,
      full_name: userResponse.data.full_name,
      role: userResponse.data.role
    });
    console.log('');

    // Test 4: Brand Dashboard Access
    console.log('4️⃣ Testing brand dashboard access...');
    const dashboardResponse = await axios.get(`${API_BASE_URL}/brand/dashboard`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Brand dashboard access successful:', {
      has_brand: !!dashboardResponse.data.brand,
      brand_name: dashboardResponse.data.brand?.name,
      tickets_count: dashboardResponse.data.tickets?.length || 0,
      stats: dashboardResponse.data.stats
    });
    console.log('');

    // Test 5: Create a ticket for the brand
    console.log('5️⃣ Testing ticket creation for brand...');
    const ticketData = {
      title: 'Test Complaint for Brand',
      description: 'This is a test complaint for the brand user',
      priority: 'high'
    };
    
    const ticketResponse = await axios.post(`${API_BASE_URL}/tickets`, ticketData, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Ticket creation successful:', {
      ticket_id: ticketResponse.data.id,
      title: ticketResponse.data.title,
      status: ticketResponse.data.status,
      priority: ticketResponse.data.priority
    });
    console.log('');

    console.log('🎉 All brand authentication tests passed successfully!');
    console.log('\n📋 Summary:');
    console.log('✅ Brand signup with brand creation');
    console.log('✅ Brand login with JWT token');
    console.log('✅ User profile retrieval');
    console.log('✅ Brand dashboard access');
    console.log('✅ Ticket creation for brand');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
    if (error.response?.status) {
      console.error('Status:', error.response.status);
    }
  }
}

// Run the test
testBrandAuth(); 