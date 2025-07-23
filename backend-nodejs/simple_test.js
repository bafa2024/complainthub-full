const axios = require('axios');

async function testHealth() {
  try {
    console.log('Testing health endpoint...');
    const response = await axios.get('http://localhost:8001/health');
    console.log('✅ Health check successful:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
    return false;
  }
}

testHealth(); 