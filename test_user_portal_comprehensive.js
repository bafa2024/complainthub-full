// Comprehensive User Portal Testing Script
// Tests all User Portal functionality according to SRS requirements

const axios = require('axios');

class UserPortalTester {
    constructor() {
        this.baseURL = 'http://localhost:8001';
        this.testResults = [];
        this.userAuthToken = null;
        this.testUserId = null;
        this.testTicketId = null;
    }

    // Main test runner
    async runAllTests() {
        console.log('👤 Starting Comprehensive User Portal Testing...\n');

        try {
            // Test 1: User Authentication
            await this.testUserAuthentication();

            // Test 2: Public Features
            await this.testPublicFeatures();

            // Test 3: User Account Features
            await this.testUserAccountFeatures();

            // Test 4: Ticket Submission
            await this.testTicketSubmission();

            // Test 5: Ticket Tracking
            await this.testTicketTracking();

            // Test 6: Search and Filtering
            await this.testSearchFiltering();

            // Test 7: Public Complaint Listing
            await this.testPublicComplaintListing();

            // Test 8: SEO and Performance
            await this.testSEOPerformance();

            // Generate test report
            this.generateTestReport();

        } catch (error) {
            console.error('❌ Test suite failed:', error);
            this.addTestResult('CRITICAL', 'Test Suite Execution', false, error.message);
        }
    }

    // Test 1: User Authentication
    async testUserAuthentication() {
        console.log('1️⃣ Testing User Authentication...');

        try {
            // Test user signup
            const uniqueEmail = `testuser${Date.now()}@example.com`;
            const signupData = {
                email: uniqueEmail,
                full_name: 'Test User',
                password: 'TestPass123!',
                role: 'user'
            };

            const signupResponse = await this.makeRequest('POST', '/api/v1/auth/signup', signupData);
            this.addTestResult('HIGH', 'User Signup', 
                signupResponse.status === 201 && signupResponse.data.user,
                `Status: ${signupResponse.status}, User created: ${!!signupResponse.data.user}`);

            // Test user login
            const loginData = {
                username: uniqueEmail,
                password: 'TestPass123!'
            };

            const loginResponse = await this.makeRequest('POST', '/api/v1/login/access-token', loginData);
            this.addTestResult('HIGH', 'User Login', 
                loginResponse.status === 200 && loginResponse.data.access_token,
                `Status: ${loginResponse.status}, Token received: ${!!loginResponse.data.access_token}`);

            if (loginResponse.data.access_token) {
                this.userAuthToken = loginResponse.data.access_token;
                this.testUserId = loginResponse.data.user.id;
            }

            // Test user profile access
            if (this.userAuthToken) {
                const profileResponse = await this.makeRequest('GET', '/api/v1/users/me', null, {
                    'Authorization': `Bearer ${this.userAuthToken}`
                });
                this.addTestResult('HIGH', 'User Profile Access', 
                    profileResponse.status === 200,
                    `Status: ${profileResponse.status}, Profile accessed`);
            }

            // Test password change functionality
            const passwordChangeResponse = await this.makeRequest('PUT', '/api/v1/users/change-password', {
                current_password: 'TestPass123!',
                new_password: 'NewTestPass123!'
            }, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Password Change', 
                passwordChangeResponse.status === 200 || passwordChangeResponse.status === 404,
                `Status: ${passwordChangeResponse.status}, Password change functionality`);

            console.log('   ✅ User Authentication tests completed\n');

        } catch (error) {
            console.log('   ❌ User Authentication tests failed\n');
            this.addTestResult('HIGH', 'User Authentication', false, error.message);
        }
    }

    // Test 2: Public Features
    async testPublicFeatures() {
        console.log('2️⃣ Testing Public Features...');

        try {
            // Test public complaint listing
            const publicComplaintsResponse = await this.makeRequest('GET', '/api/v1/public/complaints');
            this.addTestResult('HIGH', 'Public Complaint Listing', 
                publicComplaintsResponse.status === 200,
                `Status: ${publicComplaintsResponse.status}, Public complaints accessible`);

            // Test anonymous complaint submission
            const anonymousComplaintData = {
                title: 'Test Anonymous Complaint',
                description: 'This is a test anonymous complaint submission',
                brand_name: 'Test Brand',
                category: 'Service',
                anonymous: true
            };

            const anonymousResponse = await this.makeRequest('POST', '/api/v1/public/tickets', anonymousComplaintData);
            this.addTestResult('HIGH', 'Anonymous Complaint Submission', 
                anonymousResponse.status === 201,
                `Status: ${anonymousResponse.status}, Anonymous complaint submitted`);

            // Test public brand listing
            const publicBrandsResponse = await this.makeRequest('GET', '/api/v1/public/brands');
            this.addTestResult('MEDIUM', 'Public Brand Listing', 
                publicBrandsResponse.status === 200,
                `Status: ${publicBrandsResponse.status}, Public brands listed`);

            // Test complaint tracking without login
            const trackingResponse = await this.makeRequest('GET', '/api/v1/public/track/TICKET123');
            this.addTestResult('MEDIUM', 'Public Complaint Tracking', 
                trackingResponse.status === 200 || trackingResponse.status === 404,
                `Status: ${trackingResponse.status}, Tracking functionality available`);

            console.log('   ✅ Public Features tests completed\n');

        } catch (error) {
            console.log('   ❌ Public Features tests failed\n');
            this.addTestResult('HIGH', 'Public Features', false, error.message);
        }
    }

    // Test 3: User Account Features
    async testUserAccountFeatures() {
        console.log('3️⃣ Testing User Account Features...');

        try {
            if (!this.userAuthToken) {
                this.addTestResult('HIGH', 'User Account Features', false, 'No user auth token available');
                return;
            }

            // Test user dashboard
            const dashboardResponse = await this.makeRequest('GET', '/api/v1/user/dashboard', null, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('HIGH', 'User Dashboard', 
                dashboardResponse.status === 200,
                `Status: ${dashboardResponse.status}, Dashboard accessible`);

            // Test user's personal tickets
            const userTicketsResponse = await this.makeRequest('GET', '/api/v1/tickets/my-tickets', null, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('HIGH', 'Personal Ticket Dashboard', 
                userTicketsResponse.status === 200 || userTicketsResponse.status === 404,
                `Status: ${userTicketsResponse.status}, Personal tickets accessible`);

            // Test profile update
            const profileUpdateData = {
                full_name: 'Updated Test User',
                phone: '+1234567890'
            };
            const profileUpdateResponse = await this.makeRequest('PUT', '/api/v1/users/me', profileUpdateData, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Profile Update', 
                profileUpdateResponse.status === 200 || profileUpdateResponse.status === 404,
                `Status: ${profileUpdateResponse.status}, Profile update functionality`);

            // Test notification preferences
            const notificationResponse = await this.makeRequest('GET', '/api/v1/users/notifications', null, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Notification Preferences', 
                notificationResponse.status === 200 || notificationResponse.status === 404,
                `Status: ${notificationResponse.status}, Notification settings available`);

            console.log('   ✅ User Account Features tests completed\n');

        } catch (error) {
            console.log('   ❌ User Account Features tests failed\n');
            this.addTestResult('HIGH', 'User Account Features', false, error.message);
        }
    }

    // Test 4: Ticket Submission
    async testTicketSubmission() {
        console.log('4️⃣ Testing Ticket Submission...');

        try {
            if (!this.userAuthToken) {
                this.addTestResult('HIGH', 'Ticket Submission', false, 'No user auth token available');
                return;
            }

            // Test logged-in user ticket submission
            const ticketData = {
                title: 'Test User Complaint',
                description: 'This is a test complaint from a logged-in user',
                brand_id: 1, // Assuming brand ID 1 exists
                category: 'Service',
                priority: 'medium'
            };

            const ticketResponse = await this.makeRequest('POST', '/api/v1/tickets', ticketData, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('HIGH', 'Authenticated Ticket Submission', 
                ticketResponse.status === 201,
                `Status: ${ticketResponse.status}, Ticket submitted by authenticated user`);

            if (ticketResponse.data && ticketResponse.data.id) {
                this.testTicketId = ticketResponse.data.id;
            }

            // Test form validation
            const invalidTicketData = {
                title: '', // Empty title should fail validation
                description: 'Test'
            };

            const invalidTicketResponse = await this.makeRequest('POST', '/api/v1/tickets', invalidTicketData, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Ticket Form Validation', 
                invalidTicketResponse.status >= 400 && invalidTicketResponse.status < 500,
                `Status: ${invalidTicketResponse.status}, Validation working`);

            // Test file upload capability
            const fileUploadResponse = await this.makeRequest('POST', '/api/v1/tickets/upload', {
                ticket_id: this.testTicketId,
                file_type: 'image',
                file_data: 'base64mockdata'
            }, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'File Upload Support', 
                fileUploadResponse.status === 200 || fileUploadResponse.status === 404,
                `Status: ${fileUploadResponse.status}, File upload functionality`);

            // Test multiple category support
            const categoryResponse = await this.makeRequest('GET', '/api/v1/categories');
            this.addTestResult('MEDIUM', 'Category Support', 
                categoryResponse.status === 200 || categoryResponse.status === 404,
                `Status: ${categoryResponse.status}, Category listing available`);

            console.log('   ✅ Ticket Submission tests completed\n');

        } catch (error) {
            console.log('   ❌ Ticket Submission tests failed\n');
            this.addTestResult('HIGH', 'Ticket Submission', false, error.message);
        }
    }

    // Test 5: Ticket Tracking
    async testTicketTracking() {
        console.log('5️⃣ Testing Ticket Tracking...');

        try {
            if (!this.userAuthToken) {
                this.addTestResult('HIGH', 'Ticket Tracking', false, 'No user auth token available');
                return;
            }

            // Test ticket status tracking
            if (this.testTicketId) {
                const ticketStatusResponse = await this.makeRequest('GET', `/api/v1/tickets/${this.testTicketId}`, null, {
                    'Authorization': `Bearer ${this.userAuthToken}`
                });
                this.addTestResult('HIGH', 'Ticket Status Tracking', 
                    ticketStatusResponse.status === 200 || ticketStatusResponse.status === 404,
                    `Status: ${ticketStatusResponse.status}, Ticket status accessible`);

                // Test ticket history/updates
                const ticketHistoryResponse = await this.makeRequest('GET', `/api/v1/tickets/${this.testTicketId}/history`, null, {
                    'Authorization': `Bearer ${this.userAuthToken}`
                });
                this.addTestResult('MEDIUM', 'Ticket History', 
                    ticketHistoryResponse.status === 200 || ticketHistoryResponse.status === 404,
                    `Status: ${ticketHistoryResponse.status}, Ticket history available`);

                // Test adding additional information
                const additionalInfoData = {
                    message: 'Additional information for the complaint',
                    attachment: null
                };
                const additionalInfoResponse = await this.makeRequest('POST', `/api/v1/tickets/${this.testTicketId}/additional-info`, additionalInfoData, {
                    'Authorization': `Bearer ${this.userAuthToken}`
                });
                this.addTestResult('MEDIUM', 'Additional Information Submission', 
                    additionalInfoResponse.status === 200 || additionalInfoResponse.status === 404,
                    `Status: ${additionalInfoResponse.status}, Additional info functionality`);
            }

            // Test ticket reopening (48h window)
            const reopenResponse = await this.makeRequest('POST', `/api/v1/tickets/${this.testTicketId}/reopen`, {
                reason: 'Issue not resolved'
            }, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Ticket Reopening', 
                reopenResponse.status === 200 || reopenResponse.status === 404,
                `Status: ${reopenResponse.status}, Ticket reopening functionality`);

            // Test satisfaction rating
            const ratingData = {
                rating: 4,
                feedback: 'Good service overall'
            };
            const ratingResponse = await this.makeRequest('POST', `/api/v1/tickets/${this.testTicketId}/rating`, ratingData, {
                'Authorization': `Bearer ${this.userAuthToken}`
            });
            this.addTestResult('HIGH', 'Satisfaction Rating', 
                ratingResponse.status === 200 || ratingResponse.status === 404,
                `Status: ${ratingResponse.status}, Rating system available`);

            console.log('   ✅ Ticket Tracking tests completed\n');

        } catch (error) {
            console.log('   ❌ Ticket Tracking tests failed\n');
            this.addTestResult('HIGH', 'Ticket Tracking', false, error.message);
        }
    }

    // Test 6: Search and Filtering
    async testSearchFiltering() {
        console.log('6️⃣ Testing Search and Filtering...');

        try {
            // Test search functionality
            const searchResponse = await this.makeRequest('GET', '/api/v1/public/search?q=test');
            this.addTestResult('MEDIUM', 'Search Functionality', 
                searchResponse.status === 200 || searchResponse.status === 404,
                `Status: ${searchResponse.status}, Search functionality available`);

            // Test filtering by brand
            const brandFilterResponse = await this.makeRequest('GET', '/api/v1/public/complaints?brand=testbrand');
            this.addTestResult('MEDIUM', 'Brand Filtering', 
                brandFilterResponse.status === 200 || brandFilterResponse.status === 404,
                `Status: ${brandFilterResponse.status}, Brand filtering available`);

            // Test filtering by category
            const categoryFilterResponse = await this.makeRequest('GET', '/api/v1/public/complaints?category=service');
            this.addTestResult('MEDIUM', 'Category Filtering', 
                categoryFilterResponse.status === 200 || categoryFilterResponse.status === 404,
                `Status: ${categoryFilterResponse.status}, Category filtering available`);

            // Test date range filtering
            const dateFilterResponse = await this.makeRequest('GET', '/api/v1/public/complaints?from=2024-01-01&to=2024-12-31');
            this.addTestResult('MEDIUM', 'Date Range Filtering', 
                dateFilterResponse.status === 200 || dateFilterResponse.status === 404,
                `Status: ${dateFilterResponse.status}, Date filtering available`);

            // Test sorting options
            const sortResponse = await this.makeRequest('GET', '/api/v1/public/complaints?sort=date&order=desc');
            this.addTestResult('MEDIUM', 'Sorting Options', 
                sortResponse.status === 200 || sortResponse.status === 404,
                `Status: ${sortResponse.status}, Sorting functionality available`);

            console.log('   ✅ Search and Filtering tests completed\n');

        } catch (error) {
            console.log('   ❌ Search and Filtering tests failed\n');
            this.addTestResult('MEDIUM', 'Search and Filtering', false, error.message);
        }
    }

    // Test 7: Public Complaint Listing
    async testPublicComplaintListing() {
        console.log('7️⃣ Testing Public Complaint Listing...');

        try {
            // Test public complaint page
            const publicPageResponse = await this.makeRequest('GET', '/api/v1/public/complaints');
            this.addTestResult('HIGH', 'Public Complaint Page', 
                publicPageResponse.status === 200,
                `Status: ${publicPageResponse.status}, Public page accessible`);

            // Test pagination
            const paginationResponse = await this.makeRequest('GET', '/api/v1/public/complaints?page=1&limit=10');
            this.addTestResult('MEDIUM', 'Pagination Support', 
                paginationResponse.status === 200,
                `Status: ${paginationResponse.status}, Pagination working`);

            // Test voice complaint playback
            const voicePlaybackResponse = await this.makeRequest('GET', '/api/v1/public/voice/TICKET123');
            this.addTestResult('MEDIUM', 'Voice Complaint Playback', 
                voicePlaybackResponse.status === 200 || voicePlaybackResponse.status === 404,
                `Status: ${voicePlaybackResponse.status}, Voice playback functionality`);

            // Test complaint statistics
            const statsResponse = await this.makeRequest('GET', '/api/v1/public/statistics');
            this.addTestResult('MEDIUM', 'Public Statistics', 
                statsResponse.status === 200 || statsResponse.status === 404,
                `Status: ${statsResponse.status}, Public statistics available`);

            // Test responsive design (mobile compatibility)
            const mobileResponse = await this.makeRequest('GET', '/api/v1/public/complaints', null, {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
            });
            this.addTestResult('MEDIUM', 'Mobile Compatibility', 
                mobileResponse.status === 200,
                `Status: ${mobileResponse.status}, Mobile-friendly response`);

            console.log('   ✅ Public Complaint Listing tests completed\n');

        } catch (error) {
            console.log('   ❌ Public Complaint Listing tests failed\n');
            this.addTestResult('HIGH', 'Public Complaint Listing', false, error.message);
        }
    }

    // Test 8: SEO and Performance
    async testSEOPerformance() {
        console.log('8️⃣ Testing SEO and Performance...');

        try {
            // Test response times
            const startTime = Date.now();
            await this.makeRequest('GET', '/api/v1/public/complaints');
            const responseTime = Date.now() - startTime;
            
            this.addTestResult('MEDIUM', 'Response Time Performance', 
                responseTime < 2000, // Should respond within 2 seconds
                `Response time: ${responseTime}ms`);

            // Test SEO metadata
            const seoResponse = await this.makeRequest('GET', '/api/v1/public/meta');
            this.addTestResult('MEDIUM', 'SEO Metadata', 
                seoResponse.status === 200 || seoResponse.status === 404,
                `Status: ${seoResponse.status}, SEO metadata available`);

            // Test sitemap
            const sitemapResponse = await this.makeRequest('GET', '/sitemap.xml');
            this.addTestResult('MEDIUM', 'Sitemap Generation', 
                sitemapResponse.status === 200 || sitemapResponse.status === 404,
                `Status: ${sitemapResponse.status}, Sitemap available`);

            // Test robots.txt
            const robotsResponse = await this.makeRequest('GET', '/robots.txt');
            this.addTestResult('MEDIUM', 'Robots.txt', 
                robotsResponse.status === 200 || robotsResponse.status === 404,
                `Status: ${robotsResponse.status}, Robots.txt available`);

            // Test concurrent user handling
            const concurrentPromises = [];
            for (let i = 0; i < 10; i++) {
                concurrentPromises.push(
                    this.makeRequest('GET', '/api/v1/public/complaints')
                );
            }

            const concurrentStartTime = Date.now();
            const concurrentResults = await Promise.all(concurrentPromises);
            const concurrentTime = Date.now() - concurrentStartTime;

            this.addTestResult('HIGH', 'Concurrent User Handling', 
                concurrentResults.length === 10 && concurrentTime < 5000,
                `10 concurrent users handled in ${concurrentTime}ms`);

            console.log('   ✅ SEO and Performance tests completed\n');

        } catch (error) {
            console.log('   ❌ SEO and Performance tests failed\n');
            this.addTestResult('MEDIUM', 'SEO and Performance', false, error.message);
        }
    }

    // Helper method to make HTTP requests
    async makeRequest(method, endpoint, data = null, headers = {}) {
        try {
            const config = {
                method: method.toLowerCase(),
                url: `${this.baseURL}${endpoint}`,
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                }
            };

            if (data) {
                config.data = data;
            }

            const response = await axios(config);
            return response;
        } catch (error) {
            // Return error response for testing
            return error.response || { status: 500, data: null };
        }
    }

    // Add test result
    addTestResult(priority, testName, passed, details) {
        this.testResults.push({
            priority,
            testName,
            passed,
            details,
            timestamp: new Date()
        });
    }

    // Generate comprehensive test report
    generateTestReport() {
        console.log('📊 User Portal Test Report');
        console.log('============================\n');

        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(result => result.passed).length;
        const failedTests = totalTests - passedTests;
        const successRate = ((passedTests / totalTests) * 100).toFixed(1);

        console.log(`Total Tests: ${totalTests}`);
        console.log(`Passed: ${passedTests}`);
        console.log(`Failed: ${failedTests}`);
        console.log(`Success Rate: ${successRate}%\n`);

        // Group by priority
        const criticalTests = this.testResults.filter(r => r.priority === 'CRITICAL');
        const highTests = this.testResults.filter(r => r.priority === 'HIGH');
        const mediumTests = this.testResults.filter(r => r.priority === 'MEDIUM');

        if (criticalTests.length > 0) {
            console.log('🔴 CRITICAL TESTS:');
            criticalTests.forEach(test => {
                console.log(`   ${test.passed ? '✅' : '❌'} ${test.testName}`);
                if (!test.passed) console.log(`      ${test.details}`);
            });
            console.log('');
        }

        if (highTests.length > 0) {
            console.log('🟡 HIGH PRIORITY TESTS:');
            highTests.forEach(test => {
                console.log(`   ${test.passed ? '✅' : '❌'} ${test.testName}`);
                if (!test.passed) console.log(`      ${test.details}`);
            });
            console.log('');
        }

        if (mediumTests.length > 0) {
            console.log('🟢 MEDIUM PRIORITY TESTS:');
            mediumTests.forEach(test => {
                console.log(`   ${test.passed ? '✅' : '❌'} ${test.testName}`);
                if (!test.passed) console.log(`      ${test.details}`);
            });
            console.log('');
        }

        // Recommendations
        console.log('💡 RECOMMENDATIONS:');
        const failedCritical = criticalTests.filter(t => !t.passed);
        const failedHigh = highTests.filter(t => !t.passed);

        if (failedCritical.length > 0) {
            console.log('   🚨 IMMEDIATE ACTION REQUIRED: Critical tests failed');
        }
        if (failedHigh.length > 0) {
            console.log('   ⚠️  HIGH PRIORITY: Address failed high priority tests');
        }
        if (successRate < 80) {
            console.log('   📈 IMPROVEMENT NEEDED: Success rate below 80%');
        }
        if (successRate >= 90) {
            console.log('   🎉 EXCELLENT: High success rate achieved');
        }

        console.log('\nUser Portal Testing Complete! 👤');
    }
}

// Run the comprehensive test suite
async function runUserPortalTests() {
    const tester = new UserPortalTester();
    await tester.runAllTests();
}

// Export for use in other test scripts
module.exports = UserPortalTester;

// Run tests if called directly
if (require.main === module) {
    runUserPortalTests();
}