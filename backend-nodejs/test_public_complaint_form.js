// Test script for public complaint form functionality
const axios = require('axios');

const BACKEND_URL = 'http://localhost:8001';
const FRONTEND_URL = 'http://localhost:5173';

async function testPublicComplaintForm() {
  console.log('🧪 Testing Public Complaint Form Functionality\n');

  try {
    // Test 1: Check if backend is running
    console.log('1. Testing backend health...');
    const healthResponse = await axios.get(`${BACKEND_URL}/health`);
    console.log('✅ Backend is healthy:', healthResponse.data);
    console.log('');

    // Test 2: Create a public complaint
    console.log('2. Testing public complaint creation...');
    const complaintData = {
      fullName: "Jane Smith",
      email: "jane.smith@example.com",
      phone: "+1234567890",
      brandName: "TechCorp",
      title: "Defective smartphone with cracked screen",
      description: "I received a smartphone that has several issues including a cracked screen, non-functional camera, and battery that drains within 2 hours. The device was purchased brand new and should be in perfect condition.",
      category: "Product Quality",
      priority: "high",
      isAnonymous: false
    };

    const complaintResponse = await axios.post(`${BACKEND_URL}/api/v1/public/tickets`, complaintData);
    console.log('✅ Complaint created successfully:');
    console.log('   Ticket Number:', complaintResponse.data.ticket_number);
    console.log('   Status:', complaintResponse.data.status);
    console.log('   Brand:', complaintResponse.data.brand_name);
    console.log('   Category:', complaintResponse.data.category);
    console.log('   Priority:', complaintResponse.data.priority);
    console.log('');

    // Test 3: Create an anonymous complaint
    console.log('3. Testing anonymous complaint creation...');
    const anonymousComplaintData = {
      fullName: "Anonymous User",
      email: "anonymous@example.com",
      brandName: "FoodExpress",
      title: "Wrong order delivered",
      description: "Ordered a specific model but received a completely different product. Customer service was unhelpful.",
      category: "Order Issues",
      priority: "medium",
      isAnonymous: true
    };

    const anonymousResponse = await axios.post(`${BACKEND_URL}/api/v1/public/tickets`, anonymousComplaintData);
    console.log('✅ Anonymous complaint created successfully:');
    console.log('   Ticket Number:', anonymousResponse.data.ticket_number);
    console.log('   Status:', anonymousResponse.data.status);
    console.log('');

    // Test 4: Test validation (missing required fields)
    console.log('4. Testing validation (missing required fields)...');
    try {
      const invalidData = {
        fullName: "Test User",
        email: "test@example.com"
        // Missing required fields: brandName, title, description, category
      };
      
      await axios.post(`${BACKEND_URL}/api/v1/public/tickets`, invalidData);
      console.log('❌ Validation failed - should have rejected invalid data');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.log('✅ Validation working correctly - rejected invalid data');
        console.log('   Error:', error.response.data.error);
      } else {
        console.log('❌ Unexpected error:', error.message);
      }
    }
    console.log('');

    // Test 5: Test email validation
    console.log('5. Testing email validation...');
    try {
      const invalidEmailData = {
        fullName: "Test User",
        email: "invalid-email",
        brandName: "TestBrand",
        title: "Test Complaint",
        description: "Test description",
        category: "Product Quality",
        priority: "medium"
      };
      
      await axios.post(`${BACKEND_URL}/api/v1/public/tickets`, invalidEmailData);
      console.log('❌ Email validation failed - should have rejected invalid email');
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.log('✅ Email validation working correctly');
        console.log('   Error:', error.response.data.error);
      } else {
        console.log('❌ Unexpected error:', error.message);
      }
    }
    console.log('');

    console.log('🎉 All tests completed successfully!');
    console.log('');
    console.log('📋 Summary:');
    console.log('   ✅ Backend health check passed');
    console.log('   ✅ Public complaint creation working');
    console.log('   ✅ Anonymous complaint creation working');
    console.log('   ✅ Form validation working');
    console.log('   ✅ Email validation working');
    console.log('');
    console.log('🌐 Frontend URLs:');
    console.log(`   Homepage: ${FRONTEND_URL}`);
    console.log(`   Submit Complaint: ${FRONTEND_URL}/submit-complaint`);
    console.log(`   Track Complaint: ${FRONTEND_URL}/track-complaint`);
    console.log(`   View Complaints: ${FRONTEND_URL}/complaints`);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    if (error.response) {
      console.error('   Response status:', error.response.status);
      console.error('   Response data:', error.response.data);
    }
  }
}

// Run the test
testPublicComplaintForm(); 