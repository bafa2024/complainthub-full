// Test script to verify backend connection
const API_BASE_URL = 'http://localhost:8000/api/v1';

async function testBackendConnection() {
  console.log('🧪 Testing Backend Connection');
  console.log('================================');
  
  try {
    // Test 1: Health check
    console.log('1. Testing health endpoint...');
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    console.log(`Health status: ${healthResponse.status}`);
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('Health data:', healthData);
    }
    
    // Test 2: Try to get tickets without auth
    console.log('\n2. Testing tickets endpoint (no auth)...');
    const ticketsResponse = await fetch(`${API_BASE_URL}/tickets/`);
    console.log(`Tickets status: ${ticketsResponse.status}`);
    if (!ticketsResponse.ok) {
      const errorText = await ticketsResponse.text();
      console.log('Expected error (no auth):', errorText);
    }
    
    // Test 3: Test with mock token
    console.log('\n3. Testing with mock token...');
    const mockTokenResponse = await fetch(`${API_BASE_URL}/tickets/`, {
      headers: {
        'Authorization': 'Bearer mock-token'
      }
    });
    console.log(`Mock token status: ${mockTokenResponse.status}`);
    if (!mockTokenResponse.ok) {
      const errorText = await mockTokenResponse.text();
      console.log('Mock token error:', errorText);
    }
    
    console.log('\n✅ Backend connection test completed');
    
  } catch (error) {
    console.error('❌ Connection error:', error);
  }
}

// Run the test
testBackendConnection(); 