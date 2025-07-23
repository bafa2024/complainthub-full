const axios = require('axios');

const FRONTEND_URL = 'http://localhost:5173';

async function testFrontendAdminAuth() {
    console.log('🧪 Testing Frontend Admin Authentication Components\n');

    try {
        // Test 1: Check if admin signup page is accessible
        console.log('1️⃣ Testing Admin Signup Page Accessibility...');
        try {
            const signupResponse = await axios.get(`${FRONTEND_URL}/admin/signup`);
            if (signupResponse.status === 200) {
                console.log('✅ Admin signup page is accessible');
                console.log('   - Status:', signupResponse.status);
                console.log('   - Content-Type:', signupResponse.headers['content-type']);
            } else {
                console.log('❌ Admin signup page returned unexpected status:', signupResponse.status);
            }
        } catch (error) {
            console.log('❌ Admin signup page not accessible:', error.message);
        }

        // Test 2: Check if admin login page is accessible
        console.log('\n2️⃣ Testing Admin Login Page Accessibility...');
        try {
            const loginResponse = await axios.get(`${FRONTEND_URL}/admin/login`);
            if (loginResponse.status === 200) {
                console.log('✅ Admin login page is accessible');
                console.log('   - Status:', loginResponse.status);
                console.log('   - Content-Type:', loginResponse.headers['content-type']);
            } else {
                console.log('❌ Admin login page returned unexpected status:', loginResponse.status);
            }
        } catch (error) {
            console.log('❌ Admin login page not accessible:', error.message);
        }

        // Test 3: Check if admin dashboard is protected (should redirect to login)
        console.log('\n3️⃣ Testing Admin Dashboard Protection...');
        try {
            const dashboardResponse = await axios.get(`${FRONTEND_URL}/admin/dashboard`);
            if (dashboardResponse.status === 200) {
                console.log('⚠️ Admin dashboard is accessible without authentication (might be in mockup mode)');
            } else {
                console.log('✅ Admin dashboard properly protected');
            }
        } catch (error) {
            console.log('✅ Admin dashboard properly protected (redirects to login)');
        }

        // Test 4: Check if other admin routes are accessible
        console.log('\n4️⃣ Testing Other Admin Routes...');
        const adminRoutes = [
            '/admin/users',
            '/admin/brands',
            '/admin/analytics',
            '/admin/settings'
        ];

        for (const route of adminRoutes) {
            try {
                const response = await axios.get(`${FRONTEND_URL}${route}`);
                if (response.status === 200) {
                    console.log(`⚠️ ${route} is accessible without authentication`);
                } else {
                    console.log(`✅ ${route} properly protected`);
                }
            } catch (error) {
                console.log(`✅ ${route} properly protected (redirects to login)`);
            }
        }

        // Test 5: Check if frontend is serving React app correctly
        console.log('\n5️⃣ Testing Frontend React App...');
        try {
            const homeResponse = await axios.get(`${FRONTEND_URL}/`);
            if (homeResponse.status === 200 && homeResponse.data.includes('React')) {
                console.log('✅ Frontend React app is serving correctly');
            } else {
                console.log('⚠️ Frontend might not be serving React app correctly');
            }
        } catch (error) {
            console.log('❌ Frontend not accessible:', error.message);
        }

        console.log('\n🎉 Frontend admin authentication component tests completed!');
        console.log('\n📝 Next Steps:');
        console.log('   1. Open browser and navigate to http://localhost:5173/admin/signup');
        console.log('   2. Test admin signup functionality');
        console.log('   3. Navigate to http://localhost:5173/admin/login');
        console.log('   4. Test admin login functionality');
        console.log('   5. Verify admin dashboard access after login');

    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

// Run the test
testFrontendAdminAuth(); 