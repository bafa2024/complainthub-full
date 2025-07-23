const axios = require('axios');

async function testHealth() {
  try {
    console.log('Testing backend health...');
    const response = await axios.get('http://localhost:8001/health');
    console.log('✅ Backend is running:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Backend test failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    return false;
  }
}

testHealth(); 