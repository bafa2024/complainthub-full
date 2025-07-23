const axios = require('axios');

async function comprehensiveBrandTest() {
  console.log('🧪 Comprehensive Brand Authentication Test...\n');

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
    
    console.log('Signup data:', signupData);
    const signupResponse = await axios.post('http://localhost:8001/api/v1/auth/signup', signupData);
    console.log('✅ Brand signup successful!');
    console.log('User ID:', signupResponse.data.user?.id);
    console.log('User email:', signupResponse.data.user?.email);
    console.log('User role:', signupResponse.data.user?.role);
    console.log('Has brand:', !!signupResponse.data.user?.brand);
    console.log('Brand data:', signupResponse.data.user?.brand);
    console.log('');

    // Test 2: Brand Login
    console.log('2️⃣ Testing brand login...');
    const loginForm = new URLSearchParams();
    loginForm.append('username', signupData.email);
    loginForm.append('password', signupData.password);
    
    const loginResponse = await axios.post('http://localhost:8001/api/v1/login/access-token', loginForm, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    console.log('✅ Brand login successful!');
    console.log('User ID:', loginResponse.data.user?.id);
    console.log('User email:', loginResponse.data.user?.email);
    console.log('User role:', loginResponse.data.user?.role);
    console.log('Has token:', !!loginResponse.data.access_token);
    console.log('');

    // Test 3: Get Current User
    console.log('3️⃣ Testing get current user...');
    const token = loginResponse.data.access_token;
    const userResponse = await axios.get('http://localhost:8001/api/v1/users/me', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Get current user successful!');
    console.log('User ID:', userResponse.data.id);
    console.log('User email:', userResponse.data.email);
    console.log('User role:', userResponse.data.role);
    console.log('');

    // Test 4: Brand Dashboard
    console.log('4️⃣ Testing brand dashboard...');
    const dashboardResponse = await axios.get('http://localhost:8001/api/v1/brand/dashboard', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('✅ Brand dashboard successful!');
    console.log('Has brand:', !!dashboardResponse.data.brand);
    console.log('Brand name:', dashboardResponse.data.brand?.name);
    console.log('Tickets count:', dashboardResponse.data.tickets?.length || 0);
    console.log('');

    console.log('🎉 All brand authentication tests passed successfully!');

  } catch (error) {
    console.error('❌ Test failed!');
    console.error('Error message:', error.message);
    console.error('Response status:', error.response?.status);
    console.error('Response data:', error.response?.data);
    
    if (error.response?.data?.error) {
      console.error('Server error details:', error.response.data.error);
    }
  }
}

comprehensiveBrandTest(); 