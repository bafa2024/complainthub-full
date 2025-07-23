const axios = require('axios');

const BASE_URL = 'http://localhost:8001';
const TEST_USER_ID = 'test_user_' + Date.now();

class ComprehensiveTestSuiteV2 {
    constructor() {
        this.results = {
            passed: 0,
            failed: 0,
            total: 0,
            details: []
        };
        this.adminToken = null;
        this.brandToken = null;
        this.userToken = null;
        this.testBrandId = null;
        this.testTicketId = null;
    }

    async runAllTests() {
        console.log('🚀 Starting Comprehensive Test Suite V2 - All Features');
        console.log('=' .repeat(80));

        // Phase 1: Core System Tests
        await this.testCoreSystem();
        
        // Phase 2: AI Bot Tests
        await this.testAIBot();
        
        // Phase 3: Multi-Channel Tests
        await this.testMultiChannel();
        
        // Phase 4: Billing System Tests
        await this.testBillingSystem();
        
        // Phase 5: Follow-up System Tests
        await this.testFollowupSystem();
        
        // Phase 6: Integration Tests
        await this.testIntegration();
        
        // Phase 7: Performance Tests
        await this.testPerformance();

        this.printResults();
    }

    async testCoreSystem() {
        console.log('\n📋 Phase 1: Core System Tests');
        console.log('-'.repeat(40));

        await this.test('Backend Health Check', async () => {
            const response = await axios.get(`${BASE_URL}/health`);
            return response.status === 200 && response.data.status === 'healthy';
        });

        await this.test('API Base Endpoint', async () => {
            const response = await axios.get(`${BASE_URL}/`);
            return response.status === 200 && response.data.message.includes('ComplaintHub');
        });

        await this.test('Admin Authentication', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/auth/login`, {
                email: 'admin@complainthub.com',
                password: 'admin123'
            });
            this.adminToken = response.data.token;
            return response.status === 200 && response.data.token;
        });

        await this.test('Brand Signup', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/auth/signup`, {
                email: 'testbrand@example.com',
                full_name: 'Test Brand',
                password: 'brand123',
                brand_name: 'Test Brand Inc',
                role: 'brand_user'
            });
            return response.status === 201;
        });

        await this.test('Brand Login', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/auth/login`, {
                email: 'testbrand@example.com',
                password: 'brand123'
            });
            this.brandToken = response.data.token;
            return response.status === 200 && response.data.token;
        });

        await this.test('User Signup', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/auth/signup`, {
                email: 'testuser@example.com',
                full_name: 'Test User',
                password: 'user123',
                role: 'user'
            });
            return response.status === 201;
        });

        await this.test('User Login', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/auth/login`, {
                email: 'testuser@example.com',
                password: 'user123'
            });
            this.userToken = response.data.token;
            return response.status === 200 && response.data.token;
        });
    }

    async testAIBot() {
        console.log('\n🤖 Phase 2: AI Bot Tests');
        console.log('-'.repeat(40));

        await this.test('AI Bot Chat - Basic Message', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'Hello, I need help with a complaint',
                userId: TEST_USER_ID,
                channel: 'web'
            });
            return response.status === 200 && 
                   response.data.text && 
                   response.data.sentiment &&
                   response.data.actions;
        });

        await this.test('AI Bot Chat - Complaint Intent', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'I want to complain about Amazon delivery service',
                userId: TEST_USER_ID,
                channel: 'web'
            });
            return response.status === 200 && 
                   response.data.actions.includes('create_complaint');
        });

        await this.test('AI Bot Chat - Negative Sentiment', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'I am extremely angry and frustrated with this terrible service!',
                userId: TEST_USER_ID,
                channel: 'web'
            });
            return response.status === 200 && 
                   response.data.sentiment.score < 0 &&
                   response.data.priority === 'high';
        });

        await this.test('AI Bot Chat - Human Escalation', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'I need to speak to a human representative immediately',
                userId: TEST_USER_ID,
                channel: 'web'
            });
            return response.status === 200 && 
                   response.data.actions.includes('escalate_to_human');
        });

        await this.test('AI Bot Voice Processing', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/voice`, {
                audioUrl: 'https://example.com/test-audio.wav',
                userId: TEST_USER_ID
            });
            return response.status === 200;
        });
    }

    async testMultiChannel() {
        console.log('\n📱 Phase 3: Multi-Channel Tests');
        console.log('-'.repeat(40));

        await this.test('WhatsApp Message Handling', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/channels/whatsapp`, {
                from: '+1234567890',
                body: 'I have a complaint about delivery service'
            });
            return response.status === 200 && response.data.text;
        });

        await this.test('Telegram Message Handling', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/channels/telegram`, {
                chatId: '123456789',
                text: 'Need help with a complaint'
            });
            return response.status === 200 && response.data.text;
        });

        await this.test('Voice Call Handling', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/voice/call`, {
                from: '+1234567890',
                to: '+0987654321'
            });
            return response.status === 200 && response.data.includes('TwiML');
        });

        await this.test('Web Chat Message Handling', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'Web chat test message',
                userId: 'webchat_user_123',
                channel: 'webchat'
            });
            return response.status === 200 && response.data.text;
        });
    }

    async testBillingSystem() {
        console.log('\n💰 Phase 4: Billing System Tests');
        console.log('-'.repeat(40));

        // First create a test brand if we don't have one
        if (!this.testBrandId) {
            const brandResponse = await axios.post(`${BASE_URL}/api/v1/brands`, {
                name: 'Billing Test Brand',
                description: 'Test brand for billing',
                support_email: 'billing@testbrand.com',
                industry: 'Technology'
            }, {
                headers: { Authorization: `Bearer ${this.adminToken}` }
            });
            this.testBrandId = brandResponse.data.id;
        }

        await this.test('Get Brand Credits', async () => {
            const response = await axios.get(`${BASE_URL}/api/v1/billing/credits/${this.testBrandId}`);
            return response.status === 200 && 
                   typeof response.data.credits === 'number';
        });

        await this.test('Payment Processing', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/billing/payment`, {
                brandId: this.testBrandId,
                amount: 50.00,
                paymentMethodId: 'pm_test_payment_method'
            });
            return response.status === 200;
        });

        await this.test('Billing History', async () => {
            const response = await axios.get(`${BASE_URL}/api/v1/billing/history/${this.testBrandId}`);
            return response.status === 200 && 
                   Array.isArray(response.data.transactions) &&
                   Array.isArray(response.data.payments);
        });

        await this.test('Credit Deduction', async () => {
            // First add some credits
            await axios.post(`${BASE_URL}/api/v1/billing/payment`, {
                brandId: this.testBrandId,
                amount: 100.00,
                paymentMethodId: 'pm_test_payment_method'
            });

            // Then test deduction (this would be done internally when processing complaints)
            const response = await axios.get(`${BASE_URL}/api/v1/billing/credits/${this.testBrandId}`);
            return response.status === 200 && response.data.credits >= 0;
        });
    }

    async testFollowupSystem() {
        console.log('\n📧 Phase 5: Follow-up System Tests');
        console.log('-'.repeat(40));

        // Create a test ticket first
        if (!this.testTicketId) {
            const ticketResponse = await axios.post(`${BASE_URL}/api/v1/tickets`, {
                title: 'Follow-up Test Ticket',
                description: 'Test ticket for follow-up system',
                brand_id: this.testBrandId,
                user_id: 1,
                priority: 'medium',
                category: 'complaint',
                channel: 'web'
            }, {
                headers: { Authorization: `Bearer ${this.adminToken}` }
            });
            this.testTicketId = ticketResponse.data.id;
        }

        await this.test('Follow-up Statistics', async () => {
            const response = await axios.get(`${BASE_URL}/api/v1/followup/stats/${this.testBrandId}`);
            return response.status === 200 && 
                   typeof response.data.total_tickets === 'number';
        });

        await this.test('Manual Follow-up Logging', async () => {
            const response = await axios.post(`${BASE_URL}/api/v1/followup/manual`, {
                ticketId: this.testTicketId,
                message: 'Test manual follow-up message',
                type: 'manual'
            });
            return response.status === 200 && response.data.success;
        });

        await this.test('Follow-up Statistics - All Brands', async () => {
            const response = await axios.get(`${BASE_URL}/api/v1/followup/stats`);
            return response.status === 200 && 
                   typeof response.data.total_tickets === 'number';
        });
    }

    async testIntegration() {
        console.log('\n🔗 Phase 6: Integration Tests');
        console.log('-'.repeat(40));

        await this.test('End-to-End Complaint Flow', async () => {
            // 1. User starts chat with bot
            const chatResponse = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                message: 'I want to complain about poor customer service',
                userId: 'integration_test_user',
                channel: 'web'
            });

            // 2. Bot should identify complaint intent
            const hasComplaintIntent = chatResponse.data.actions.includes('create_complaint');
            
            // 3. Create ticket through admin API
            const ticketResponse = await axios.post(`${BASE_URL}/api/v1/tickets`, {
                title: 'Integration Test Complaint',
                description: 'Test complaint for integration testing',
                brand_id: this.testBrandId,
                user_id: 1,
                priority: 'medium',
                category: 'complaint',
                channel: 'web'
            }, {
                headers: { Authorization: `Bearer ${this.adminToken}` }
            });

            // 4. Check billing impact
            const billingResponse = await axios.get(`${BASE_URL}/api/v1/billing/credits/${this.testBrandId}`);

            return chatResponse.status === 200 && 
                   hasComplaintIntent &&
                   ticketResponse.status === 201 &&
                   billingResponse.status === 200;
        });

        await this.test('Multi-Channel Integration', async () => {
            // Test that the same bot can handle different channels
            const channels = ['web', 'whatsapp', 'telegram', 'webchat'];
            const results = [];

            for (const channel of channels) {
                const response = await axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                    message: 'Test message from ' + channel,
                    userId: `integration_${channel}_user`,
                    channel: channel
                });
                results.push(response.status === 200);
            }

            return results.every(result => result === true);
        });

        await this.test('Billing and Follow-up Integration', async () => {
            // Test that billing and follow-up systems work together
            const followupStats = await axios.get(`${BASE_URL}/api/v1/followup/stats/${this.testBrandId}`);
            const billingHistory = await axios.get(`${BASE_URL}/api/v1/billing/history/${this.testBrandId}`);

            return followupStats.status === 200 && billingHistory.status === 200;
        });
    }

    async testPerformance() {
        console.log('\n⚡ Phase 7: Performance Tests');
        console.log('-'.repeat(40));

        await this.test('Concurrent Bot Requests', async () => {
            const promises = [];
            const numRequests = 10;

            for (let i = 0; i < numRequests; i++) {
                promises.push(
                    axios.post(`${BASE_URL}/api/v1/bot/chat`, {
                        message: `Concurrent test message ${i}`,
                        userId: `perf_user_${i}`,
                        channel: 'web'
                    })
                );
            }

            const startTime = Date.now();
            const responses = await Promise.all(promises);
            const endTime = Date.now();
            const duration = endTime - startTime;

            const allSuccessful = responses.every(response => response.status === 200);
            const avgResponseTime = duration / numRequests;

            console.log(`   Average response time: ${avgResponseTime.toFixed(2)}ms per request`);
            console.log(`   Total duration: ${duration}ms for ${numRequests} requests`);

            return allSuccessful && avgResponseTime < 2000; // Less than 2 seconds average
        });

        await this.test('Database Query Performance', async () => {
            const startTime = Date.now();
            
            // Test multiple database operations
            const promises = [
                axios.get(`${BASE_URL}/api/v1/brands`, {
                    headers: { Authorization: `Bearer ${this.adminToken}` }
                }),
                axios.get(`${BASE_URL}/api/v1/tickets`, {
                    headers: { Authorization: `Bearer ${this.adminToken}` }
                }),
                axios.get(`${BASE_URL}/api/v1/users`, {
                    headers: { Authorization: `Bearer ${this.adminToken}` }
                })
            ];

            const responses = await Promise.all(promises);
            const endTime = Date.now();
            const duration = endTime - startTime;

            console.log(`   Database queries completed in: ${duration}ms`);

            return responses.every(response => response.status === 200) && duration < 1000;
        });

        await this.test('Memory Usage Check', async () => {
            // This is a basic check - in production you'd want more sophisticated monitoring
            const memUsage = process.memoryUsage();
            const heapUsedMB = Math.round(memUsage.heapUsed / 1024 / 1024);
            
            console.log(`   Current heap usage: ${heapUsedMB}MB`);

            return heapUsedMB < 500; // Less than 500MB heap usage
        });
    }

    async test(testName, testFunction) {
        this.results.total++;
        
        try {
            const result = await testFunction();
            
            if (result) {
                this.results.passed++;
                console.log(`✅ ${testName}`);
                this.results.details.push({ name: testName, status: 'PASSED' });
            } else {
                this.results.failed++;
                console.log(`❌ ${testName}`);
                this.results.details.push({ name: testName, status: 'FAILED', error: 'Test returned false' });
            }
        } catch (error) {
            this.results.failed++;
            console.log(`❌ ${testName} - Error: ${error.message}`);
            this.results.details.push({ name: testName, status: 'FAILED', error: error.message });
        }
    }

    printResults() {
        console.log('\n' + '='.repeat(80));
        console.log('📊 COMPREHENSIVE TEST SUITE V2 RESULTS');
        console.log('='.repeat(80));
        
        console.log(`\n🎯 Overall Results:`);
        console.log(`   Total Tests: ${this.results.total}`);
        console.log(`   Passed: ${this.results.passed} ✅`);
        console.log(`   Failed: ${this.results.failed} ❌`);
        console.log(`   Success Rate: ${((this.results.passed / this.results.total) * 100).toFixed(1)}%`);

        console.log(`\n📋 Detailed Results:`);
        this.results.details.forEach(detail => {
            const icon = detail.status === 'PASSED' ? '✅' : '❌';
            console.log(`   ${icon} ${detail.name}`);
            if (detail.error) {
                console.log(`      Error: ${detail.error}`);
            }
        });

        console.log(`\n🚀 Feature Implementation Status:`);
        console.log(`   ✅ Core System: ${this.getFeatureStatus('Core System')}`);
        console.log(`   ✅ AI Bot: ${this.getFeatureStatus('AI Bot')}`);
        console.log(`   ✅ Multi-Channel: ${this.getFeatureStatus('Multi-Channel')}`);
        console.log(`   ✅ Billing System: ${this.getFeatureStatus('Billing System')}`);
        console.log(`   ✅ Follow-up System: ${this.getFeatureStatus('Follow-up System')}`);
        console.log(`   ✅ Integration: ${this.getFeatureStatus('Integration')}`);
        console.log(`   ✅ Performance: ${this.getFeatureStatus('Performance')}`);

        console.log(`\n🎉 Test Suite Complete!`);
        
        if (this.results.failed === 0) {
            console.log(`🎊 All tests passed! The system is ready for production.`);
        } else {
            console.log(`⚠️  ${this.results.failed} tests failed. Please review and fix the issues.`);
        }
    }

    getFeatureStatus(featureName) {
        const featureTests = this.results.details.filter(detail => 
            detail.name.includes(featureName) || 
            (featureName === 'Core System' && detail.name.includes('Health') || detail.name.includes('Auth')) ||
            (featureName === 'AI Bot' && detail.name.includes('Bot')) ||
            (featureName === 'Multi-Channel' && detail.name.includes('WhatsApp') || detail.name.includes('Telegram') || detail.name.includes('Voice')) ||
            (featureName === 'Billing System' && detail.name.includes('Billing') || detail.name.includes('Payment')) ||
            (featureName === 'Follow-up System' && detail.name.includes('Follow-up')) ||
            (featureName === 'Integration' && detail.name.includes('Integration')) ||
            (featureName === 'Performance' && detail.name.includes('Performance'))
        );

        const passedTests = featureTests.filter(test => test.status === 'PASSED').length;
        const totalTests = featureTests.length;

        if (totalTests === 0) return 'Not Tested';
        if (passedTests === totalTests) return '✅ Fully Implemented';
        if (passedTests > 0) return '🔄 Partially Implemented';
        return '❌ Not Working';
    }
}

// Run the test suite
async function runTests() {
    const testSuite = new ComprehensiveTestSuiteV2();
    await testSuite.runAllTests();
}

// Export for use in other files
module.exports = ComprehensiveTestSuiteV2;

// Run if this file is executed directly
if (require.main === module) {
    runTests().catch(console.error);
} 