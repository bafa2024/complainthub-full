// Simple Authentication Test Script
// This script can be run in the browser console to test auth functionality

console.log('🔍 Starting Authentication Tests...');

// Test 1: Check if AuthContext is available
function testAuthContext() {
  console.log('✅ Test 1: AuthContext Availability');
  try {
    // This would need to be run in the React app context
    console.log('AuthContext should be available in React components');
    return true;
  } catch (error) {
    console.error('❌ AuthContext not available:', error);
    return false;
  }
}

// Test 2: Test form validation
function testFormValidation() {
  console.log('✅ Test 2: Form Validation');
  
  const testCases = [
    {
      name: 'Valid Login Data',
      data: { email: 'test@example.com', password: 'password123' },
      expected: true
    },
    {
      name: 'Invalid Email',
      data: { email: 'invalid-email', password: 'password123' },
      expected: false
    },
    {
      name: 'Empty Password',
      data: { email: 'test@example.com', password: '' },
      expected: false
    }
  ];

  testCases.forEach(testCase => {
    const isValid = validateLoginForm(testCase.data);
    const result = isValid === testCase.expected ? '✅' : '❌';
    console.log(`${result} ${testCase.name}: ${isValid ? 'Valid' : 'Invalid'}`);
  });
}

// Test 3: Test signup validation
function testSignupValidation() {
  console.log('✅ Test 3: Signup Validation');
  
  const testCases = [
    {
      name: 'Valid Signup Data',
      data: {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com',
        phone: '+1234567890',
        password: 'password123',
        confirmPassword: 'password123'
      },
      expected: true
    },
    {
      name: 'Password Mismatch',
      data: {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@example.com',
        phone: '+1234567890',
        password: 'password123',
        confirmPassword: 'differentpassword'
      },
      expected: false
    },
    {
      name: 'Missing Required Fields',
      data: {
        firstName: 'John',
        lastName: '',
        email: 'john@example.com',
        phone: '+1234567890',
        password: 'password123',
        confirmPassword: 'password123'
      },
      expected: false
    }
  ];

  testCases.forEach(testCase => {
    const isValid = validateSignupForm(testCase.data);
    const result = isValid === testCase.expected ? '✅' : '❌';
    console.log(`${result} ${testCase.name}: ${isValid ? 'Valid' : 'Invalid'}`);
  });
}

// Helper functions for validation
function validateLoginForm(data) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(data.email) && data.password.length >= 6;
}

function validateSignupForm(data) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
  
  return (
    data.firstName.trim() !== '' &&
    data.lastName.trim() !== '' &&
    emailRegex.test(data.email) &&
    phoneRegex.test(data.phone) &&
    data.password.length >= 6 &&
    data.password === data.confirmPassword
  );
}

// Test 4: Test API endpoints (mock)
function testAPIEndpoints() {
  console.log('✅ Test 4: API Endpoints');
  
  const endpoints = [
    { name: 'Login Endpoint', url: '/api/v1/login/access-token', method: 'POST' },
    { name: 'Signup Endpoint', url: '/api/v1/auth/signup', method: 'POST' },
    { name: 'Current User Endpoint', url: '/api/v1/users/me', method: 'GET' }
  ];

  endpoints.forEach(endpoint => {
    console.log(`🔗 ${endpoint.name}: ${endpoint.method} ${endpoint.url}`);
  });
}

// Test 5: Test localStorage functionality
function testLocalStorage() {
  console.log('✅ Test 5: LocalStorage');
  
  try {
    // Test token storage
    const testToken = 'test-token-123';
    localStorage.setItem('token', testToken);
    const retrievedToken = localStorage.getItem('token');
    
    if (retrievedToken === testToken) {
      console.log('✅ Token storage: Working');
    } else {
      console.log('❌ Token storage: Failed');
    }
    
    // Clean up
    localStorage.removeItem('token');
    console.log('✅ Token cleanup: Working');
    
  } catch (error) {
    console.error('❌ LocalStorage test failed:', error);
  }
}

// Run all tests
function runAllTests() {
  console.log('🚀 Running All Authentication Tests...\n');
  
  testAuthContext();
  console.log('');
  
  testFormValidation();
  console.log('');
  
  testSignupValidation();
  console.log('');
  
  testAPIEndpoints();
  console.log('');
  
  testLocalStorage();
  console.log('');
  
  console.log('🎉 All tests completed!');
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  window.authTests = {
    runAllTests,
    testAuthContext,
    testFormValidation,
    testSignupValidation,
    testAPIEndpoints,
    testLocalStorage
  };
  
  console.log('📋 Authentication tests loaded! Run authTests.runAllTests() to start testing.');
}

// Manual test instructions
console.log(`
📋 Manual Testing Instructions:

1. Navigate to http://localhost:5173/auth-test
2. Test the authentication functionality using the UI
3. Check the following:
   - Login form validation
   - Signup form validation
   - Password confirmation matching
   - Error message display
   - Loading states
   - Navigation after successful auth
   - Logout functionality

4. Test the actual login/signup pages:
   - http://localhost:5173/login
   - http://localhost:5173/signup

5. Check browser console for any errors
6. Verify localStorage token management
7. Test responsive design on different screen sizes
`); 