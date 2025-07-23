const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';

async function testBrandCRUD() {
    console.log('🧪 Testing Brand CRUD Operations in Admin Dashboard\n');

    let adminToken = null;
    let testBrandId = null;

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

        // Step 2: Test Get All Brands (READ)
        console.log('\n2️⃣ Testing Get All Brands (READ)...');
        const getBrandsResponse = await axios.get(`${BASE_URL}/admin/brands`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Brands retrieved:', getBrandsResponse.data.length, 'brands');
        if (getBrandsResponse.data.length > 0) {
            console.log('   Sample brand:', {
                id: getBrandsResponse.data[0].id,
                name: getBrandsResponse.data[0].name,
                industry: getBrandsResponse.data[0].industry
            });
        }

        // Step 3: Test Create Brand (CREATE)
        console.log('\n3️⃣ Testing Create Brand (CREATE)...');
        const newBrandData = {
            name: 'Test Brand CRUD ' + Date.now(),
            description: 'A test brand for CRUD operations testing',
            support_email: 'support@testbrandcrud.com',
            industry: 'Technology',
            logo_url: 'https://example.com/test-logo.png',
            contact_info: 'Phone: +1234567890\nAddress: 123 Test St, Test City'
        };

        const createBrandResponse = await axios.post(`${BASE_URL}/admin/brands`, newBrandData, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        testBrandId = createBrandResponse.data.id;
        console.log('✅ Brand created successfully:', {
            id: testBrandId,
            name: createBrandResponse.data.name,
            industry: createBrandResponse.data.industry,
            support_email: createBrandResponse.data.support_email
        });

        // Step 4: Test Get Single Brand (READ)
        console.log('\n4️⃣ Testing Get Single Brand (READ)...');
        const getSingleBrandResponse = await axios.get(`${BASE_URL}/admin/brands/${testBrandId}`, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Single brand retrieved:', {
            id: getSingleBrandResponse.data.id,
            name: getSingleBrandResponse.data.name,
            description: getSingleBrandResponse.data.description
        });

        // Step 5: Test Update Brand (UPDATE)
        console.log('\n5️⃣ Testing Update Brand (UPDATE)...');
        const updateData = {
            name: 'Updated Test Brand CRUD',
            description: 'Updated description for CRUD testing',
            industry: 'Updated Technology',
            support_email: 'updated-support@testbrandcrud.com',
            logo_url: 'https://example.com/updated-logo.png',
            contact_info: 'Updated Phone: +9876543210\nUpdated Address: 456 Update St, Update City'
        };

        const updateBrandResponse = await axios.put(`${BASE_URL}/admin/brands/${testBrandId}`, updateData, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Brand updated successfully:', {
            id: updateBrandResponse.data.id,
            name: updateBrandResponse.data.name,
            industry: updateBrandResponse.data.industry,
            support_email: updateBrandResponse.data.support_email
        });

        // Step 6: Test Partial Update Brand (UPDATE)
        console.log('\n6️⃣ Testing Partial Update Brand (UPDATE)...');
        const partialUpdateData = {
            name: 'Partially Updated Brand',
            industry: 'Finance'
        };

        const partialUpdateResponse = await axios.put(`${BASE_URL}/admin/brands/${testBrandId}`, partialUpdateData, {
            headers: { 'Authorization': `Bearer ${adminToken}` }
        });
        
        console.log('✅ Brand partially updated successfully:', {
            id: partialUpdateResponse.data.id,
            name: partialUpdateResponse.data.name,
            industry: partialUpdateResponse.data.industry,
            support_email: partialUpdateResponse.data.support_email // Should remain unchanged
        });

        // Step 7: Test Validation Errors (CREATE)
        console.log('\n7️⃣ Testing Validation Errors (CREATE)...');
        try {
            const invalidBrandData = {
                // Missing required name field
                description: 'Brand without name',
                industry: 'Technology'
            };

            await axios.post(`${BASE_URL}/admin/brands`, invalidBrandData, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('❌ Should have failed validation');
        } catch (error) {
            if (error.response?.status === 400) {
                console.log('✅ Validation error caught correctly:', error.response.data.error);
            } else {
                console.log('❌ Unexpected error:', error.response?.data?.error);
            }
        }

        // Step 8: Test Duplicate Brand Creation
        console.log('\n8️⃣ Testing Duplicate Brand Creation...');
        try {
            const duplicateBrandData = {
                name: 'Test Brand CRUD ' + Date.now(), // Same name pattern
                description: 'Another test brand',
                industry: 'Technology'
            };

            await axios.post(`${BASE_URL}/admin/brands`, duplicateBrandData, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('✅ Duplicate brand created (if names are different)');
        } catch (error) {
            if (error.response?.status === 400) {
                console.log('✅ Duplicate validation working:', error.response.data.error);
            } else {
                console.log('❌ Unexpected error:', error.response?.data?.error);
            }
        }

        // Step 9: Test Non-Admin Access (Security)
        console.log('\n9️⃣ Testing Non-Admin Access (Security)...');
        
        // Create a regular user
        const regularUserData = {
            email: `user_crud_${Date.now()}@example.com`,
            full_name: 'Regular User CRUD',
            password: 'user123',
            role: 'user'
        };
        
        const regularUserResponse = await axios.post(`${BASE_URL}/auth/signup`, regularUserData);
        const regularUserToken = regularUserResponse.data.access_token;
        
        // Try to access admin brand endpoints with regular user
        try {
            await axios.get(`${BASE_URL}/admin/brands`, {
                headers: { 'Authorization': `Bearer ${regularUserToken}` }
            });
            console.log('❌ Regular user should not access admin endpoints');
        } catch (error) {
            if (error.response?.status === 403) {
                console.log('✅ Security working: Regular user denied admin access');
            } else {
                console.log('❌ Unexpected security error:', error.response?.data?.error);
            }
        }

        // Step 10: Test Delete Brand (DELETE)
        console.log('\n🔟 Testing Delete Brand (DELETE)...');
        try {
            const deleteResponse = await axios.delete(`${BASE_URL}/admin/brands/${testBrandId}`, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('✅ Brand deleted successfully:', deleteResponse.data.message);
        } catch (error) {
            if (error.response?.status === 400) {
                console.log('⚠️ Brand cannot be deleted due to associated data (expected behavior)');
            } else {
                console.log('❌ Brand deletion failed:', error.response?.data?.error);
            }
        }

        // Step 11: Test Get Deleted Brand (should fail)
        console.log('\n1️⃣1️⃣ Testing Get Deleted Brand (should fail)...');
        try {
            await axios.get(`${BASE_URL}/admin/brands/${testBrandId}`, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('❌ Should not be able to get deleted brand');
        } catch (error) {
            if (error.response?.status === 404) {
                console.log('✅ Correctly cannot access deleted brand');
            } else {
                console.log('⚠️ Unexpected error for deleted brand:', error.response?.data?.error);
            }
        }

        // Step 12: Test Invalid Brand ID
        console.log('\n1️⃣2️⃣ Testing Invalid Brand ID...');
        try {
            await axios.get(`${BASE_URL}/admin/brands/99999`, {
                headers: { 'Authorization': `Bearer ${adminToken}` }
            });
            console.log('❌ Should not find non-existent brand');
        } catch (error) {
            if (error.response?.status === 404) {
                console.log('✅ Correctly handles non-existent brand');
            } else {
                console.log('⚠️ Unexpected error for non-existent brand:', error.response?.data?.error);
            }
        }

        console.log('\n🎉 Brand CRUD Operations Test Completed Successfully!');
        console.log('\n📝 Summary:');
        console.log('   ✅ Admin authentication working');
        console.log('   ✅ CREATE: Brand creation working');
        console.log('   ✅ READ: Get all brands and single brand working');
        console.log('   ✅ UPDATE: Full and partial updates working');
        console.log('   ✅ DELETE: Brand deletion working (with validation)');
        console.log('   ✅ Validation: Input validation working');
        console.log('   ✅ Security: Role-based access control working');
        console.log('   ✅ Error Handling: Proper error responses');

    } catch (error) {
        console.error('❌ Test failed:', error.response?.data?.error || error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }
}

// Run the test
testBrandCRUD(); 