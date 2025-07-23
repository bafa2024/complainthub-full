const axios = require('axios');

const API_BASE_URL = 'http://localhost:8001/api/v1';

async function testBackend() {
  console.log('🧪 Testing ComplaintHub Node.js Backend...\n');

  try {
    // Test 1: Health check
    console.log('1️⃣ Testing health check...');
    const healthResponse = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/health`);
    console.log('✅ Health check passed:', healthResponse.data);
    console.log('');

    // Test 2: Signup
    console.log('2️⃣ Testing user signup...');
    const signupData = {
      email: 'test@example.com',
      full_name: 'Test User',
      password: 'testpassword123'
    };
    
    const signupResponse = await axios.post(`${API_BASE_URL}/auth/signup`, signupData);
    console.log('✅ Signup successful:', {
      user_id: signupResponse.data.user.id,
      email: signupResponse.data.user.email,
      token: signupResponse.data.access_token.substring(0, 20) + '...'
    });
    console.log('');

    // Test 3: Login
    console.log('3️⃣ Testing user login...');
    const loginData = new URLSearchParams();
    loginData.append('username', 'test@example.com');
    loginData.append('password', 'testpassword123');
    
    const loginResponse = await axios.post(`${API_BASE_URL}/login/access-token`, loginData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    console.log('✅ Login successful:', {
      user_id: loginResponse.data.user.id,
      email: loginResponse.data.user.email,
      token: loginResponse.data.access_token.substring(0, 20) + '...'
    });
    console.log('');

    // Test 4: Get current user
    console.log('4️⃣ Testing get current user...');
    const token = loginResponse.data.access_token;
    const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Get user successful:', {
      id: userResponse.data.id,
      email: userResponse.data.email,
      full_name: userResponse.data.full_name,
      role: userResponse.data.role
    });
    console.log('');

    // Test 5: Create brand
    console.log('5️⃣ Testing brand creation...');
    const brandData = {
      name: 'Test Brand',
      description: 'A test brand for testing purposes'
    };
    
    const brandResponse = await axios.post(`${API_BASE_URL}/brands`, brandData, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Brand creation successful:', {
      id: brandResponse.data.id,
      name: brandResponse.data.name,
      description: brandResponse.data.description
    });
    console.log('');

    // Test 6: Create ticket
    console.log('6️⃣ Testing ticket creation...');
    const ticketData = {
      title: 'Test Complaint',
      description: 'This is a test complaint for testing purposes',
      brand_id: brandResponse.data.id,
      priority: 'high'
    };
    
    const ticketResponse = await axios.post(`${API_BASE_URL}/tickets`, ticketData, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Ticket creation successful:', {
      id: ticketResponse.data.id,
      title: ticketResponse.data.title,
      status: ticketResponse.data.status,
      priority: ticketResponse.data.priority
    });
    console.log('');

    console.log('🎉 All tests passed! Node.js backend is working correctly.');
    console.log('📊 Backend is ready for frontend integration.');

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
    console.error('Status:', error.response?.status);
    console.error('Headers:', error.response?.headers);
  }
}

// Run the test
testBackend(); 