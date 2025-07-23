// Comprehensive BOT API Testing Script
// Tests all AI bot functionality according to SRS requirements

const ComplaintBot = require('./backend-nodejs/services/ai-bot');
const MultiChannelService = require('./backend-nodejs/services/multi-channel');

class BotAPITester {
    constructor() {
        this.aiBot = new ComplaintBot();
        this.multiChannel = new MultiChannelService();
        this.testResults = [];
    }

    // Main test runner
    async runAllTests() {
        console.log('🤖 Starting Comprehensive BOT API Testing...\n');

        try {
            // Test 1: Basic AI Bot Functionality
            await this.testBasicAIBot();

            // Test 2: Sentiment Analysis
            await this.testSentimentAnalysis();

            // Test 3: Multi-channel Integration
            await this.testMultiChannelIntegration();

            // Test 4: Conversation Management
            await this.testConversationManagement();

            // Test 5: Voice Processing
            await this.testVoiceProcessing();

            // Test 6: Complaint Creation Flow
            await this.testComplaintCreationFlow();

            // Test 7: Error Handling
            await this.testErrorHandling();

            // Test 8: Performance & Load Testing
            await this.testPerformance();

            // Generate test report
            this.generateTestReport();

        } catch (error) {
            console.error('❌ Test suite failed:', error);
            this.addTestResult('CRITICAL', 'Test Suite Execution', false, error.message);
        }
    }

    // Test 1: Basic AI Bot Functionality
    async testBasicAIBot() {
        console.log('1️⃣ Testing Basic AI Bot Functionality...');

        try {
            // Test greeting response
            const greetingResponse = await this.aiBot.handleMessage('test_user_1', 'Hello', 'web');
            this.addTestResult('HIGH', 'Bot Greeting Response', 
                greetingResponse.text.length > 0, 
                `Response: ${greetingResponse.text}`);

            // Test complaint intent recognition
            const complaintResponse = await this.aiBot.handleMessage('test_user_1', 
                'I want to file a complaint about poor service', 'web');
            this.addTestResult('HIGH', 'Complaint Intent Recognition', 
                complaintResponse.actions.includes('create_complaint') || 
                complaintResponse.text.toLowerCase().includes('complaint'),
                `Actions: ${complaintResponse.actions}, Response: ${complaintResponse.text}`);

            // Test brand identification
            const brandResponse = await this.aiBot.handleMessage('test_user_1', 
                'I have an issue with Apple iPhone', 'web');
            this.addTestResult('HIGH', 'Brand Identification', 
                brandResponse.actions.includes('identify_brand') || 
                brandResponse.text.toLowerCase().includes('brand'),
                `Actions: ${brandResponse.actions}, Response: ${brandResponse.text}`);

            // Test urgency escalation
            const urgentResponse = await this.aiBot.handleMessage('test_user_1', 
                'This is terrible! I am extremely angry and need immediate help!', 'web');
            this.addTestResult('HIGH', 'Urgency Escalation', 
                urgentResponse.priority === 'high' || urgentResponse.actions.includes('escalate_priority'),
                `Priority: ${urgentResponse.priority}, Actions: ${urgentResponse.actions}`);

            console.log('   ✅ Basic AI Bot tests completed\n');

        } catch (error) {
            console.log('   ❌ Basic AI Bot tests failed\n');
            this.addTestResult('HIGH', 'Basic AI Bot Functionality', false, error.message);
        }
    }

    // Test 2: Sentiment Analysis
    async testSentimentAnalysis() {
        console.log('2️⃣ Testing Sentiment Analysis...');

        try {
            // Test positive sentiment
            const positiveSentiment = await this.aiBot.analyzeSentiment('I love this product! It works great!');
            this.addTestResult('MEDIUM', 'Positive Sentiment Detection', 
                positiveSentiment.score > 0,
                `Score: ${positiveSentiment.score}, Magnitude: ${positiveSentiment.magnitude}`);

            // Test negative sentiment
            const negativeSentiment = await this.aiBot.analyzeSentiment('This is absolutely terrible and I hate it!');
            this.addTestResult('MEDIUM', 'Negative Sentiment Detection', 
                negativeSentiment.score < 0,
                `Score: ${negativeSentiment.score}, Magnitude: ${negativeSentiment.magnitude}`);

            // Test neutral sentiment
            const neutralSentiment = await this.aiBot.analyzeSentiment('The weather is okay today.');
            this.addTestResult('MEDIUM', 'Neutral Sentiment Detection', 
                Math.abs(neutralSentiment.score) < 0.3,
                `Score: ${neutralSentiment.score}, Magnitude: ${neutralSentiment.magnitude}`);

            // Test abuse detection
            const abusiveSentiment = await this.aiBot.analyzeSentiment('You idiots are terrible and useless!');
            this.addTestResult('HIGH', 'Abuse Detection', 
                abusiveSentiment.score < -0.5,
                `Score: ${abusiveSentiment.score}, Magnitude: ${abusiveSentiment.magnitude}`);

            console.log('   ✅ Sentiment Analysis tests completed\n');

        } catch (error) {
            console.log('   ❌ Sentiment Analysis tests failed\n');
            this.addTestResult('HIGH', 'Sentiment Analysis', false, error.message);
        }
    }

    // Test 3: Multi-channel Integration
    async testMultiChannelIntegration() {
        console.log('3️⃣ Testing Multi-channel Integration...');

        try {
            // Test web chat
            const webChatResponse = await this.multiChannel.handleWebChatMessage('webchat_user_1', 
                'I need help with my order');
            this.addTestResult('HIGH', 'Web Chat Integration', 
                webChatResponse && webChatResponse.text,
                `Response: ${webChatResponse?.text}`);

            // Test WhatsApp (mock)
            const whatsAppResponse = await this.multiChannel.handleWhatsAppMessage('+1234567890', 
                'Hello, I have a complaint');
            this.addTestResult('HIGH', 'WhatsApp Integration', 
                whatsAppResponse && whatsAppResponse.text,
                `Response: ${whatsAppResponse?.text}`);

            // Test channel status
            const channelStatus = this.multiChannel.getChannelStatus();
            this.addTestResult('MEDIUM', 'Channel Status Check', 
                channelStatus.webchat !== undefined && channelStatus.whatsapp !== undefined,
                `Status: ${JSON.stringify(channelStatus)}`);

            // Test voice call handling
            const voiceResponse = await this.multiChannel.handleVoiceCall('+1234567890', '+0987654321');
            this.addTestResult('HIGH', 'Voice Call Handling', 
                voiceResponse && voiceResponse.includes('Welcome'),
                `TwiML Response generated: ${voiceResponse ? 'Yes' : 'No'}`);

            console.log('   ✅ Multi-channel Integration tests completed\n');

        } catch (error) {
            console.log('   ❌ Multi-channel Integration tests failed\n');
            this.addTestResult('HIGH', 'Multi-channel Integration', false, error.message);
        }
    }

    // Test 4: Conversation Management
    async testConversationManagement() {
        console.log('4️⃣ Testing Conversation Management...');

        try {
            const userId = 'conversation_test_user';

            // Test conversation initiation
            await this.aiBot.handleMessage(userId, 'Hello, I need help', 'web');
            let history = this.aiBot.getConversationHistory(userId);
            this.addTestResult('MEDIUM', 'Conversation Initiation', 
                history.messages.length > 0,
                `Messages count: ${history.messages.length}`);

            // Test conversation continuity
            await this.aiBot.handleMessage(userId, 'I want to complain about a product', 'web');
            await this.aiBot.handleMessage(userId, 'The product is from Apple', 'web');
            history = this.aiBot.getConversationHistory(userId);
            this.addTestResult('MEDIUM', 'Conversation Continuity', 
                history.messages.length >= 6, // 3 user + 3 bot messages
                `Messages count: ${history.messages.length}`);

            // Test context update
            this.aiBot.updateContext(userId, { brandId: 'apple', priority: 'high' });
            history = this.aiBot.getConversationHistory(userId);
            this.addTestResult('MEDIUM', 'Context Management', 
                history.context.brandId === 'apple' && history.context.priority === 'high',
                `Context: ${JSON.stringify(history.context)}`);

            // Test conversation clearing
            this.aiBot.clearConversation(userId);
            history = this.aiBot.getConversationHistory(userId);
            this.addTestResult('MEDIUM', 'Conversation Clearing', 
                history.messages.length === 0,
                `Messages count after clear: ${history.messages.length}`);

            console.log('   ✅ Conversation Management tests completed\n');

        } catch (error) {
            console.log('   ❌ Conversation Management tests failed\n');
            this.addTestResult('MEDIUM', 'Conversation Management', false, error.message);
        }
    }

    // Test 5: Voice Processing
    async testVoiceProcessing() {
        console.log('5️⃣ Testing Voice Processing...');

        try {
            // Test TTS capability
            const ttsAudio = await this.aiBot.textToSpeech('Hello, this is a test message');
            this.addTestResult('MEDIUM', 'Text-to-Speech', 
                ttsAudio !== null || this.aiBot.ttsClient === null,
                `TTS available: ${this.aiBot.ttsClient !== null ? 'Yes' : 'No (fallback)'}`);

            // Test STT capability (would need actual audio buffer)
            const sttResult = await this.aiBot.speechToText(Buffer.from('mock audio data'));
            this.addTestResult('MEDIUM', 'Speech-to-Text', 
                sttResult !== null || this.aiBot.deepgram === null,
                `STT available: ${this.aiBot.deepgram !== null ? 'Yes' : 'No (fallback)'}`);

            // Test voice processing pipeline
            const voiceProcessResult = await this.multiChannel.processVoiceInput(
                'https://example.com/audio.wav', 'voice_test_user');
            this.addTestResult('MEDIUM', 'Voice Processing Pipeline', 
                voiceProcessResult !== null,
                `Voice processing result: ${typeof voiceProcessResult}`);

            console.log('   ✅ Voice Processing tests completed\n');

        } catch (error) {
            console.log('   ❌ Voice Processing tests failed\n');
            this.addTestResult('MEDIUM', 'Voice Processing', false, error.message);
        }
    }

    // Test 6: Complaint Creation Flow
    async testComplaintCreationFlow() {
        console.log('6️⃣ Testing Complaint Creation Flow...');

        try {
            const userId = 'complaint_flow_user';

            // Simulate complete complaint flow
            await this.aiBot.handleMessage(userId, 'I want to file a complaint', 'web');
            await this.aiBot.handleMessage(userId, 'I have an issue with Samsung Galaxy phone', 'web');
            await this.aiBot.handleMessage(userId, 'The battery life is terrible and it keeps crashing', 'web');

            // Test complaint data extraction
            const conversation = this.aiBot.getConversationHistory(userId);
            const complaintData = this.multiChannel.extractComplaintData(conversation);
            this.addTestResult('HIGH', 'Complaint Data Extraction', 
                complaintData.brand !== null && complaintData.description !== null,
                `Brand: ${complaintData.brand}, Description: ${complaintData.description ? 'Present' : 'Missing'}`);

            // Test brand name extraction
            const brandName = this.multiChannel.extractBrandName('I have a problem with Apple iPhone');
            this.addTestResult('MEDIUM', 'Brand Name Extraction', 
                brandName === 'Apple' || brandName === 'iPhone',
                `Extracted brand: ${brandName}`);

            // Test ticket creation
            const ticket = await this.multiChannel.createTicket({
                brand: 'TestBrand',
                description: 'Test complaint description'
            }, userId, 'web');
            this.addTestResult('HIGH', 'Ticket Creation', 
                ticket && ticket.id && ticket.title,
                `Ticket ID: ${ticket?.id}, Title: ${ticket?.title}`);

            console.log('   ✅ Complaint Creation Flow tests completed\n');

        } catch (error) {
            console.log('   ❌ Complaint Creation Flow tests failed\n');
            this.addTestResult('HIGH', 'Complaint Creation Flow', false, error.message);
        }
    }

    // Test 7: Error Handling
    async testErrorHandling() {
        console.log('7️⃣ Testing Error Handling...');

        try {
            // Test invalid user input
            const invalidResponse = await this.aiBot.handleMessage('error_test_user', '', 'web');
            this.addTestResult('MEDIUM', 'Empty Message Handling', 
                invalidResponse.text && invalidResponse.text.length > 0,
                `Response to empty message: ${invalidResponse.text}`);

            // Test service failures (when APIs are not available)
            const fallbackResponse = this.aiBot.generateFallbackResponse(
                'I have a complaint', { score: -0.5, magnitude: 0.8 }, { messages: [] });
            this.addTestResult('HIGH', 'Fallback Response System', 
                fallbackResponse.text && fallbackResponse.actions,
                `Fallback response generated: ${fallbackResponse.text ? 'Yes' : 'No'}`);

            // Test malformed audio processing
            const badAudioResult = await this.multiChannel.downloadAudio('invalid-url');
            this.addTestResult('MEDIUM', 'Invalid Audio URL Handling', 
                badAudioResult === null,
                `Bad audio handled gracefully: ${badAudioResult === null ? 'Yes' : 'No'}`);

            console.log('   ✅ Error Handling tests completed\n');

        } catch (error) {
            console.log('   ❌ Error Handling tests failed\n');
            this.addTestResult('MEDIUM', 'Error Handling', false, error.message);
        }
    }

    // Test 8: Performance & Load Testing
    async testPerformance() {
        console.log('8️⃣ Testing Performance & Load...');

        try {
            // Test response time
            const startTime = Date.now();
            await this.aiBot.handleMessage('perf_test_user', 'Hello, I need help with my order', 'web');
            const responseTime = Date.now() - startTime;
            
            this.addTestResult('HIGH', 'Response Time Performance', 
                responseTime < 5000, // Should respond within 5 seconds
                `Response time: ${responseTime}ms`);

            // Test concurrent users
            const concurrentPromises = [];
            for (let i = 0; i < 10; i++) {
                concurrentPromises.push(
                    this.aiBot.handleMessage(`concurrent_user_${i}`, 
                        `Test message ${i}`, 'web')
                );
            }

            const concurrentStartTime = Date.now();
            const concurrentResults = await Promise.all(concurrentPromises);
            const concurrentTime = Date.now() - concurrentStartTime;

            this.addTestResult('MEDIUM', 'Concurrent User Handling', 
                concurrentResults.length === 10 && concurrentTime < 10000,
                `10 concurrent users handled in ${concurrentTime}ms`);

            // Test memory usage
            const memUsage = process.memoryUsage();
            this.addTestResult('MEDIUM', 'Memory Usage', 
                memUsage.heapUsed < 100 * 1024 * 1024, // Less than 100MB
                `Heap used: ${Math.round(memUsage.heapUsed / 1024 / 1024)}MB`);

            console.log('   ✅ Performance & Load tests completed\n');

        } catch (error) {
            console.log('   ❌ Performance & Load tests failed\n');
            this.addTestResult('HIGH', 'Performance & Load Testing', false, error.message);
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
        console.log('📊 BOT API Test Report');
        console.log('========================\n');

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

        console.log('\nBOT API Testing Complete! 🤖');
    }
}

// Run the comprehensive test suite
async function runBotAPITests() {
    const tester = new BotAPITester();
    await tester.runAllTests();
}

// Export for use in other test scripts
module.exports = BotAPITester;

// Run tests if called directly
if (require.main === module) {
    runBotAPITests();
}