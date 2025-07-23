const twilio = require('twilio');
const TelegramBot = require('node-telegram-bot-api');
const ComplaintBot = require('./ai-bot');

class MultiChannelService {
    constructor() {
        // Initialize Twilio for voice calls and WhatsApp (with error handling)
        try {
            this.twilioClient = twilio(
                process.env.TWILIO_ACCOUNT_SID || 'your-twilio-sid',
                process.env.TWILIO_AUTH_TOKEN || 'your-twilio-token'
            );
        } catch (error) {
            console.warn('Twilio initialization failed:', error.message);
            this.twilioClient = null;
        }

        // Initialize Telegram Bot (with error handling)
        try {
            const telegramToken = process.env.TELEGRAM_BOT_TOKEN;
            if (telegramToken && telegramToken !== 'your-telegram-token') {
                this.telegramBot = new TelegramBot(telegramToken, { polling: true });
            } else {
                console.warn('Telegram bot token not configured, skipping initialization');
                this.telegramBot = null;
            }
        } catch (error) {
            console.warn('Telegram bot initialization failed:', error.message);
            this.telegramBot = null;
        }

        // Initialize AI Bot
        this.aiBot = new ComplaintBot();

        // Channel configurations
        this.channels = {
            whatsapp: {
                enabled: true,
                webhookUrl: process.env.WHATSAPP_WEBHOOK_URL,
                accessToken: process.env.WHATSAPP_ACCESS_TOKEN
            },
            telegram: {
                enabled: true,
                botUsername: process.env.TELEGRAM_BOT_USERNAME
            },
            voice: {
                enabled: true,
                phoneNumber: process.env.TWILIO_PHONE_NUMBER
            },
            webchat: {
                enabled: true
            }
        };

        this.setupTelegramBot();
    }

    // Setup Telegram Bot handlers
    setupTelegramBot() {
        if (!this.telegramBot) {
            console.warn('Telegram bot not available, skipping handler setup');
            return;
        }
        
        this.telegramBot.on('message', async (msg) => {
            try {
                const chatId = msg.chat.id;
                const text = msg.text;
                const userId = `telegram_${chatId}`;

                console.log(`Telegram message from ${chatId}: ${text}`);

                // Handle bot response
                const response = await this.aiBot.handleMessage(userId, text, 'telegram');
                
                // Send response back to Telegram
                await this.telegramBot.sendMessage(chatId, response.text);

                // Handle actions
                await this.handleBotActions(response.actions, userId, 'telegram', chatId);

            } catch (error) {
                console.error('Telegram bot error:', error);
                await this.telegramBot.sendMessage(msg.chat.id, 
                    "I'm sorry, I'm experiencing technical difficulties. Please try again later.");
            }
        });

        this.telegramBot.on('error', (error) => {
            console.error('Telegram bot error:', error);
        });
    }

    // Handle WhatsApp messages
    async handleWhatsAppMessage(from, body) {
        try {
            const userId = `whatsapp_${from}`;
            console.log(`WhatsApp message from ${from}: ${body}`);

            // Handle bot response
            const response = await this.aiBot.handleMessage(userId, body, 'whatsapp');

            // Send response via Twilio WhatsApp
            await this.sendWhatsAppMessage(from, response.text);

            // Handle actions
            await this.handleBotActions(response.actions, userId, 'whatsapp', from);

            return response;

        } catch (error) {
            console.error('WhatsApp handling error:', error);
            await this.sendWhatsAppMessage(from, 
                "I'm sorry, I'm experiencing technical difficulties. Please try again later.");
        }
    }

    // Send WhatsApp message via Twilio
    async sendWhatsAppMessage(to, message) {
        try {
            await this.twilioClient.messages.create({
                body: message,
                from: `whatsapp:${this.channels.voice.phoneNumber}`,
                to: `whatsapp:${to}`
            });
        } catch (error) {
            console.error('WhatsApp send error:', error);
        }
    }

    // Handle voice calls
    async handleVoiceCall(from, to) {
        try {
            console.log(`Voice call from ${from} to ${to}`);

            // Create TwiML for voice response
            const twiml = new twilio.twiml.VoiceResponse();
            
            // Greeting message
            twiml.say({
                voice: 'alice',
                language: 'en-US'
            }, 'Welcome to ComplaintHub. I\'m here to help you lodge a complaint. Please tell me about your issue.');

            // Record user input
            twiml.record({
                maxLength: 30,
                action: '/voice/process',
                method: 'POST',
                transcribe: true,
                transcribeCallback: '/voice/transcribe'
            });

            return twiml.toString();

        } catch (error) {
            console.error('Voice call handling error:', error);
            const twiml = new twilio.twiml.VoiceResponse();
            twiml.say('I apologize, but I\'m experiencing technical difficulties. Please try again later.');
            return twiml.toString();
        }
    }

    // Process voice input
    async processVoiceInput(audioUrl, userId) {
        try {
            // Download audio file
            const audioBuffer = await this.downloadAudio(audioUrl);
            
            // Convert speech to text
            const text = await this.aiBot.speechToText(audioBuffer);
            
            if (!text) {
                return "I'm sorry, I couldn't understand what you said. Please try speaking more clearly.";
            }

            // Process with AI bot
            const response = await this.aiBot.handleMessage(userId, text, 'voice');
            
            // Convert response to speech
            const audioResponse = await this.aiBot.textToSpeech(response.text);
            
            return {
                text: response.text,
                audio: audioResponse,
                actions: response.actions
            };

        } catch (error) {
            console.error('Voice processing error:', error);
            return "I'm sorry, I'm experiencing technical difficulties. Please try again later.";
        }
    }

    // Download audio file from URL
    async downloadAudio(audioUrl) {
        try {
            const response = await fetch(audioUrl);
            const arrayBuffer = await response.arrayBuffer();
            return Buffer.from(arrayBuffer);
        } catch (error) {
            console.error('Audio download error:', error);
            return null;
        }
    }

    // Handle web chat messages
    async handleWebChatMessage(userId, message) {
        try {
            console.log(`Web chat message from ${userId}: ${message}`);

            // Handle bot response
            const response = await this.aiBot.handleMessage(userId, message, 'webchat');

            // Handle actions
            await this.handleBotActions(response.actions, userId, 'webchat');

            return response;

        } catch (error) {
            console.error('Web chat handling error:', error);
            return {
                text: "I'm sorry, I'm experiencing technical difficulties. Please try again later.",
                sentiment: { score: 0, magnitude: 0 },
                priority: 'medium',
                actions: ['escalate_to_human'],
                confidence: 0
            };
        }
    }

    // Handle bot actions across channels
    async handleBotActions(actions, userId, channel, channelId = null) {
        for (const action of actions) {
            try {
                switch (action) {
                    case 'create_complaint':
                        await this.handleCreateComplaint(userId, channel);
                        break;
                    case 'escalate_to_human':
                        await this.escalateToHuman(userId, channel, channelId);
                        break;
                    case 'escalate_priority':
                        await this.escalatePriority(userId, channel);
                        break;
                    case 'ask_for_brand':
                        await this.askForBrand(userId, channel, channelId);
                        break;
                    default:
                        console.log(`Unknown action: ${action}`);
                }
            } catch (error) {
                console.error(`Error handling action ${action}:`, error);
            }
        }
    }

    // Handle complaint creation
    async handleCreateComplaint(userId, channel) {
        try {
            const conversation = this.aiBot.getConversationHistory(userId);
            
            // Extract complaint details from conversation
            const complaintData = this.extractComplaintData(conversation);
            
            if (complaintData.brand && complaintData.description) {
                // Create ticket in database
                const ticket = await this.createTicket(complaintData, userId, channel);
                
                // Update conversation context
                this.aiBot.updateContext(userId, { currentComplaint: ticket.id });
                
                console.log(`Complaint created: ${ticket.id}`);
            }
        } catch (error) {
            console.error('Complaint creation error:', error);
        }
    }

    // Extract complaint data from conversation
    extractComplaintData(conversation) {
        const messages = conversation.messages || [];
        let brand = null;
        let description = null;

        // Simple extraction logic - in production, use more sophisticated NLP
        for (const message of messages) {
            if (message.role === 'user') {
                const text = message.content.toLowerCase();
                
                // Look for brand mentions
                if (text.includes('brand') || text.includes('company')) {
                    brand = this.extractBrandName(message.content);
                }
                
                // Look for complaint description
                if (text.includes('complaint') || text.includes('issue') || text.includes('problem')) {
                    description = message.content;
                }
            }
        }

        return { brand, description };
    }

    // Extract brand name from text
    extractBrandName(text) {
        // Simple extraction - in production, use entity recognition
        const words = text.split(' ');
        const brandKeywords = ['brand', 'company', 'about', 'regarding'];
        
        for (let i = 0; i < words.length; i++) {
            if (brandKeywords.includes(words[i].toLowerCase()) && i + 1 < words.length) {
                return words[i + 1].replace(/[^\w]/g, '');
            }
        }
        
        return null;
    }

    // Create ticket in database
    async createTicket(complaintData, userId, channel) {
        // This would integrate with your existing ticket creation logic
        // For now, return a mock ticket
        return {
            id: `TICKET_${Date.now()}`,
            title: `Complaint about ${complaintData.brand}`,
            description: complaintData.description,
            status: 'open',
            priority: 'medium',
            channel: channel,
            userId: userId,
            createdAt: new Date()
        };
    }

    // Escalate to human support
    async escalateToHuman(userId, channel, channelId) {
        try {
            const message = "I'm connecting you to a human representative. Please wait a moment...";
            
            switch (channel) {
                case 'whatsapp':
                    await this.sendWhatsAppMessage(channelId, message);
                    break;
                case 'telegram':
                    if (this.telegramBot) {
                        await this.telegramBot.sendMessage(channelId, message);
                    } else {
                        console.warn('Telegram bot not available for escalation');
                    }
                    break;
                case 'webchat':
                    // Send to web chat interface
                    break;
                case 'voice':
                    // Transfer call to human agent
                    break;
            }
            
            console.log(`Escalated ${userId} to human support via ${channel}`);
        } catch (error) {
            console.error('Escalation error:', error);
        }
    }

    // Escalate priority
    async escalatePriority(userId, channel) {
        try {
            this.aiBot.updateContext(userId, { priority: 'high' });
            console.log(`Escalated priority for ${userId} via ${channel}`);
        } catch (error) {
            console.error('Priority escalation error:', error);
        }
    }

    // Ask for brand information
    async askForBrand(userId, channel, channelId) {
        try {
            const message = "Could you please tell me which brand or company you'd like to complain about?";
            
            switch (channel) {
                case 'whatsapp':
                    await this.sendWhatsAppMessage(channelId, message);
                    break;
                case 'telegram':
                    if (this.telegramBot) {
                        await this.telegramBot.sendMessage(channelId, message);
                    } else {
                        console.warn('Telegram bot not available for escalation');
                    }
                    break;
                case 'webchat':
                    // Send to web chat interface
                    break;
                case 'voice':
                    // Send voice message
                    break;
            }
        } catch (error) {
            console.error('Ask for brand error:', error);
        }
    }

    // Get channel status
    getChannelStatus() {
        return {
            whatsapp: this.channels.whatsapp.enabled,
            telegram: this.channels.telegram.enabled,
            voice: this.channels.voice.enabled,
            webchat: this.channels.webchat.enabled
        };
    }

    // Update channel configuration
    updateChannelConfig(channel, config) {
        if (this.channels[channel]) {
            this.channels[channel] = { ...this.channels[channel], ...config };
        }
    }
}

module.exports = MultiChannelService; 