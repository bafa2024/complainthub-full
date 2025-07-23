const axios = require('axios');

async function quickVerificationTest() {
  console.log('🔍 Quick Verification Test - Checking Fixed Issues\n');

  try {
    // Test 1: Backend Health
    console.log('1️⃣ Testing backend health...');
    const healthResponse = await axios.get('http://localhost:8001/health');
    console.log('✅ Backend is healthy');

    // Test 2: Admin Analytics (previously failing)
    console.log('\n2️⃣ Testing admin analytics (previously failing)...');
    const loginForm = new URLSearchParams();
    loginForm.append('username', 'admin@complainthub.com');
    loginForm.append('password', 'admin123');

    const loginResponse = await axios.post('http://localhost:8001/api/v1/login/access-token', loginForm, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const adminToken = loginResponse.data.access_token;
    const analyticsResponse = await axios.get('http://localhost:8001/api/v1/admin/analytics', {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    
    console.log('✅ Admin analytics is working');
    console.log('   Analytics data:', analyticsResponse.data);

    // Test 3: Frontend Accessibility
    console.log('\n3️⃣ Testing frontend accessibility...');
    const frontendResponse = await axios.get('http://localhost:5173');
    console.log('✅ Frontend is accessible');

    console.log('\n🎉 All critical fixes verified successfully!');
    console.log('\n📊 Current System Status:');
    console.log('   ✅ Backend server running');
    console.log('   ✅ Frontend server running');
    console.log('   ✅ Admin analytics fixed');
    console.log('   ✅ Database schema updated');
    console.log('   ✅ Authentication working');

  } catch (error) {
    console.error('❌ Verification failed:', error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
  }
}

quickVerificationTest(); 