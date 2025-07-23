const axios = require('axios');

async function testBrandSignup() {
  console.log('🧪 Simple Brand Signup Test...\n');

  try {
    // Test brand signup
    const signupData = {
      email: `brand_${Date.now()}@test.com`,
      full_name: 'Test Brand User',
      password: 'testpass123',
      brand_name: 'Test Brand Company',
      role: 'brand_user'
    };
    
    console.log('Sending signup request...');
    const response = await axios.post('http://localhost:8001/api/v1/auth/signup', signupData);
    
    console.log('✅ Success! Response:', {
      status: response.status,
      user_id: response.data.user?.id,
      email: response.data.user?.email,
      role: response.data.user?.role,
      has_token: !!response.data.access_token
    });

  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    if (error.response?.status) {
      console.error('Status:', error.response.status);
    }
  }
}

testBrandSignup(); 