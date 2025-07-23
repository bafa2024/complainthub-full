// Test the brand tickets endpoint with proper authentication
const jwt = require('jsonwebtoken');
const http = require('http');

const JWT_SECRET = 'your-secret-key-change-in-production';

// Create a test token for a brand user
const testToken = jwt.sign({
  user_id: 1,
  email: 'brandmanager@test.com',
  role: 'brand_user',
  brand_id: 1
}, JWT_SECRET);

console.log('🔑 Test token created:', testToken);

// Test the endpoint
const options = {
  hostname: 'localhost',
  port: 8001,
  path: '/api/v1/brands/1/tickets',
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${testToken}`,
    'Content-Type': 'application/json'
  }
};

console.log('\n🧪 Testing /api/v1/brands/1/tickets endpoint...');

const req = http.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  console.log(`Headers:`, res.headers);
  
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    console.log('\nResponse:');
    try {
      const parsed = JSON.parse(data);
      console.log(JSON.stringify(parsed, null, 2));
    } catch (e) {
      console.log(data);
    }
  });
});

req.on('error', (e) => {
  console.error('Request error:', e.message);
});

req.end();