const axios = require('axios');

async function testBrandSignup() {
  console.log('🧪 Simple Brand Signup Test (Fixed)...\n');

  try {
    // Test brand signup with minimal data
    const signupData = {
      email: `brand_${Date.now()}@test.com`,
      full_name: 'Test Brand User',
      password: 'testpass123',
      brand_name: 'Test Brand Company',
      role: 'brand_user'
    };
    
    console.log('Sending brand signup request with data:', signupData);
    const response = await axios.post('http://localhost:8001/api/v1/auth/signup', signupData);
    
    console.log('✅ Brand signup successful!');
    console.log('Response status:', response.status);
    console.log('User ID:', response.data.user?.id);
    console.log('User email:', response.data.user?.email);
    console.log('User role:', response.data.user?.role);
    console.log('Has brand:', !!response.data.user?.brand);
    console.log('Brand data:', response.data.user?.brand);

  } catch (error) {
    console.error('❌ Brand signup failed!');
    console.error('Error message:', error.message);
    console.error('Response status:', error.response?.status);
    console.error('Response data:', error.response?.data);
    
    if (error.response?.data?.error) {
      console.error('Server error details:', error.response.data.error);
    }
  }
}

testBrandSignup(); 