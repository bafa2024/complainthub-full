# Multi-Channel Bot Integration Guide

## Overview

This guide covers the comprehensive multi-channel bot implementation for the Brand Complaint Management System. The system now supports multiple communication channels including WhatsApp, Telegram, Facebook Messenger, Voice calls, SMS, and Web Chat.

## 🚀 Supported Channels

### 1. WhatsApp Business API
- **Provider**: Twilio WhatsApp or Meta WhatsApp Business API
- **Features**: Text messages, media files, quick replies, template messages
- **Webhook**: `/api/v1/webhook/whatsapp`

### 2. Telegram Bot
- **Provider**: Telegram Bot API
- **Features**: Text messages, voice messages, photos, documents, inline keyboards
- **Webhook**: `/api/v1/webhook/telegram`

### 3. Facebook Messenger
- **Provider**: Facebook Messenger Platform
- **Features**: Text messages, media, buttons, quick replies, templates
- **Webhook**: `/api/v1/webhook/facebook`

### 4. Voice Calls (Twilio)
- **Provider**: Twilio Voice API
- **Features**: Voice recording, transcription, IVR, TTS responses
- **Webhook**: `/api/v1/webhook/voice`

### 5. SMS (Twilio)
- **Provider**: Twilio SMS API
- **Features**: Text messages, media messages
- **Webhook**: `/api/v1/webhook/sms`

### 6. Web Chat
- **Provider**: Custom implementation
- **Features**: Real-time chat, file uploads, session management
- **Webhook**: `/api/v1/webhook/webchat`

### 7. Instagram Direct Messages
- **Provider**: Instagram Graph API
- **Features**: Text messages, media, quick replies
- **Webhook**: `/api/v1/webhook/instagram`

### 8. LinkedIn Messaging
- **Provider**: LinkedIn API
- **Features**: Text messages
- **Webhook**: `/api/v1/webhook/linkedin`

## 📋 Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890

# WhatsApp Business API (Alternative to Twilio)
WHATSAPP_BUSINESS_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/webhook/telegram

# Facebook Messenger
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token
FACEBOOK_APP_SECRET=your_app_secret

# WebSocket Configuration
WEBSOCKET_ENABLED=true
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
```

### Channel Configuration

Enable/disable channels in `backend/app/config/settings.py`:

```python
ENABLED_CHANNELS = ["whatsapp", "telegram", "facebook", "webchat", "voice", "sms", "instagram", "linkedin"]
```

## 🔧 Setup Instructions

### 1. WhatsApp Setup

#### Option A: Using Twilio
1. Create a Twilio account
2. Get your Account SID and Auth Token
3. Purchase a WhatsApp-enabled phone number
4. Configure webhook URL: `https://your-domain.com/api/v1/webhook/whatsapp`

#### Option B: Using Meta WhatsApp Business API
1. Create a Meta Developer account
2. Set up a WhatsApp Business app
3. Get your access token and phone number ID
4. Configure webhook URL: `https://your-domain.com/api/v1/webhook/whatsapp`

### 2. Telegram Setup
1. Create a bot using @BotFather
2. Get your bot token
3. Set webhook URL: `https://your-domain.com/api/v1/webhook/telegram`
4. Use the API endpoint: `POST /api/v1/telegram/set-webhook`

### 3. Facebook Messenger Setup
1. Create a Facebook Developer account
2. Create a Facebook app
3. Set up Messenger product
4. Get your page access token
5. Configure webhook URL: `https://your-domain.com/api/v1/webhook/facebook`
6. Set verify token in your app settings

### 4. Twilio Voice/SMS Setup
1. Create a Twilio account
2. Get your Account SID and Auth Token
3. Purchase phone numbers for voice and SMS
4. Configure webhook URLs:
   - Voice: `https://your-domain.com/api/v1/webhook/voice`
   - SMS: `https://your-domain.com/api/v1/webhook/sms`

### 5. WebChat Setup
1. No external setup required
2. WebSocket server runs on port 8001 by default
3. Configure in frontend to connect to WebSocket

### 6. Instagram Setup
1. Create a Facebook Developer account and Instagram Business account
2. Set up Instagram Graph API and get access token
3. Configure webhook URL: `https://your-domain.com/api/v1/webhook/instagram`

### 7. LinkedIn Setup
1. Create a LinkedIn Developer account
2. Set up LinkedIn Messaging API and get access token
3. Configure webhook URL: `https://your-domain.com/api/v1/webhook/linkedin`

## 📡 Webhook Endpoints

### Main Webhook Endpoint
```
POST /api/v1/webhook/{channel}
```

Supported channels: `whatsapp`, `telegram`, `facebook`, `webchat`, `voice`, `sms`, `instagram`, `linkedin`

### Voice-Specific Endpoints
```
POST /api/v1/webhook/voice/transcription
POST /api/v1/webhook/voice/recording
POST /api/v1/webhook/voice/ivr
```

### Facebook Verification
```
GET /api/v1/webhook/facebook/verify
```

## 🔌 Channel Management API

### Get All Channels
```
GET /api/v1/channels/
```

Response:
```json
{
  "channels": [
    {
      "id": "whatsapp",
      "name": "WhatsApp",
      "enabled": true,
      "status": "configured",
      "message": "Configured via Twilio",
      "config": {
        "twilio_enabled": true,
        "business_api_enabled": false,
        "phone_number": "+1234567890"
      }
    }
  ],
  "total_enabled": 6,
  "total_configured": 5
}
```

### Test Channel
```
POST /api/v1/channels/{channel_id}/test
```

Example for WhatsApp:
```json
{
  "phone_number": "+1234567890",
  "message": "Test message"
}
```

### Configure Channel
```
POST /api/v1/channels/{channel_id}/configure
```

### Get Webhook URL
```
GET /api/v1/channels/{channel_id}/webhook-url
```

## 💬 Message Format Examples

### WhatsApp (Twilio Format)
```json
{
  "From": "whatsapp:+1234567890",
  "To": "whatsapp:+0987654321",
  "Body": "I have a complaint about your service",
  "MediaUrl0": "https://example.com/image.jpg"
}
```

### Telegram
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 123,
    "from": {
      "id": 987654321,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "text": "I have a complaint about your service"
  }
}
```

### Facebook Messenger
```json
{
  "object": "page",
  "entry": [
    {
      "id": "123456789",
      "time": 1234567890,
      "messaging": [
        {
          "sender": {"id": "987654321"},
          "recipient": {"id": "123456789"},
          "timestamp": 1234567890000,
          "message": {
            "mid": "mid.123456789",
            "text": "I have a complaint about your service"
          }
        }
      ]
    }
  ]
}
```

### WebChat
```json
{
  "session_id": "session_123",
  "message": "I have a complaint about your service",
  "user_id": "user_123",
  "user_name": "John Doe",
  "brand_id": 1,
  "file_upload": {
    "name": "screenshot.png",
    "type": "image/png",
    "size": 1024,
    "url": "https://example.com/file.png"
  }
}
```

### Voice Call (Twilio)
```
From: +1234567890
To: +0987654321
CallSid: call_sid_123
CallStatus: ringing
```

## 🎯 Advanced Features

### 1. Interactive Voice Response (IVR)
The system supports IVR with the following options:
- Press 1: Lodge a complaint
- Press 2: Check complaint status
- Press 3: Speak to agent
- Press 4: Hear options again

### 2. Voice Transcription
- Automatic transcription of voice messages
- Sentiment analysis on transcribed text
- Integration with AI engine for response generation

### 3. Media Handling
- Image, video, audio, and document support
- File type validation
- Size limits enforcement
- Automatic categorization

### 4. Quick Replies
- WhatsApp quick reply buttons
- Telegram inline keyboards
- Facebook quick replies
- WebChat quick reply options

### 5. Template Messages
- WhatsApp template messages
- Facebook template messages
- Brand-specific templates

## 🧪 Testing

### Run Test Script
```bash
python test_multi_channel_integration.py
```

This script tests:
- Channel API endpoints
- Webhook processing
- Voice transcription
- Voice recording
- IVR functionality
- Facebook verification
- Channel testing endpoints

### Manual Testing

#### Test WhatsApp
```bash
curl -X POST http://localhost:8000/api/v1/webhook/whatsapp \
  -d "From=whatsapp:+1234567890" \
  -d "To=whatsapp:+0987654321" \
  -d "Body=Test complaint"
```

#### Test Telegram
```bash
curl -X POST http://localhost:8000/api/v1/webhook/telegram \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 123,
      "from": {"id": 987654321, "first_name": "Test"},
      "chat": {"id": 987654321, "type": "private"},
      "text": "Test complaint"
    }
  }'
```

#### Test WebChat
```bash
curl -X POST http://localhost:8000/api/v1/webhook/webchat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "message": "Test complaint",
    "brand_id": 1
  }'
```

## 🔒 Security Considerations

### 1. Webhook Verification
- Facebook webhook verification
- Telegram webhook verification
- WhatsApp webhook signature validation

### 2. Rate Limiting
- Implement rate limiting for webhook endpoints
- Prevent abuse and spam

### 3. Input Validation
- Validate all incoming webhook data
- Sanitize user inputs
- File type and size validation

### 4. Authentication
- Secure API endpoints with authentication
- Use environment variables for sensitive data
- Implement proper error handling

## 🚨 Troubleshooting

### Common Issues

#### 1. Webhook Not Receiving Messages
- Check webhook URL configuration
- Verify SSL certificate (required for production)
- Check firewall settings
- Review webhook logs

#### 2. Authentication Errors
- Verify API keys and tokens
- Check environment variables
- Ensure proper permissions

#### 3. Message Delivery Issues
- Check phone number format
- Verify account status
- Review rate limits
- Check message content compliance

#### 4. Voice Call Issues
- Verify Twilio credentials
- Check phone number configuration
- Review TwiML syntax
- Test with Twilio console

### Debug Mode
Enable debug logging in `backend/app/config/settings.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Log Files
Check log files for detailed error information:
- `backend/app.log`
- Webhook processing logs
- Channel adapter logs

## 📈 Monitoring

### Key Metrics
- Message delivery rates
- Response times
- Error rates
- Channel usage statistics
- User engagement metrics

### Health Checks
```bash
# Check channel status
curl http://localhost:8000/api/v1/channels/

# Test specific channel
curl -X POST http://localhost:8000/api/v1/channels/whatsapp/test \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "message": "Health check"}'
```

## 🔄 Integration with Frontend

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/chat');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  // Handle incoming messages
};

ws.send(JSON.stringify({
  type: 'message',
  content: 'Hello from frontend'
}));
```

### API Integration
```javascript
// Send message via API
const response = await fetch('/api/v1/webhook/webchat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: 'session_123',
    message: 'User message',
    brand_id: 1
  })
});
```

## 📚 Additional Resources

- [Twilio Documentation](https://www.twilio.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Facebook Messenger Platform](https://developers.facebook.com/docs/messenger-platform)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files
3. Test with the provided test script
4. Consult the API documentation
5. Check channel provider documentation

---

**Note**: This implementation provides a solid foundation for multi-channel communication. Each channel can be further customized based on specific business requirements and branding needs. 