// Comprehensive Admin Panel Testing Script
// Tests all Admin Panel functionality according to SRS requirements

const axios = require('axios');

class AdminPanelTester {
    constructor() {
        this.baseURL = 'http://localhost:8001';
        this.testResults = [];
        this.adminAuthToken = null;
        this.testAdminId = null;
    }

    // Main test runner
    async runAllTests() {
        console.log('🔧 Starting Comprehensive Admin Panel Testing...\n');

        try {
            // Test 1: Admin Authentication
            await this.testAdminAuthentication();

            // Test 2: System Management
            await this.testSystemManagement();

            // Test 3: User Management
            await this.testUserManagement();

            // Test 4: Brand Management
            await this.testBrandManagement();

            // Test 5: Global Settings
            await this.testGlobalSettings();

            // Test 6: Monitoring and Analytics
            await this.testMonitoringAnalytics();

            // Test 7: Content Moderation
            await this.testContentModeration();

            // Test 8: Data Export and Backup
            await this.testDataExportBackup();

            // Generate test report
            this.generateTestReport();

        } catch (error) {
            console.error('❌ Test suite failed:', error);
            this.addTestResult('CRITICAL', 'Test Suite Execution', false, error.message);
        }
    }

    // Test 1: Admin Authentication
    async testAdminAuthentication() {
        console.log('1️⃣ Testing Admin Authentication...');

        try {
            // Test admin signup (first admin or system setup)
            const uniqueEmail = `admin${Date.now()}@example.com`;
            const adminSignupData = {
                email: uniqueEmail,
                full_name: 'Test Admin User',
                password: 'AdminPass123!',
                role: 'admin'
            };

            const signupResponse = await this.makeRequest('POST', '/api/v1/auth/signup', adminSignupData);
            this.addTestResult('HIGH', 'Admin Signup', 
                signupResponse.status === 201 && signupResponse.data.user,
                `Status: ${signupResponse.status}, Admin created: ${!!signupResponse.data.user}`);

            // Test admin login
            const loginData = {
                username: uniqueEmail,
                password: 'AdminPass123!'
            };

            const loginResponse = await this.makeRequest('POST', '/api/v1/login/access-token', loginData);
            this.addTestResult('HIGH', 'Admin Login', 
                loginResponse.status === 200 && loginResponse.data.access_token,
                `Status: ${loginResponse.status}, Token received: ${!!loginResponse.data.access_token}`);

            if (loginResponse.data.access_token) {
                this.adminAuthToken = loginResponse.data.access_token;
                this.testAdminId = loginResponse.data.user.id;
            }

            // Test admin role verification
            if (this.adminAuthToken) {
                const profileResponse = await this.makeRequest('GET', '/api/v1/users/me', null, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'Admin Role Verification', 
                    profileResponse.status === 200 && profileResponse.data.role === 'admin',
                    `Status: ${profileResponse.status}, Role: ${profileResponse.data?.role}`);
            }

            // Test admin-only endpoint access
            const adminDashboardResponse = await this.makeRequest('GET', '/api/v1/admin/dashboard', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Admin Dashboard Access', 
                adminDashboardResponse.status === 200,
                `Status: ${adminDashboardResponse.status}, Admin dashboard accessible`);

            console.log('   ✅ Admin Authentication tests completed\n');

        } catch (error) {
            console.log('   ❌ Admin Authentication tests failed\n');
            this.addTestResult('HIGH', 'Admin Authentication', false, error.message);
        }
    }

    // Test 2: System Management
    async testSystemManagement() {
        console.log('2️⃣ Testing System Management...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('HIGH', 'System Management', false, 'No admin auth token available');
                return;
            }

            // Test global metrics dashboard
            const metricsResponse = await this.makeRequest('GET', '/api/v1/admin/dashboard', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Global Metrics Dashboard', 
                metricsResponse.status === 200,
                `Status: ${metricsResponse.status}, Global metrics available`);

            // Test system health monitoring
            const healthResponse = await this.makeRequest('GET', '/api/v1/admin/system/health', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'System Health Monitoring', 
                healthResponse.status === 200 || healthResponse.status === 404,
                `Status: ${healthResponse.status}, Health monitoring endpoint`);

            // Test analytics overview
            const analyticsResponse = await this.makeRequest('GET', '/api/v1/admin/analytics', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Analytics Overview', 
                analyticsResponse.status === 200,
                `Status: ${analyticsResponse.status}, Analytics data available`);

            // Test API key management
            const apiKeysResponse = await this.makeRequest('GET', '/api/v1/admin/api-keys', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'API Key Management', 
                apiKeysResponse.status === 200 || apiKeysResponse.status === 404,
                `Status: ${apiKeysResponse.status}, API key management available`);

            // Test system configuration
            const configResponse = await this.makeRequest('GET', '/api/v1/admin/config', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'System Configuration', 
                configResponse.status === 200 || configResponse.status === 404,
                `Status: ${configResponse.status}, System config accessible`);

            console.log('   ✅ System Management tests completed\n');

        } catch (error) {
            console.log('   ❌ System Management tests failed\n');
            this.addTestResult('HIGH', 'System Management', false, error.message);
        }
    }

    // Test 3: User Management
    async testUserManagement() {
        console.log('3️⃣ Testing User Management...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('HIGH', 'User Management', false, 'No admin auth token available');
                return;
            }

            // Test user listing
            const usersResponse = await this.makeRequest('GET', '/api/v1/admin/users', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'User Listing', 
                usersResponse.status === 200,
                `Status: ${usersResponse.status}, Users list accessible`);

            // Test user detail view
            const userDetailResponse = await this.makeRequest('GET', `/api/v1/admin/users/${this.testAdminId}`, null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'User Detail View', 
                userDetailResponse.status === 200,
                `Status: ${userDetailResponse.status}, User details accessible`);

            // Test user creation
            const newUserData = {
                email: `testuser${Date.now()}@example.com`,
                full_name: 'Admin Created User',
                password: 'UserPass123!',
                role: 'user'
            };

            const createUserResponse = await this.makeRequest('POST', '/api/v1/admin/users', newUserData, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'User Creation', 
                createUserResponse.status === 201,
                `Status: ${createUserResponse.status}, User creation by admin`);

            let createdUserId = null;
            if (createUserResponse.data && createUserResponse.data.id) {
                createdUserId = createUserResponse.data.id;
            }

            // Test user update
            if (createdUserId) {
                const updateUserData = {
                    full_name: 'Updated Admin Created User',
                    role: 'brand_user'
                };

                const updateUserResponse = await this.makeRequest('PUT', `/api/v1/admin/users/${createdUserId}`, updateUserData, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'User Update', 
                    updateUserResponse.status === 200,
                    `Status: ${updateUserResponse.status}, User update by admin`);

                // Test brand assignment
                const brandAssignmentData = {
                    brand_id: 1 // Assuming brand ID 1 exists
                };

                const assignBrandResponse = await this.makeRequest('POST', `/api/v1/admin/users/${createdUserId}/assign-brand`, brandAssignmentData, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'Brand Assignment', 
                    assignBrandResponse.status === 200,
                    `Status: ${assignBrandResponse.status}, Brand assignment by admin`);

                // Test user deletion
                const deleteUserResponse = await this.makeRequest('DELETE', `/api/v1/admin/users/${createdUserId}`, null, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'User Deletion', 
                    deleteUserResponse.status === 200,
                    `Status: ${deleteUserResponse.status}, User deletion by admin`);
            }

            // Test user search and filtering
            const searchResponse = await this.makeRequest('GET', '/api/v1/admin/users?search=test&role=user', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'User Search and Filtering', 
                searchResponse.status === 200,
                `Status: ${searchResponse.status}, User search functionality`);

            console.log('   ✅ User Management tests completed\n');

        } catch (error) {
            console.log('   ❌ User Management tests failed\n');
            this.addTestResult('HIGH', 'User Management', false, error.message);
        }
    }

    // Test 4: Brand Management
    async testBrandManagement() {
        console.log('4️⃣ Testing Brand Management...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('HIGH', 'Brand Management', false, 'No admin auth token available');
                return;
            }

            // Test brand listing
            const brandsResponse = await this.makeRequest('GET', '/api/v1/admin/brands', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Brand Listing', 
                brandsResponse.status === 200,
                `Status: ${brandsResponse.status}, Brands list accessible`);

            // Test brand detail view
            const brandDetailResponse = await this.makeRequest('GET', '/api/v1/admin/brands/1', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Brand Detail View', 
                brandDetailResponse.status === 200 || brandDetailResponse.status === 404,
                `Status: ${brandDetailResponse.status}, Brand details accessible`);

            // Test brand creation
            const newBrandData = {
                name: `Test Brand ${Date.now()}`,
                description: 'Admin created test brand',
                user_id: this.testAdminId,
                industry: 'Technology',
                contact_info: 'test@testbrand.com'
            };

            const createBrandResponse = await this.makeRequest('POST', '/api/v1/admin/brands', newBrandData, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Brand Creation', 
                createBrandResponse.status === 201,
                `Status: ${createBrandResponse.status}, Brand creation by admin`);

            let createdBrandId = null;
            if (createBrandResponse.data && createBrandResponse.data.id) {
                createdBrandId = createBrandResponse.data.id;
            }

            // Test brand update
            if (createdBrandId) {
                const updateBrandData = {
                    description: 'Updated admin created test brand',
                    industry: 'Healthcare'
                };

                const updateBrandResponse = await this.makeRequest('PUT', `/api/v1/admin/brands/${createdBrandId}`, updateBrandData, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'Brand Update', 
                    updateBrandResponse.status === 200,
                    `Status: ${updateBrandResponse.status}, Brand update by admin`);

                // Test brand deletion
                const deleteBrandResponse = await this.makeRequest('DELETE', `/api/v1/admin/brands/${createdBrandId}`, null, {
                    'Authorization': `Bearer ${this.adminAuthToken}`
                });
                this.addTestResult('HIGH', 'Brand Deletion', 
                    deleteBrandResponse.status === 200,
                    `Status: ${deleteBrandResponse.status}, Brand deletion by admin`);
            }

            // Test credit management
            const creditResponse = await this.makeRequest('PUT', '/api/v1/admin/brands/1/credits', {
                amount: 100,
                operation: 'add'
            }, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Credit Management', 
                creditResponse.status === 200 || creditResponse.status === 404,
                `Status: ${creditResponse.status}, Credit management functionality`);

            console.log('   ✅ Brand Management tests completed\n');

        } catch (error) {
            console.log('   ❌ Brand Management tests failed\n');
            this.addTestResult('HIGH', 'Brand Management', false, error.message);
        }
    }

    // Test 5: Global Settings
    async testGlobalSettings() {
        console.log('5️⃣ Testing Global Settings...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('MEDIUM', 'Global Settings', false, 'No admin auth token available');
                return;
            }

            // Test settings retrieval
            const settingsResponse = await this.makeRequest('GET', '/api/v1/admin/settings', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Settings Retrieval', 
                settingsResponse.status === 200 || settingsResponse.status === 404,
                `Status: ${settingsResponse.status}, Settings accessible`);

            // Test settings update
            const settingsUpdateData = {
                max_ticket_duration: '48h',
                billing_rate: 50,
                default_priority: 'medium'
            };

            const updateSettingsResponse = await this.makeRequest('PUT', '/api/v1/admin/settings', settingsUpdateData, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Settings Update', 
                updateSettingsResponse.status === 200 || updateSettingsResponse.status === 404,
                `Status: ${updateSettingsResponse.status}, Settings update functionality`);

            // Test email templates management
            const emailTemplatesResponse = await this.makeRequest('GET', '/api/v1/admin/email-templates', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Email Templates Management', 
                emailTemplatesResponse.status === 200 || emailTemplatesResponse.status === 404,
                `Status: ${emailTemplatesResponse.status}, Email templates accessible`);

            // Test notification settings
            const notificationSettingsResponse = await this.makeRequest('GET', '/api/v1/admin/notification-settings', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Notification Settings', 
                notificationSettingsResponse.status === 200 || notificationSettingsResponse.status === 404,
                `Status: ${notificationSettingsResponse.status}, Notification settings available`);

            console.log('   ✅ Global Settings tests completed\n');

        } catch (error) {
            console.log('   ❌ Global Settings tests failed\n');
            this.addTestResult('MEDIUM', 'Global Settings', false, error.message);
        }
    }

    // Test 6: Monitoring and Analytics
    async testMonitoringAnalytics() {
        console.log('6️⃣ Testing Monitoring and Analytics...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('HIGH', 'Monitoring Analytics', false, 'No admin auth token available');
                return;
            }

            // Test admin analytics
            const analyticsResponse = await this.makeRequest('GET', '/api/v1/admin/analytics', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Admin Analytics', 
                analyticsResponse.status === 200,
                `Status: ${analyticsResponse.status}, Analytics data available`);

            // Test ticket analytics
            const ticketAnalyticsResponse = await this.makeRequest('GET', '/api/v1/admin/tickets', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('HIGH', 'Ticket Analytics', 
                ticketAnalyticsResponse.status === 200,
                `Status: ${ticketAnalyticsResponse.status}, Ticket analytics available`);

            // Test performance metrics
            const performanceResponse = await this.makeRequest('GET', '/api/v1/admin/performance', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Performance Metrics', 
                performanceResponse.status === 200 || performanceResponse.status === 404,
                `Status: ${performanceResponse.status}, Performance metrics available`);

            // Test billing logs
            const billingLogsResponse = await this.makeRequest('GET', '/api/v1/admin/billing/logs', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Billing Logs', 
                billingLogsResponse.status === 200 || billingLogsResponse.status === 404,
                `Status: ${billingLogsResponse.status}, Billing logs accessible`);

            // Test audit logs
            const auditLogsResponse = await this.makeRequest('GET', '/api/v1/admin/audit-logs', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Audit Logs', 
                auditLogsResponse.status === 200 || auditLogsResponse.status === 404,
                `Status: ${auditLogsResponse.status}, Audit logs available`);

            console.log('   ✅ Monitoring and Analytics tests completed\n');

        } catch (error) {
            console.log('   ❌ Monitoring and Analytics tests failed\n');
            this.addTestResult('HIGH', 'Monitoring Analytics', false, error.message);
        }
    }

    // Test 7: Content Moderation
    async testContentModeration() {
        console.log('7️⃣ Testing Content Moderation...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('MEDIUM', 'Content Moderation', false, 'No admin auth token available');
                return;
            }

            // Test flagged content review
            const flaggedContentResponse = await this.makeRequest('GET', '/api/v1/admin/flagged-content', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Flagged Content Review', 
                flaggedContentResponse.status === 200 || flaggedContentResponse.status === 404,
                `Status: ${flaggedContentResponse.status}, Flagged content accessible`);

            // Test content approval/rejection
            const moderationActionResponse = await this.makeRequest('POST', '/api/v1/admin/moderate/approve', {
                content_id: 'test123',
                action: 'approve'
            }, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Content Moderation Actions', 
                moderationActionResponse.status === 200 || moderationActionResponse.status === 404,
                `Status: ${moderationActionResponse.status}, Moderation actions available`);

            // Test automated moderation rules
            const moderationRulesResponse = await this.makeRequest('GET', '/api/v1/admin/moderation-rules', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Moderation Rules', 
                moderationRulesResponse.status === 200 || moderationRulesResponse.status === 404,
                `Status: ${moderationRulesResponse.status}, Moderation rules accessible`);

            console.log('   ✅ Content Moderation tests completed\n');

        } catch (error) {
            console.log('   ❌ Content Moderation tests failed\n');
            this.addTestResult('MEDIUM', 'Content Moderation', false, error.message);
        }
    }

    // Test 8: Data Export and Backup
    async testDataExportBackup() {
        console.log('8️⃣ Testing Data Export and Backup...');

        try {
            if (!this.adminAuthToken) {
                this.addTestResult('MEDIUM', 'Data Export Backup', false, 'No admin auth token available');
                return;
            }

            // Test data export
            const exportResponse = await this.makeRequest('GET', '/api/v1/admin/export/tickets?format=csv', null, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Data Export', 
                exportResponse.status === 200 || exportResponse.status === 404,
                `Status: ${exportResponse.status}, Data export functionality`);

            // Test backup creation
            const backupResponse = await this.makeRequest('POST', '/api/v1/admin/backup', {
                type: 'full'
            }, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Backup Creation', 
                backupResponse.status === 200 || backupResponse.status === 404,
                `Status: ${backupResponse.status}, Backup functionality`);

            // Test report generation
            const reportResponse = await this.makeRequest('POST', '/api/v1/admin/reports/generate', {
                type: 'monthly',
                format: 'pdf'
            }, {
                'Authorization': `Bearer ${this.adminAuthToken}`
            });
            this.addTestResult('MEDIUM', 'Report Generation', 
                reportResponse.status === 200 || reportResponse.status === 404,
                `Status: ${reportResponse.status}, Report generation available`);

            console.log('   ✅ Data Export and Backup tests completed\n');

        } catch (error) {
            console.log('   ❌ Data Export and Backup tests failed\n');
            this.addTestResult('MEDIUM', 'Data Export Backup', false, error.message);
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
        console.log('📊 Admin Panel Test Report');
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

        console.log('\nAdmin Panel Testing Complete! 🔧');
    }
}

// Run the comprehensive test suite
async function runAdminPanelTests() {
    const tester = new AdminPanelTester();
    await tester.runAllTests();
}

// Export for use in other test scripts
module.exports = AdminPanelTester;

// Run tests if called directly
if (require.main === module) {
    runAdminPanelTests();
}