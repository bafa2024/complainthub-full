const axios = require('axios');

async function debugTest() {
  console.log('🔍 Debug Test...\n');

  try {
    // Test 1: Health check
    console.log('1️⃣ Testing health check...');
    const healthResponse = await axios.get('http://localhost:8001/health');
    console.log('✅ Health check passed:', healthResponse.data);
    console.log('');

    // Test 2: Simple signup without brand
    console.log('2️⃣ Testing simple signup...');
    const signupData = {
      email: `user_${Date.now()}@test.com`,
      full_name: 'Test User',
      password: 'testpass123'
    };
    
    const signupResponse = await axios.post('http://localhost:8001/api/v1/auth/signup', signupData);
    console.log('✅ Simple signup successful:', {
      user_id: signupResponse.data.user?.id,
      email: signupResponse.data.user?.email,
      role: signupResponse.data.user?.role
    });
    console.log('');

    // Test 3: Brand signup
    console.log('3️⃣ Testing brand signup...');
    const brandSignupData = {
      email: `brand_${Date.now()}@test.com`,
      full_name: 'Test Brand User',
      password: 'testpass123',
      brand_name: 'Test Brand Company',
      role: 'brand_user'
    };
    
    const brandSignupResponse = await axios.post('http://localhost:8001/api/v1/auth/signup', brandSignupData);
    console.log('✅ Brand signup successful:', {
      user_id: brandSignupResponse.data.user?.id,
      email: brandSignupResponse.data.user?.email,
      role: brandSignupResponse.data.user?.role,
      has_brand: !!brandSignupResponse.data.user?.brand
    });

  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
    if (error.response?.status) {
      console.error('Status:', error.response.status);
    }
    if (error.response?.data?.error) {
      console.error('Server Error:', error.response.data.error);
    }
  }
}

debugTest(); 