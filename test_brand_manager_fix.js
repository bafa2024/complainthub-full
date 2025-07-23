// Test script to verify brand manager functionality fixes
const http = require('http');

// Test configuration
const baseURL = 'http://localhost:8001';
const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImJyYW5kbWFuYWdlckBleGFtcGxlLmNvbSIsInJvbGUiOiJicmFuZF91c2VyIiwiaWF0IjoxNzM3NTMzODIyfQ.test';

// Helper function to make HTTP requests
function makeRequest(path, method = 'GET', data = null, token = testToken) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, baseURL);
    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    };

    const req = http.request(options, (res) => {
      let responseData = '';
      res.on('data', (chunk) => responseData += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(responseData);
          resolve({ status: res.statusCode, data: parsed });
        } catch (e) {
          resolve({ status: res.statusCode, data: responseData });
        }
      });
    });

    req.on('error', (e) => reject(e));
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

async function runTests() {
  console.log('🧪 Testing Brand Manager Functionality Fixes\n');

  try {
    // Test 1: Check if brands endpoint works
    console.log('1. Testing brands endpoint...');
    const brandsResponse = await makeRequest('/api/v1/brands');
    console.log(`   Status: ${brandsResponse.status}`);
    if (brandsResponse.status === 200) {
      console.log(`   ✅ Found ${brandsResponse.data.length} brands`);
    } else {
      console.log(`   ❌ Error: ${JSON.stringify(brandsResponse.data)}`);
    }

    // Test 2: Check if brand tickets endpoint exists (should return 401/403 without proper auth)
    console.log('\n2. Testing brand tickets endpoint...');
    const ticketsResponse = await makeRequest('/api/v1/brands/1/tickets');
    console.log(`   Status: ${ticketsResponse.status}`);
    if (ticketsResponse.status === 401 || ticketsResponse.status === 403) {
      console.log('   ✅ Endpoint exists (authentication required)');
    } else if (ticketsResponse.status === 404) {
      console.log('   ❌ Endpoint not found - server needs restart');
    } else {
      console.log(`   ⚠️  Unexpected response: ${JSON.stringify(ticketsResponse.data)}`);
    }

    // Test 3: Check public brands endpoint
    console.log('\n3. Testing public brands endpoint...');
    const publicBrandsResponse = await makeRequest('/api/v1/public/brands', 'GET', null, null);
    console.log(`   Status: ${publicBrandsResponse.status}`);
    if (publicBrandsResponse.status === 200) {
      console.log(`   ✅ Found ${publicBrandsResponse.data.length} public brands`);
    } else {
      console.log(`   ❌ Error: ${JSON.stringify(publicBrandsResponse.data)}`);
    }

    // Test 4: Test server health
    console.log('\n4. Testing server health...');
    const healthResponse = await makeRequest('/health', 'GET', null, null);
    console.log(`   Status: ${healthResponse.status}`);
    if (healthResponse.status === 200) {
      console.log('   ✅ Server is healthy');
    } else {
      console.log('   ⚠️  Health endpoint not available');
    }

  } catch (error) {
    console.log('❌ Test failed:', error.message);
  }

  console.log('\n📋 Summary:');
  console.log('- Added missing /api/v1/brands/:id/tickets endpoint');
  console.log('- Fixed BrandDashboard.jsx ticket fetching logic');
  console.log('- Improved BrandManage.jsx brand filtering');
  console.log('- Added authentication to /brand/my-brands route');
  console.log('\nTo complete the fix, restart the backend server.');
}

runTests();