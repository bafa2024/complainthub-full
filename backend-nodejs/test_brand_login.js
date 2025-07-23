const axios = require('axios');

const API_BASE_URL = 'http://localhost:8001/api/v1';

async function testBrandLogin() {
  console.log('🧪 Testing Brand Login Response...\n');

  try {
    // First, create a brand user
    const signupData = {
      email: `brand_${Date.now()}@test.com`,
      full_name: 'Test Brand User',
      password: 'testpass123',
      brand_name: 'Test Brand Company',
      role: 'brand_user'
    };

    console.log('1️⃣ Creating brand user...');
    const signupResponse = await axios.post(`${API_BASE_URL}/auth/signup`, signupData);
    console.log('✅ Signup successful!');
    console.log('Signup response:', JSON.stringify(signupResponse.data, null, 2));

    // Now test login - use the correct endpoint
    console.log('\n2️⃣ Testing brand login...');
    const form = new URLSearchParams();
    form.append('username', signupData.email);
    form.append('password', signupData.password);

    const loginResponse = await axios.post(`${API_BASE_URL}/login/access-token`, form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    console.log('✅ Login successful!');
    console.log('Login response:', JSON.stringify(loginResponse.data, null, 2));

    // Test get current user - use the correct endpoint
    console.log('\n3️⃣ Testing get current user...');
    const token = loginResponse.data.access_token;
    const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Get current user successful!');
    console.log('User response:', JSON.stringify(userResponse.data, null, 2));

  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

testBrandLogin(); 