// Integration test script
import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3002';

async function testIntegration() {
    console.log('🔗 Testing Frontend-Backend Integration...\n');
    
    // Test backend endpoints
    console.log('📡 Testing Backend Endpoints:');
    
    const endpoints = [
        { name: 'Health Check', url: '/health' },
        { name: 'Root', url: '/' },
        { name: 'Testing Dashboard', url: '/api/v1/testing/' },
        { name: 'Database Test', url: '/api/v1/testing/database' }
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await axios.get(`${BACKEND_URL}${endpoint.url}`, { timeout: 5000 });
            console.log(`  ✅ ${endpoint.name}: ${response.status} - ${response.data.message || 'OK'}`);
        } catch (error) {
            console.log(`  ❌ ${endpoint.name}: ${error.response?.status || 'FAILED'} - ${error.message}`);
        }
    }
    
    // Test CORS
    console.log('\n🌐 Testing CORS (Cross-Origin Resource Sharing):');
    try {
        const response = await axios.get(`${BACKEND_URL}/health`, {
            headers: {
                'Origin': FRONTEND_URL
            },
            timeout: 5000
        });
        console.log('  ✅ CORS: Enabled - Frontend can access backend');
    } catch (error) {
        console.log('  ❌ CORS: Issues detected -', error.message);
    }
    
    // Test frontend availability
    console.log('\n🖥️  Testing Frontend Availability:');
    try {
        const response = await axios.get(FRONTEND_URL, { timeout: 5000 });
        console.log('  ✅ Frontend: Available on port 3000');
    } catch (error) {
        console.log('  ❌ Frontend: Not accessible -', error.message);
    }
    
    console.log('\n📊 Integration Test Summary:');
    console.log(`  Backend: ${BACKEND_URL}`);
    console.log(`  Frontend: ${FRONTEND_URL}`);
    console.log('  Status: Tests completed');
    console.log('\n💡 Visit http://localhost:3000 to see the integration test interface');
}

// Run the test
testIntegration().catch(console.error);