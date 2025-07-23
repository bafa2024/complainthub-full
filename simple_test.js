const axios = require('axios');

async function testBackend() {
  try {
    console.log('Testing backend connection...');
    const response = await axios.get('http://localhost:8001/health');
    console.log('Backend is running:', response.data);
  } catch (error) {
    console.error('Backend test failed:', error.message);
  }
}

testBackend(); 