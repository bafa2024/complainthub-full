const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';
const FRONTEND_URL = 'http://localhost:5173';

async function testAdminAuthComprehensive() {
    console.log('🧪 Comprehensive Admin Authentication Test\n');

    try {
        // Test 1: Test admin signup with unique email
        console.log('1️⃣ Testing Admin Signup with unique email...');
        const uniqueEmail = `admin_${Date.now()}@complainthub.com`;
        const signupData = {
            email: uniqueEmail,
            full_name: 'Test Admin User',
            password: 'admin123456',
            role: 'admin'
        };

        try {
            const signupResponse = await axios.post(`${BASE_URL}/auth/signup`, signupData);
            console.log('✅ Admin signup successful:', {
                user_id: signupResponse.data.user.id,
                email: signupResponse.data.user.email,
                role: signupResponse.data.user.role,
                token: signupResponse.data.access_token ? 'Generated' : 'None'
            });

            const token = signupResponse.data.access_token;

            // Test 2: Test admin login with the new account
            console.log('\n2️⃣ Testing Admin Login with new account...');
            const loginForm = new URLSearchParams();
            loginForm.append('username', uniqueEmail);
            loginForm.append('password', 'admin123456');

            const loginResponse = await axios.post(`${BASE_URL}/login/access-token`, loginForm, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            console.log('✅ Admin login successful:', {
                user_id: loginResponse.data.user.id,
                email: loginResponse.data.user.email,
                role: loginResponse.data.user.role
            });

            // Test 3: Test admin-specific endpoints
            console.log('\n3️⃣ Testing Admin-specific endpoints...');
            
            // Test get current user
            const userResponse = await axios.get(`${BASE_URL}/users/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            console.log('✅ Get current user successful:', {
                user_id: userResponse.data.id,
                email: userResponse.data.email,
                role: userResponse.data.role
            });

            // Test get all users (admin only)
            const usersResponse = await axios.get(`${BASE_URL}/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            console.log('✅ Admin can access users list:', {
                user_count: usersResponse.data.length
            });

            // Test 4: Test role-based access control
            console.log('\n4️⃣ Testing Role-based Access Control...');
            
            // Create a regular user
            const regularUserData = {
                email: `user_${Date.now()}@example.com`,
                full_name: 'Regular User',
                password: 'user123',
                role: 'user'
            };
            
            const regularUserResponse = await axios.post(`${BASE_URL}/auth/signup`, regularUserData);
            const regularUserToken = regularUserResponse.data.access_token;
            
            // Try to access admin endpoint with regular user
            try {
                await axios.get(`${BASE_URL}/users`, {
                    headers: { 'Authorization': `Bearer ${regularUserToken}` }
                });
                console.log('❌ Regular user should not access admin endpoint');
            } catch (error) {
                if (error.response?.status === 403) {
                    console.log('✅ Role-based access control working: Regular user denied admin access');
                } else {
                    console.log('❌ Unexpected error:', error.response?.data?.error);
                }
            }

        } catch (error) {
            console.log('❌ Admin signup failed:', error.response?.data?.error || error.message);
        }

        // Test 5: Test existing admin login
        console.log('\n5️⃣ Testing existing admin login...');
        const existingLoginForm = new URLSearchParams();
        existingLoginForm.append('username', 'admin@complainthub.com');
        existingLoginForm.append('password', 'admin123');

        try {
            const existingLoginResponse = await axios.post(`${BASE_URL}/login/access-token`, existingLoginForm, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            console.log('✅ Existing admin login successful:', {
                user_id: existingLoginResponse.data.user.id,
                email: existingLoginResponse.data.user.email,
                role: existingLoginResponse.data.user.role
            });
        } catch (error) {
            console.log('❌ Existing admin login failed:', error.response?.data?.error || error.message);
        }

        // Test 6: Test invalid credentials
        console.log('\n6️⃣ Testing invalid credentials...');
        const invalidLoginForm = new URLSearchParams();
        invalidLoginForm.append('username', 'nonexistent@example.com');
        invalidLoginForm.append('password', 'wrongpassword');

        try {
            await axios.post(`${BASE_URL}/login/access-token`, invalidLoginForm, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            console.log('❌ Invalid login should have failed');
        } catch (error) {
            if (error.response?.status === 401) {
                console.log('✅ Invalid credentials properly rejected');
            } else {
                console.log('❌ Unexpected error for invalid credentials:', error.response?.data?.error);
            }
        }

        // Test 7: Test duplicate signup
        console.log('\n7️⃣ Testing duplicate signup...');
        try {
            await axios.post(`${BASE_URL}/auth/signup`, signupData);
            console.log('❌ Duplicate signup should have failed');
        } catch (error) {
            if (error.response?.data?.error === 'User already exists') {
                console.log('✅ Duplicate signup properly rejected');
            } else {
                console.log('❌ Unexpected error for duplicate signup:', error.response?.data?.error);
            }
        }

        console.log('\n🎉 All admin authentication tests completed!');

    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

// Run the test
testAdminAuthComprehensive(); 