const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';

async function testAdminAuth() {
    console.log('🧪 Testing Admin Authentication System\n');

    try {
        // Test 1: Admin Signup
        console.log('1️⃣ Testing Admin Signup...');
        const signupData = {
            email: 'newadmin@complainthub.com',
            full_name: 'New Admin User',
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
        } catch (error) {
            if (error.response?.data?.error === 'User already exists') {
                console.log('⚠️ Admin user already exists, proceeding with login test...');
            } else {
                console.log('❌ Admin signup failed:', error.response?.data?.error || error.message);
            }
        }

        // Test 2: Admin Login
        console.log('\n2️⃣ Testing Admin Login...');
        const loginForm = new URLSearchParams();
        loginForm.append('username', 'newadmin@complainthub.com');
        loginForm.append('password', 'admin123456');

        try {
            const loginResponse = await axios.post(`${BASE_URL}/login/access-token`, loginForm, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            console.log('✅ Admin login successful:', {
                user_id: loginResponse.data.user.id,
                email: loginResponse.data.user.email,
                role: loginResponse.data.user.role,
                token: loginResponse.data.access_token ? 'Generated' : 'None'
            });

            const token = loginResponse.data.access_token;

            // Test 3: Get Current User
            console.log('\n3️⃣ Testing Get Current User...');
            const userResponse = await axios.get(`${BASE_URL}/users/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            console.log('✅ Get current user successful:', {
                user_id: userResponse.data.id,
                email: userResponse.data.email,
                role: userResponse.data.role
            });

            // Test 4: Admin-specific endpoint (Get all users)
            console.log('\n4️⃣ Testing Admin-specific endpoint (Get all users)...');
            const usersResponse = await axios.get(`${BASE_URL}/users`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            console.log('✅ Admin can access users list:', {
                user_count: usersResponse.data.length,
                users: usersResponse.data.map(u => ({ id: u.id, email: u.email, role: u.role }))
            });

        } catch (error) {
            console.log('❌ Admin login failed:', error.response?.data?.error || error.message);
        }

        // Test 5: Test with existing admin
        console.log('\n5️⃣ Testing with existing admin...');
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

    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

// Run the test
testAdminAuth(); 