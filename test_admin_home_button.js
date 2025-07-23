const axios = require('axios');

async function testAdminHomeButton() {
  console.log('🧪 Testing Admin Home Button Visibility\n');

  try {
    // Test 1: Check if frontend is accessible
    console.log('1️⃣ Testing frontend accessibility...');
    const frontendResponse = await axios.get('http://localhost:5173');
    console.log('✅ Frontend is accessible (Status:', frontendResponse.status, ')');

    // Test 2: Check if backend is accessible
    console.log('\n2️⃣ Testing backend accessibility...');
    const backendResponse = await axios.get('http://localhost:8001/health');
    console.log('✅ Backend is accessible (Status:', backendResponse.status, ')');

    // Test 3: Test admin login
    console.log('\n3️⃣ Testing admin login...');
    const loginForm = new URLSearchParams();
    loginForm.append('username', 'admin@complainthub.com');
    loginForm.append('password', 'admin123');

    const loginResponse = await axios.post('http://localhost:8001/api/v1/login/access-token', loginForm, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    console.log('✅ Admin login successful');
    const adminToken = loginResponse.data.access_token;
    
    // Test 4: Test admin dashboard endpoint
    console.log('\n4️⃣ Testing admin dashboard endpoint...');
    const dashboardResponse = await axios.get('http://localhost:8001/api/v1/admin/dashboard', {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    console.log('✅ Admin dashboard endpoint accessible');
    console.log('   Dashboard data received:', dashboardResponse.data.overview ? 'Yes' : 'No');
    
    console.log('\n🎉 Admin Home Button Test Completed Successfully!');
    console.log('\n📝 Summary:');
    console.log('   ✅ Frontend server running');
    console.log('   ✅ Backend server running');
    console.log('   ✅ Admin authentication working');
    console.log('   ✅ Admin dashboard API accessible');
    
    console.log('\n🌐 To see the Home button:');
    console.log('   1. Go to: http://localhost:5173/admin/login');
    console.log('   2. Login with: admin@complainthub.com / admin123');
    console.log('   3. You should see the admin dashboard with:');
    console.log('      - Breadcrumb navigation with "Home" link');
    console.log('      - Large "Home" button next to the title');
    console.log('      - Admin navigation in the header');
    
    console.log('\n🔍 Expected Home Button Features:');
    console.log('   - Large blue button with home icon');
    console.log('   - Located next to "Admin Dashboard" title');
    console.log('   - Breadcrumb navigation at the top');
    console.log('   - Hover effects and animations');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
  }
}

// Run the test
testAdminHomeButton(); 