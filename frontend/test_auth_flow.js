// Test Authentication Flow
// This script tests the authentication endpoints

console.log('🧪 Testing Authentication Flow...');

// Test API endpoints
const API_BASE_URL = 'http://localhost:8001/api/v1';

// Test 1: Check if backend is running
async function testBackendHealth() {
    console.log('✅ Test 1: Backend Health Check');
    try {
        const response = await fetch('http://localhost:8001/health');
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend is running:', data);
            return true;
        } else {
            console.log('❌ Backend health check failed:', response.status);
            return false;
        }
    } catch (error) {
        console.log('❌ Backend not accessible:', error.message);
        return false;
    }
}

// Test 2: Test signup endpoint
async function testSignup() {
    console.log('✅ Test 2: Signup Endpoint');
    try {
        const signupData = {
            email: 'test@example.com',
            full_name: 'Test User',
            phone_number: '+1234567890',
            password: 'password123'
        };

        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(signupData)
        });

        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Signup successful:', data);
            return true;
        } else {
            console.log('❌ Signup failed:', data);
            return false;
        }
    } catch (error) {
        console.log('❌ Signup error:', error.message);
        return false;
    }
}

// Test 3: Test login endpoint
async function testLogin() {
    console.log('✅ Test 3: Login Endpoint');
    try {
        const loginData = {
            email: 'test@example.com',
            password: 'password123'
        };

        const response = await fetch(`${API_BASE_URL}/login/access-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Login successful:', data);
            return data.access_token;
        } else {
            console.log('❌ Login failed:', data);
            return null;
        }
    } catch (error) {
        console.log('❌ Login error:', error.message);
        return null;
    }
}

// Test 4: Test get current user endpoint
async function testGetCurrentUser(token) {
    console.log('✅ Test 4: Get Current User');
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Get current user successful:', data);
            return true;
        } else {
            console.log('❌ Get current user failed:', data);
            return false;
        }
    } catch (error) {
        console.log('❌ Get current user error:', error.message);
        return false;
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 Running Authentication Tests...\n');
    
    // Test 1: Backend health
    const backendRunning = await testBackendHealth();
    if (!backendRunning) {
        console.log('\n❌ Backend is not running. Please start the backend server first.');
        console.log('💡 To start the backend: cd backend && python minimal_server.py');
        return;
    }
    
    console.log('');
    
    // Test 2: Signup
    const signupSuccess = await testSignup();
    console.log('');
    
    // Test 3: Login
    const token = await testLogin();
    console.log('');
    
    // Test 4: Get current user
    if (token) {
        await testGetCurrentUser(token);
    }
    
    console.log('\n🎉 Authentication tests completed!');
}

// Export for use in browser console
if (typeof window !== 'undefined') {
    window.authFlowTests = {
        runAllTests,
        testBackendHealth,
        testSignup,
        testLogin,
        testGetCurrentUser
    };
    
    console.log('📋 Authentication flow tests loaded! Run authFlowTests.runAllTests() to start testing.');
}

// Manual instructions
console.log(`
📋 Manual Testing Instructions:

1. Start the backend server:
   cd backend
   python minimal_server.py

2. Open browser console and run:
   authFlowTests.runAllTests()

3. Or test individual endpoints:
   authFlowTests.testBackendHealth()
   authFlowTests.testSignup()
   authFlowTests.testLogin()

4. Check the frontend authentication:
   - Navigate to http://localhost:5173/login
   - Try logging in with test@example.com / password123
   - Check browser console for any errors

5. Test signup:
   - Navigate to http://localhost:5173/signup
   - Fill the form and submit
   - Check browser console for any errors
`); 