const axios = require('axios');

async function testAdminNavigation() {
  console.log('🧪 Testing Admin Navigation (Simple HTTP Test)\n');

  try {
    // Test 1: Check if frontend is accessible
    console.log('1️⃣ Testing frontend accessibility...');
    const frontendResponse = await axios.get('http://localhost:5173');
    console.log('✅ Frontend is accessible (Status:', frontendResponse.status, ')');

    // Test 2: Check if backend is accessible
    console.log('\n2️⃣ Testing backend accessibility...');
    const backendResponse = await axios.get('http://localhost:8001/health');
    console.log('✅ Backend is accessible (Status:', backendResponse.status, ')');
    console.log('   Backend health:', backendResponse.data);

    // Test 3: Test admin login endpoint
    console.log('\n3️⃣ Testing admin login endpoint...');
    try {
      const loginForm = new URLSearchParams();
      loginForm.append('username', 'admin@complainthub.com');
      loginForm.append('password', 'admin123');

      const loginResponse = await axios.post('http://localhost:8001/api/v1/login/access-token', loginForm, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      console.log('✅ Admin login successful');
      console.log('   Token received:', loginResponse.data.access_token ? 'Yes' : 'No');
      
      const adminToken = loginResponse.data.access_token;
      
      // Test 4: Test admin dashboard endpoint
      console.log('\n4️⃣ Testing admin dashboard endpoint...');
      const dashboardResponse = await axios.get('http://localhost:8001/api/v1/admin/dashboard', {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      console.log('✅ Admin dashboard endpoint accessible');
      console.log('   Dashboard data received:', dashboardResponse.data.overview ? 'Yes' : 'No');
      
      // Test 5: Test admin brands endpoint
      console.log('\n5️⃣ Testing admin brands endpoint...');
      const brandsResponse = await axios.get('http://localhost:8001/api/v1/admin/brands', {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      console.log('✅ Admin brands endpoint accessible');
      console.log('   Brands count:', brandsResponse.data.length);
      
      // Test 6: Test admin analytics endpoint
      console.log('\n6️⃣ Testing admin analytics endpoint...');
      const analyticsResponse = await axios.get('http://localhost:8001/api/v1/admin/analytics', {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      console.log('✅ Admin analytics endpoint accessible');
      console.log('   Analytics data received:', analyticsResponse.data.status_breakdown ? 'Yes' : 'No');
      
      console.log('\n🎉 Admin Navigation Backend Test Completed Successfully!');
      console.log('\n📝 Summary:');
      console.log('   ✅ Frontend server running');
      console.log('   ✅ Backend server running');
      console.log('   ✅ Admin authentication working');
      console.log('   ✅ Admin dashboard API accessible');
      console.log('   ✅ Admin brands API accessible');
      console.log('   ✅ Admin analytics API accessible');
      console.log('\n🌐 Frontend URLs to test manually:');
      console.log('   - Admin Login: http://localhost:5173/admin/login');
      console.log('   - Admin Dashboard: http://localhost:5173/admin/dashboard');
      console.log('   - Admin Brands: http://localhost:5173/admin/brands');
      console.log('   - Admin Analytics: http://localhost:5173/admin/analytics');
      console.log('   - Admin Tickets: http://localhost:5173/admin/tickets');
      console.log('   - Admin Users: http://localhost:5173/admin/users');
      
    } catch (loginError) {
      console.log('❌ Admin login failed:', loginError.response?.data?.error || loginError.message);
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('   Status:', error.response.status);
      console.error('   Data:', error.response.data);
    }
  }
}

// Run the test
testAdminNavigation(); 