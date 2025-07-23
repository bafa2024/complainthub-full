# SRS Implementation Plan - ComplaintHub System

## Current Status Assessment

### ✅ IMPLEMENTED FEATURES (86.67% Success Rate)
- **Basic Authentication System** - User, Brand, Admin login/signup
- **Admin Portal** - Dashboard, Brands management, Users management  
- **Public Complaint Form** - Anonymous complaint submission
- **Role-based Access Control** - Admin, Brand, User roles
- **Basic Dashboard Analytics** - Stats, charts, overview
- **Frontend Routing & Navigation** - React Router with protected routes
- **Database Schema** - SQLite with users, brands, tickets tables
- **CRUD Operations** - Complete admin brand management

### ❌ MISSING CRITICAL SRS FEATURES

## Phase 1: Core AI BOT Implementation (Priority: HIGH)

### 1.1 AI-Powered Conversational BOT API
**Status**: Not Implemented  
**SRS Requirement**: Conversational voicebot & chatbot with ChatGPT integration

**Implementation Plan**:
```javascript
// New file: backend-nodejs/bot-api.js
const OpenAI = require('openai');
const express = require('express');

class ComplaintBot {
  constructor() {
    this.openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
    this.conversationContext = new Map();
  }

  async processMessage(userId, message, channel = 'web') {
    // Get conversation context
    const context = this.conversationContext.get(userId) || [];
    
    // Build prompt for complaint collection
    const prompt = this.buildComplaintPrompt(message, context);
    
    // Get AI response
    const response = await this.openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 150
    });

    // Update context
    context.push({ role: 'user', content: message });
    context.push({ role: 'assistant', content: response.choices[0].message.content });
    this.conversationContext.set(userId, context);

    return response.choices[0].message.content;
  }

  buildComplaintPrompt(message, context) {
    return `You are a helpful complaint collection assistant. 
    Collect the following information from the user:
    - Brand/Company name
    - Issue description
    - Contact information
    - Priority level
    
    Current conversation: ${JSON.stringify(context)}
    User message: ${message}
    
    Ask relevant follow-up questions to gather complete information.`;
  }
}
```

**API Endpoints to Add**:
- `POST /api/v1/bot/chat` - Text-based chat
- `POST /api/v1/bot/voice` - Voice-based interaction
- `GET /api/v1/bot/context/:userId` - Get conversation context

### 1.2 Sentiment Analysis & Classification
**Status**: Not Implemented  
**SRS Requirement**: Analyze urgency, abuse level, and category

**Implementation Plan**:
```javascript
// New file: backend-nodejs/sentiment-analyzer.js
const { LanguageServiceClient } = require('@google-cloud/language');

class SentimentAnalyzer {
  constructor() {
    this.languageClient = new LanguageServiceClient();
  }

  async analyzeComplaint(text) {
    const document = {
      content: text,
      type: 'PLAIN_TEXT',
    };

    const [result] = await this.languageClient.analyzeSentiment({ document });
    const sentiment = result.documentSentiment;

    return {
      sentiment_score: sentiment.score,
      sentiment_magnitude: sentiment.magnitude,
      urgency_level: this.determineUrgency(sentiment.score, sentiment.magnitude),
      abuse_level: await this.detectAbuse(text),
      category: await this.classifyCategory(text)
    };
  }

  determineUrgency(score, magnitude) {
    if (score < -0.5 && magnitude > 2.0) return 'high';
    if (score < -0.2) return 'medium';
    return 'low';
  }

  async detectAbuse(text) {
    // Implement abuse detection logic
    const abusiveWords = ['abuse', 'hate', 'terrible', 'worst'];
    const lowerText = text.toLowerCase();
    const abuseCount = abusiveWords.filter(word => lowerText.includes(word)).length;
    
    if (abuseCount > 3) return 'high';
    if (abuseCount > 1) return 'medium';
    return 'low';
  }

  async classifyCategory(text) {
    const categories = {
      'service': ['service', 'support', 'help', 'assistance'],
      'product': ['product', 'quality', 'defect', 'broken'],
      'billing': ['billing', 'payment', 'charge', 'money'],
      'delivery': ['delivery', 'shipping', 'arrive', 'late']
    };

    const lowerText = text.toLowerCase();
    for (const [category, keywords] of Object.entries(categories)) {
      if (keywords.some(keyword => lowerText.includes(keyword))) {
        return category;
      }
    }
    return 'general';
  }
}
```

## Phase 2: Multi-Channel Integration (Priority: HIGH)

### 2.1 WhatsApp Integration
**Status**: Not Implemented  
**SRS Requirement**: WhatsApp Business API integration

**Implementation Plan**:
```javascript
// New file: backend-nodejs/channels/whatsapp.js
const axios = require('axios');

class WhatsAppChannel {
  constructor() {
    this.accessToken = process.env.WHATSAPP_ACCESS_TOKEN;
    this.phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID;
    this.baseURL = 'https://graph.facebook.com/v17.0';
  }

  async sendMessage(to, message) {
    const response = await axios.post(
      `${this.baseURL}/${this.phoneNumberId}/messages`,
      {
        messaging_product: 'whatsapp',
        to: to,
        type: 'text',
        text: { body: message }
      },
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  }

  async handleIncomingMessage(data) {
    const message = data.entry[0].changes[0].value.messages[0];
    const from = message.from;
    const text = message.text.body;

    // Process with bot
    const botResponse = await this.bot.processMessage(from, text, 'whatsapp');
    
    // Send response back
    await this.sendMessage(from, botResponse);
  }
}
```

### 2.2 Telegram Integration
**Status**: Not Implemented  
**SRS Requirement**: Telegram bot API integration

**Implementation Plan**:
```javascript
// New file: backend-nodejs/channels/telegram.js
const TelegramBot = require('node-telegram-bot-api');

class TelegramChannel {
  constructor() {
    this.bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: true });
    this.setupHandlers();
  }

  setupHandlers() {
    this.bot.on('message', async (msg) => {
      const chatId = msg.chat.id;
      const text = msg.text;

      // Process with bot
      const response = await this.bot.processMessage(chatId.toString(), text, 'telegram');
      
      // Send response
      this.bot.sendMessage(chatId, response);
    });
  }
}
```

### 2.3 Voice Processing (STT/TTS)
**Status**: Not Implemented  
**SRS Requirement**: Deepgram integration for voice processing

**Implementation Plan**:
```javascript
// New file: backend-nodejs/voice/voice-processor.js
const { Deepgram } = require('@deepgram/sdk');
const { TextToSpeechClient } = require('@google-cloud/text-to-speech');

class VoiceProcessor {
  constructor() {
    this.deepgram = new Deepgram(process.env.DEEPGRAM_API_KEY);
    this.ttsClient = new TextToSpeechClient();
  }

  async speechToText(audioBuffer) {
    const response = await this.deepgram.transcription.preRecorded(
      { buffer: audioBuffer, mimetype: 'audio/wav' },
      {
        smart_format: true,
        model: 'nova',
        language: 'en-US',
        punctuate: true,
        sentiment: true
      }
    );

    return {
      text: response.results.channels[0].alternatives[0].transcript,
      sentiment: response.results.channels[0].alternatives[0].sentiment,
      confidence: response.results.channels[0].alternatives[0].confidence
    };
  }

  async textToSpeech(text, voiceId = 'en-US-Standard-A') {
    const request = {
      input: { text: text },
      voice: { languageCode: 'en-US', name: voiceId },
      audioConfig: { audioEncoding: 'MP3' },
    };

    const [response] = await this.ttsClient.synthesizeSpeech(request);
    return response.audioContent;
  }
}
```

## Phase 3: Telephony Integration (Priority: MEDIUM)

### 3.1 Twilio Integration
**Status**: Not Implemented  
**SRS Requirement**: Voice calls and SMS integration

**Implementation Plan**:
```javascript
// New file: backend-nodejs/telephony/twilio-integration.js
const twilio = require('twilio');

class TwilioIntegration {
  constructor() {
    this.client = twilio(
      process.env.TWILIO_ACCOUNT_SID,
      process.env.TWILIO_AUTH_TOKEN
    );
  }

  async handleIncomingCall(req, res) {
    const twiml = new twilio.twiml.VoiceResponse();
    
    twiml.say('Welcome to ComplaintHub. Please describe your issue.');
    twiml.record({
      action: '/api/v1/telephony/process-recording',
      maxLength: 60,
      transcribe: true
    });

    res.type('text/xml');
    res.send(twiml.toString());
  }

  async processRecording(req, res) {
    const recordingUrl = req.body.RecordingUrl;
    const transcription = req.body.TranscriptionText;
    
    // Process with bot and sentiment analysis
    const analysis = await this.sentimentAnalyzer.analyzeComplaint(transcription);
    
    // Create ticket
    const ticket = await this.createTicket({
      title: 'Voice Complaint',
      description: transcription,
      urgency_level: analysis.urgency_level,
      category: analysis.category,
      channel: 'voice'
    });

    res.json({ success: true, ticket_id: ticket.id });
  }
}
```

## Phase 4: Billing & Credit Management (Priority: MEDIUM)

### 4.1 Credit System Implementation
**Status**: Not Implemented  
**SRS Requirement**: Credit balance and billing management

**Implementation Plan**:
```javascript
// New file: backend-nodejs/billing/credit-manager.js
class CreditManager {
  async checkCreditBalance(brandId) {
    const brand = await this.getBrand(brandId);
    return brand.credit_balance;
  }

  async deductCredits(brandId, amount, reason) {
    const brand = await this.getBrand(brandId);
    
    if (brand.credit_balance < amount) {
      throw new Error('Insufficient credits');
    }

    await this.updateBrandCredits(brandId, brand.credit_balance - amount);
    
    // Log transaction
    await this.logTransaction({
      brand_id: brandId,
      amount: -amount,
      reason: reason,
      timestamp: new Date()
    });
  }

  async addCredits(brandId, amount, paymentMethod) {
    const brand = await this.getBrand(brandId);
    await this.updateBrandCredits(brandId, brand.credit_balance + amount);
    
    // Log transaction
    await this.logTransaction({
      brand_id: brandId,
      amount: amount,
      reason: 'Credit purchase',
      payment_method: paymentMethod,
      timestamp: new Date()
    });
  }

  async processComplaintCharges() {
    // Check for complaints older than 24 hours
    const oldComplaints = await this.getOldComplaints();
    
    for (const complaint of oldComplaints) {
      if (complaint.status !== 'resolved') {
        await this.deductCredits(complaint.brand_id, 50, '24h complaint charge');
        await this.updateComplaintStatus(complaint.id, 'charged');
      }
    }
  }
}
```

## Phase 5: Automated Follow-up System (Priority: MEDIUM)

### 5.1 Follow-up Workflow
**Status**: Not Implemented  
**SRS Requirement**: Automated resolution confirmation

**Implementation Plan**:
```javascript
// New file: backend-nodejs/followup/followup-manager.js
class FollowupManager {
  async scheduleFollowup(ticketId, delayHours = 24) {
    const followupTime = new Date(Date.now() + delayHours * 60 * 60 * 1000);
    
    await this.createFollowupJob({
      ticket_id: ticketId,
      scheduled_time: followupTime,
      status: 'pending'
    });
  }

  async processFollowups() {
    const pendingFollowups = await this.getPendingFollowups();
    
    for (const followup of pendingFollowups) {
      const ticket = await this.getTicket(followup.ticket_id);
      
      if (ticket.status === 'resolved') {
        await this.sendFollowupMessage(ticket);
        await this.updateFollowupStatus(followup.id, 'sent');
      }
    }
  }

  async sendFollowupMessage(ticket) {
    const message = `Hello! We're following up on your complaint about ${ticket.brand_name}. 
    Has your issue been resolved? Please reply with:
    1 - Yes, resolved
    2 - No, still have issues
    3 - Need more time`;

    // Send via original channel
    switch (ticket.channel) {
      case 'whatsapp':
        await this.whatsappChannel.sendMessage(ticket.user_phone, message);
        break;
      case 'voice':
        await this.voiceChannel.makeCall(ticket.user_phone, message);
        break;
      case 'web':
        await this.emailChannel.sendEmail(ticket.user_email, message);
        break;
    }
  }
}
```

## Phase 6: CRM Integration (Priority: LOW)

### 6.1 Webhook System
**Status**: Not Implemented  
**SRS Requirement**: CRM integration via webhooks

**Implementation Plan**:
```javascript
// New file: backend-nodejs/integrations/crm-webhooks.js
class CRMWebhookManager {
  async registerWebhook(brandId, webhookUrl, events) {
    await this.createWebhook({
      brand_id: brandId,
      url: webhookUrl,
      events: JSON.stringify(events),
      active: true
    });
  }

  async triggerWebhook(brandId, event, data) {
    const webhooks = await this.getBrandWebhooks(brandId);
    
    for (const webhook of webhooks) {
      if (webhook.events.includes(event)) {
        await this.sendWebhook(webhook.url, {
          event: event,
          data: data,
          timestamp: new Date().toISOString()
        });
      }
    }
  }

  async handleIncomingWebhook(req, res) {
    const { event, data } = req.body;
    
    switch (event) {
      case 'ticket_updated':
        await this.updateTicketFromCRM(data);
        break;
      case 'ticket_resolved':
        await this.resolveTicketFromCRM(data);
        break;
    }
    
    res.json({ success: true });
  }
}
```

## Phase 7: SEO & Public Portal (Priority: LOW)

### 7.1 SEO Optimization
**Status**: Not Implemented  
**SRS Requirement**: Public complaint indexing

**Implementation Plan**:
```javascript
// New file: frontend/src/components/public/PublicComplaints.jsx
// Enhanced with SEO features

const PublicComplaints = () => {
  const [complaints, setComplaints] = useState([]);
  const [brandFilter, setBrandFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  useEffect(() => {
    // Set meta tags for SEO
    document.title = 'Public Complaints - ComplaintHub';
    document.querySelector('meta[name="description"]').setAttribute('content', 
      'Browse and track customer complaints against various brands. Transparent complaint resolution platform.');
  }, []);

  return (
    <div className="public-complaints">
      <h1>Public Complaints</h1>
      <p>Browse complaints and track resolution status</p>
      
      {/* SEO-friendly URL structure */}
      <div className="filters">
        <input 
          type="text" 
          placeholder="Filter by brand..."
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
        />
      </div>

      <div className="complaints-list">
        {complaints.map(complaint => (
          <div key={complaint.id} className="complaint-card">
            <h3>{complaint.title}</h3>
            <p>Brand: {complaint.brand_name}</p>
            <p>Status: {complaint.status}</p>
            <p>Posted: {new Date(complaint.created_at).toLocaleDateString()}</p>
            
            {/* SEO-friendly complaint URLs */}
            <Link to={`/complaints/${complaint.brand_name}/${complaint.id}`}>
              View Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Implementation Timeline

### Week 1: Core AI BOT
- [ ] Set up OpenAI integration
- [ ] Implement conversational bot logic
- [ ] Add sentiment analysis
- [ ] Create bot API endpoints

### Week 2: Multi-Channel Integration
- [ ] WhatsApp Business API integration
- [ ] Telegram bot integration
- [ ] Voice processing (STT/TTS)
- [ ] Web chat widget

### Week 3: Telephony & Billing
- [ ] Twilio voice integration
- [ ] Credit management system
- [ ] Billing workflows
- [ ] Payment processing

### Week 4: Advanced Features
- [ ] Automated follow-up system
- [ ] CRM webhooks
- [ ] SEO optimization
- [ ] Testing & deployment

## Required Dependencies

### Backend Dependencies
```json
{
  "openai": "^4.0.0",
  "@google-cloud/language": "^5.0.0",
  "@google-cloud/text-to-speech": "^4.0.0",
  "@deepgram/sdk": "^1.0.0",
  "twilio": "^4.0.0",
  "node-telegram-bot-api": "^0.60.0",
  "stripe": "^12.0.0",
  "node-cron": "^3.0.0"
}
```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_credentials.json
DEEPGRAM_API_KEY=your_deepgram_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
TELEGRAM_BOT_TOKEN=your_telegram_token
STRIPE_SECRET_KEY=your_stripe_key
```

## Success Metrics

### Technical Metrics
- [ ] Bot response time < 2 seconds
- [ ] 99.9% uptime for core services
- [ ] Voice processing accuracy > 95%
- [ ] Sentiment analysis accuracy > 90%

### Business Metrics
- [ ] Complaint resolution rate > 80%
- [ ] User satisfaction score > 4.0/5.0
- [ ] Brand response time < 24 hours
- [ ] Platform adoption by 100+ brands

## Risk Mitigation

### Technical Risks
1. **API Rate Limits**: Implement caching and rate limiting
2. **Voice Processing Errors**: Fallback to text-based interaction
3. **AI Response Quality**: Implement response validation and human fallback

### Business Risks
1. **Data Privacy**: Implement GDPR compliance
2. **Scalability**: Use cloud-native architecture
3. **Cost Management**: Monitor API usage and optimize

This implementation plan provides a comprehensive roadmap to achieve full SRS compliance while maintaining the existing functionality. 