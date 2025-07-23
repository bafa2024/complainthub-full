const OpenAI = require('openai');
const { LanguageServiceClient } = require('@google-cloud/language');
const { TextToSpeechClient } = require('@google-cloud/text-to-speech');
const { Deepgram } = require('@deepgram/sdk');

class ComplaintBot {
    constructor() {
        // Initialize OpenAI (with error handling for missing API key)
        try {
            this.openai = new OpenAI({
                apiKey: process.env.OPENAI_API_KEY || 'your-openai-key'
            });
        } catch (error) {
            console.warn('OpenAI initialization failed:', error.message);
            this.openai = null;
        }

        // Initialize Google Cloud services (with error handling for missing credentials)
        try {
            // Only initialize if credentials are available
            if (process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_CLOUD_PROJECT) {
                this.languageClient = new LanguageServiceClient();
                this.ttsClient = new TextToSpeechClient();
            } else {
                console.warn('Google Cloud credentials not configured, using fallback');
                this.languageClient = null;
                this.ttsClient = null;
            }
        } catch (error) {
            console.warn('Google Cloud services initialization failed:', error.message);
            this.languageClient = null;
            this.ttsClient = null;
        }

        // Initialize Deepgram for voice processing (with error handling for version compatibility)
        try {
            this.deepgram = new Deepgram(process.env.DEEPGRAM_API_KEY || 'your-deepgram-key');
        } catch (error) {
            console.warn('Deepgram initialization failed:', error.message);
            this.deepgram = null;
        }

        // Conversation context storage
        this.conversations = new Map();
        
        // Bot personality and responses
        this.botPersonality = {
            name: "ComplaintHub Assistant",
            role: "I am an AI assistant designed to help users lodge complaints and get support. I'm empathetic, professional, and efficient.",
            capabilities: [
                "Help users lodge complaints",
                "Provide status updates on existing complaints", 
                "Answer questions about the complaint process",
                "Connect users to human support when needed",
                "Analyze sentiment and prioritize urgent issues"
            ]
        };
    }

    // Main conversation handler
    async handleMessage(userId, message, channel = 'web') {
        try {
            // Get or create conversation context
            let conversation = this.conversations.get(userId) || {
                messages: [],
                context: {
                    userType: 'unknown',
                    currentComplaint: null,
                    brandId: null,
                    priority: 'medium'
                }
            };

            // Add user message to conversation
            conversation.messages.push({
                role: 'user',
                content: message,
                timestamp: new Date(),
                channel: channel
            });

            // Analyze sentiment
            const sentiment = await this.analyzeSentiment(message);
            
            // Update context based on sentiment
            if (sentiment.score < -0.5) {
                conversation.context.priority = 'high';
            }

            // Generate AI response
            const response = await this.generateResponse(conversation, message, sentiment);
            
            // Add bot response to conversation
            conversation.messages.push({
                role: 'assistant',
                content: response.text,
                timestamp: new Date(),
                channel: channel
            });

            // Update conversation storage
            this.conversations.set(userId, conversation);

            return {
                text: response.text,
                sentiment: sentiment,
                priority: conversation.context.priority,
                actions: response.actions,
                confidence: response.confidence
            };

        } catch (error) {
            console.error('Bot error:', error);
            return {
                text: "I apologize, but I'm experiencing technical difficulties. Please try again or contact human support.",
                sentiment: { score: 0, magnitude: 0 },
                priority: 'medium',
                actions: ['escalate_to_human'],
                confidence: 0
            };
        }
    }

    // Generate AI response using OpenAI
    async generateResponse(conversation, message, sentiment) {
        try {
            if (!this.openai) {
                console.warn('OpenAI not available, using fallback response');
                return this.generateFallbackResponse(message, sentiment, conversation);
            }

            // Build conversation history for context
            const conversationHistory = conversation.messages
                .slice(-10) // Last 10 messages for context
                .map(msg => `${msg.role}: ${msg.content}`)
                .join('\n');

            // Create system prompt
            const systemPrompt = `You are ${this.botPersonality.name}. ${this.botPersonality.role}

Your capabilities:
${this.botPersonality.capabilities.map(cap => `- ${cap}`).join('\n')}

Current conversation context:
- User sentiment: ${sentiment.score > 0 ? 'Positive' : sentiment.score < 0 ? 'Negative' : 'Neutral'}
- Priority level: ${conversation.context.priority}
- Channel: ${conversation.messages[conversation.messages.length - 1]?.channel || 'web'}

Guidelines:
1. Be empathetic and professional
2. If user wants to lodge a complaint, ask for brand name and complaint details
3. If user is frustrated, acknowledge their feelings and offer immediate help
4. If complaint seems urgent (negative sentiment), prioritize it
5. Keep responses concise but helpful
6. If you can't help, offer to connect to human support

Respond naturally and conversationally.`;

            const completion = await this.openai.chat.completions.create({
                model: "gpt-3.5-turbo",
                messages: [
                    { role: "system", content: systemPrompt },
                    { role: "user", content: `Conversation history:\n${conversationHistory}\n\nUser message: ${message}` }
                ],
                max_tokens: 300,
                temperature: 0.7
            });

            const responseText = completion.choices[0].message.content;

            // Determine actions based on response
            const actions = this.determineActions(responseText, sentiment, conversation);

            return {
                text: responseText,
                actions: actions,
                confidence: 0.9
            };

        } catch (error) {
            console.error('OpenAI error:', error);
            return this.generateFallbackResponse(message, sentiment, conversation);
        }
    }

    // Generate fallback response when OpenAI is not available
    generateFallbackResponse(message, sentiment, conversation) {
        const lowerMessage = message.toLowerCase();
        let responseText = '';
        let actions = [];

        if (lowerMessage.includes('complaint') || lowerMessage.includes('issue') || lowerMessage.includes('problem')) {
            responseText = "I understand you have a complaint. Could you please tell me which brand or company you'd like to complain about?";
            actions = ['ask_for_brand'];
        } else if (lowerMessage.includes('brand') || lowerMessage.includes('company')) {
            responseText = "Thank you for providing the brand name. Now, could you please describe your complaint in detail?";
            actions = ['create_complaint'];
        } else if (sentiment.score < -0.3) {
            responseText = "I can see you're frustrated, and I want to help resolve this issue quickly. Please tell me more about what happened.";
            actions = ['escalate_priority'];
        } else if (lowerMessage.includes('human') || lowerMessage.includes('agent') || lowerMessage.includes('representative')) {
            responseText = "I understand you'd like to speak with a human representative. I'll connect you to one of our support agents right away.";
            actions = ['escalate_to_human'];
        } else {
            responseText = "Hello! I'm here to help you with complaints and support issues. How can I assist you today?";
            actions = [];
        }

        return {
            text: responseText,
            actions: actions,
            confidence: 0.7
        };
    }

    // Analyze sentiment using Google Cloud Natural Language
    async analyzeSentiment(text) {
        try {
            if (!this.languageClient) {
                console.warn('Google Cloud Language not available for sentiment analysis');
                // Simple fallback sentiment analysis
                const negativeWords = ['bad', 'terrible', 'awful', 'horrible', 'angry', 'frustrated', 'upset', 'disappointed'];
                const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy', 'satisfied', 'pleased'];
                
                const lowerText = text.toLowerCase();
                let score = 0;
                
                negativeWords.forEach(word => {
                    if (lowerText.includes(word)) score -= 0.3;
                });
                
                positiveWords.forEach(word => {
                    if (lowerText.includes(word)) score += 0.3;
                });
                
                return {
                    score: Math.max(-1, Math.min(1, score)),
                    magnitude: Math.abs(score),
                    language: 'en'
                };
            }

            const document = {
                content: text,
                type: 'PLAIN_TEXT',
            };

            const [result] = await this.languageClient.analyzeSentiment({ document });
            const sentiment = result.documentSentiment;

            return {
                score: sentiment.score,
                magnitude: sentiment.magnitude,
                language: result.language
            };
        } catch (error) {
            console.error('Sentiment analysis error:', error);
            return {
                score: 0,
                magnitude: 0,
                language: 'en'
            };
        }
    }

    // Convert text to speech
    async textToSpeech(text, voice = 'en-US-Standard-A') {
        try {
            if (!this.ttsClient) {
                console.warn('Google Cloud TTS not available for text-to-speech');
                return null;
            }

            const request = {
                input: { text: text },
                voice: { languageCode: 'en-US', name: voice },
                audioConfig: { audioEncoding: 'MP3' },
            };

            const [response] = await this.ttsClient.synthesizeSpeech(request);
            return response.audioContent;
        } catch (error) {
            console.error('TTS error:', error);
            return null;
        }
    }

    // Convert speech to text using Deepgram
    async speechToText(audioBuffer) {
        try {
            if (!this.deepgram) {
                console.warn('Deepgram not available for speech-to-text');
                return null;
            }

            const response = await this.deepgram.transcription.preRecorded(
                { buffer: audioBuffer, mimetype: 'audio/wav' },
                {
                    smart_format: true,
                    model: 'nova',
                    language: 'en-US'
                }
            );

            return response.results.channels[0].alternatives[0].transcript;
        } catch (error) {
            console.error('STT error:', error);
            return null;
        }
    }

    // Determine actions based on response and context
    determineActions(responseText, sentiment, conversation) {
        const actions = [];

        // Check for complaint intent
        if (responseText.toLowerCase().includes('complaint') || 
            responseText.toLowerCase().includes('issue') ||
            responseText.toLowerCase().includes('problem')) {
            actions.push('create_complaint');
        }

        // Check for brand mention
        if (responseText.toLowerCase().includes('brand') || 
            responseText.toLowerCase().includes('company')) {
            actions.push('identify_brand');
        }

        // Check for urgent sentiment
        if (sentiment.score < -0.5) {
            actions.push('escalate_priority');
        }

        // Check for human support request
        if (responseText.toLowerCase().includes('human') || 
            responseText.toLowerCase().includes('agent') ||
            responseText.toLowerCase().includes('representative')) {
            actions.push('escalate_to_human');
        }

        return actions;
    }

    // Get conversation history
    getConversationHistory(userId) {
        return this.conversations.get(userId) || { messages: [], context: {} };
    }

    // Clear conversation history
    clearConversation(userId) {
        this.conversations.delete(userId);
    }

    // Update conversation context
    updateContext(userId, context) {
        const conversation = this.conversations.get(userId);
        if (conversation) {
            conversation.context = { ...conversation.context, ...context };
            this.conversations.set(userId, conversation);
        }
    }
}

module.exports = ComplaintBot; 