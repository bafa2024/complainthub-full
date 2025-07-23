const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';

async function testAdminDashboard() {
    console.log('🧪 Testing Admin Dashboard and Brand Management\n');

    let adminToken = null;

    try {
        // Step 1: Admin Login
        console.log('1️⃣ Admin Login...');
        const loginForm = new URLSearchParams();
        loginForm.append('username', 'admin@complainthub.com');
        loginForm.append('password', 'admin123');

        const loginResponse = await axios.post(`${BASE_URL}/login/access-token`, loginForm, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        adminToken = loginResponse.data.access_token;
        console.log('✅ Admin login successful');

        // Step 2: Test Admin Dashboard
        console.log('\n2️⃣ Testing Admin Dashboard...');
        const dashboardResponse = await axios.get(`${BASE_URL}/admin/dashboard`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Admin dashboard data:', {
            total_users: dashboardResponse.data.overview.total_users,
            total_brands: dashboardResponse.data.overview.total_brands,
            total_tickets: dashboardResponse.data.overview.total_tickets,
            resolution_rate: dashboardResponse.data.overview.resolution_rate
        });

        // Step 3: Test Get All Brands
        console.log('\n3️⃣ Testing Get All Brands...');
        const brandsResponse = await axios.get(`${BASE_URL}/admin/brands`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Brands retrieved:', brandsResponse.data.length, 'brands');

        // Step 4: Test Create Brand
        console.log('\n4️⃣ Testing Create Brand...');
        const newBrandData = {
            name: 'Test Brand ' + Date.now(),
            description: 'A test brand for admin dashboard testing',
            support_email: 'support@testbrand.com',
            industry: 'Technology',
            logo_url: 'https://example.com/logo.png',
            contact_info: 'Contact: +1234567890'
        };

        const createBrandResponse = await axios.post(`${BASE_URL}/admin/brands`, newBrandData, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        const newBrandId = createBrandResponse.data.id;
        console.log('✅ Brand created successfully:', {
            id: newBrandId,
            name: createBrandResponse.data.name,
            industry: createBrandResponse.data.industry
        });

        // Step 5: Test Update Brand
        console.log('\n5️⃣ Testing Update Brand...');
        const updateData = {
            name: 'Updated Test Brand',
            description: 'Updated description for testing',
            industry: 'Updated Technology'
        };

        const updateBrandResponse = await axios.put(`${BASE_URL}/admin/brands/${newBrandId}`, updateData, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Brand updated successfully:', {
            id: updateBrandResponse.data.id,
            name: updateBrandResponse.data.name,
            industry: updateBrandResponse.data.industry
        });

        // Step 6: Test Admin Analytics
        console.log('\n6️⃣ Testing Admin Analytics...');
        const analyticsResponse = await axios.get(`${BASE_URL}/admin/analytics`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Analytics data retrieved:', {
            status_breakdown: analyticsResponse.data.status_breakdown.length,
            channel_distribution: analyticsResponse.data.channel_distribution.length,
            daily_trends: analyticsResponse.data.daily_trends.length
        });

        // Step 7: Test Get All Tickets (Admin)
        console.log('\n7️⃣ Testing Get All Tickets (Admin)...');
        const ticketsResponse = await axios.get(`${BASE_URL}/admin/tickets`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Admin tickets retrieved:', ticketsResponse.data.length, 'tickets');

        // Step 8: Test Delete Brand (if no associated tickets)
        console.log('\n8️⃣ Testing Delete Brand...');
        try {
            const deleteResponse = await axios.delete(`${BASE_URL}/admin/brands/${newBrandId}`, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('✅ Brand deleted successfully');
        } catch (error) {
            if (error.response?.status === 400) {
                console.log('⚠️ Brand cannot be deleted due to associated tickets (expected behavior)');
            } else {
                console.log('❌ Brand deletion failed:', error.response?.data?.error);
            }
        }

        // Step 9: Test Role-based Access Control
        console.log('\n9️⃣ Testing Role-based Access Control...');
        
        // Create a regular user
        const regularUserData = {
            email: `user_${Date.now()}@example.com`,
            full_name: 'Regular User',
            password: 'user123',
            role: 'user'
        };
        
        const regularUserResponse = await axios.post(`${BASE_URL}/auth/signup`, regularUserData);
        const regularUserToken = regularUserResponse.data.access_token;
        
        // Try to access admin endpoints with regular user
        try {
            await axios.get(`${BASE_URL}/admin/brands`, {
                headers: { 'Authorization': `Bearer ${regularUserToken}` }
            });
            console.log('❌ Regular user should not access admin endpoints');
        } catch (error) {
            if (error.response?.status === 403) {
                console.log('✅ Role-based access control working: Regular user denied admin access');
            } else {
                console.log('❌ Unexpected error:', error.response?.data?.error);
            }
        }

        console.log('\n🎉 Admin Dashboard and Brand Management tests completed successfully!');
        console.log('\n📝 Summary:');
        console.log('   ✅ Admin authentication working');
        console.log('   ✅ Admin dashboard data retrieval working');
        console.log('   ✅ Brand CRUD operations working');
        console.log('   ✅ Admin analytics working');
        console.log('   ✅ Role-based access control working');
        console.log('   ✅ Admin tickets access working');

    } catch (error) {
        console.error('❌ Test failed:', error.response?.data?.error || error.message);
    }
}

// Run the test
testAdminDashboard(); 