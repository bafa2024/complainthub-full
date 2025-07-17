# Chat/Message Webhook Endpoints Documentation

## Overview

This document describes the implementation of chat/message webhook endpoints with `/webhook/chat/{channel}` handlers for the Brand Complaint Management System. The system now supports comprehensive chat message handling across multiple messaging platforms including WhatsApp, Telegram, Instagram, Facebook, LinkedIn, and WebChat.

## 🎯 Supported Channels

### 1. WhatsApp Business API
- **Webhook Base**: `/api/v1/webhook/chat/whatsapp`
- **Features**: Text messages, media files, quick replies, template messages
- **Response Format**: JSON

### 2. Telegram Bot
- **Webhook Base**: `/api/v1/webhook/chat/telegram`
- **Features**: Text messages, voice messages, photos, documents, inline keyboards
- **Response Format**: JSON

### 3. Instagram Direct Messages
- **Webhook Base**: `/api/v1/webhook/chat/instagram`
- **Features**: Text messages, media, quick replies
- **Response Format**: JSON

### 4. Facebook Messenger
- **Webhook Base**: `/api/v1/webhook/chat/facebook`
- **Features**: Text messages, media, buttons, quick replies, templates
- **Response Format**: JSON

### 5. LinkedIn Messaging
- **Webhook Base**: `/api/v1/webhook/chat/linkedin`
- **Features**: Text messages, media attachments
- **Response Format**: JSON

### 6. WebChat
- **Webhook Base**: `/api/v1/webhook/chat/webchat`
- **Features**: Real-time chat, file uploads, session management
- **Response Format**: JSON

## 📡 Webhook Endpoints

### Main Chat Webhook
```
POST /api/v1/webhook/chat/{channel}
```

**Supported channels**: `whatsapp`, `telegram`, `instagram`, `facebook`, `linkedin`, `webchat`

**Purpose**: Handle incoming chat messages and generate appropriate responses

### Media Webhook
```
POST /api/v1/webhook/chat/{channel}/media
```

**Purpose**: Handle media file uploads (images, documents, voice messages)

### Status Webhook
```
POST /api/v1/webhook/chat/{channel}/status
```

**Purpose**: Handle message delivery status updates

### Typing Webhook
```
POST /api/v1/webhook/chat/{channel}/typing
```

**Purpose**: Handle typing indicators and user activity

## 🔧 Implementation Details

### 1. Channel-Specific Handlers

Each channel has dedicated handlers that:
- Process channel-specific data formats
- Generate appropriate responses
- Handle errors and edge cases
- Integrate with the conversation manager and AI engine

### 2. Data Processing

The webhook handlers:
- Extract message information (sender, recipient, message content)
- Determine brand ID based on message content or user mapping
- Process media files and attachments
- Handle status updates and typing indicators
- Create tickets and manage conversations

### 3. Response Generation

**All Channels**:
- Generate JSON responses
- Include message acknowledgments
- Handle conversation flow
- Provide appropriate error messages

## 📋 Webhook Data Formats

### WhatsApp Chat Data
```json
{
  "From": "whatsapp:+1234567890",
  "To": "whatsapp:+0987654321",
  "Body": "I have a complaint about your service",
  "MessageSid": "whatsapp_msg_123"
}
```

### WhatsApp Media Data
```json
{
  "From": "whatsapp:+1234567890",
  "To": "whatsapp:+0987654321",
  "MediaUrl0": "https://example.com/image.jpg",
  "MediaContentType0": "image/jpeg",
  "MessageSid": "whatsapp_msg_123"
}
```

### Telegram Chat Data
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

### Telegram Media Data
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 124,
    "from": {
      "id": 987654321,
      "first_name": "John"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "photo": [
      {
        "file_id": "photo_123",
        "file_size": 1024
      }
    ],
    "caption": "Screenshot of the issue"
  }
}
```

### Instagram Chat Data
```json
{
  "object": "instagram",
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

### Facebook Chat Data
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

### LinkedIn Chat Data
```json
{
  "message": {
    "id": "linkedin_msg_123",
    "from": {"id": "987654321"},
    "text": "I have a complaint about your service"
  }
}
```

### WebChat Data
```json
{
  "session_id": "webchat_session_123",
  "message": "I have a complaint about your service",
  "user_id": "user_123",
  "user_name": "John Doe",
  "brand_id": 1
}
```

### WebChat Media Data
```json
{
  "session_id": "webchat_session_123",
  "message": "Screenshot of the issue",
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

## 🔌 Integration Points

### 1. Conversation Manager
- Manages conversation state and context
- Handles returning user recognition
- Maintains conversation history

### 2. AI Engine
- Analyzes message content
- Classifies complaints and extracts details
- Determines sentiment and urgency

### 3. Ticket Management
- Creates tickets from chat messages
- Updates ticket status based on conversations
- Manages ticket lifecycle

### 4. Brand Management
- Determines brand ID from message content
- Applies brand-specific configurations
- Routes messages to appropriate brand

## 🛡️ Security and Validation

### 1. Webhook Verification
- Validates webhook signatures (where supported)
- Verifies request authenticity
- Prevents unauthorized access

### 2. Data Validation
- Validates required fields
- Sanitizes input data
- Handles malformed requests

### 3. Error Handling
- Graceful error responses
- Detailed error logging
- Fallback mechanisms

## 📊 Monitoring and Analytics

### 1. Message Metrics
- Message delivery rates
- Response times
- Channel performance comparison

### 2. Quality Metrics
- User satisfaction ratings
- Resolution times
- Conversation quality scores

### 3. Error Tracking
- Failed webhook attempts
- Channel-specific errors
- System performance issues

## 🚀 Configuration

### Environment Variables
```bash
# WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+1234567890
WHATSAPP_BUSINESS_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/webhook/chat/telegram

# Instagram Configuration
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_VERIFY_TOKEN=your_verify_token

# Facebook Configuration
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_access_token
FACEBOOK_VERIFY_TOKEN=your_verify_token
FACEBOOK_APP_SECRET=your_app_secret

# LinkedIn Configuration
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_VERIFY_TOKEN=your_verify_token

# WebChat Configuration
WEBSOCKET_ENABLED=true
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=8001
```

### Webhook URLs
Configure these webhook URLs in your messaging platform dashboard:

**WhatsApp**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/whatsapp`
- Media: `https://your-domain.com/api/v1/webhook/chat/whatsapp/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/whatsapp/status`

**Telegram**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/telegram`
- Media: `https://your-domain.com/api/v1/webhook/chat/telegram/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/telegram/status`

**Instagram**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/instagram`
- Media: `https://your-domain.com/api/v1/webhook/chat/instagram/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/instagram/status`

**Facebook**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/facebook`
- Media: `https://your-domain.com/api/v1/webhook/chat/facebook/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/facebook/status`

**LinkedIn**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/linkedin`
- Media: `https://your-domain.com/api/v1/webhook/chat/linkedin/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/linkedin/status`

**WebChat**:
- Chat: `https://your-domain.com/api/v1/webhook/chat/webchat`
- Media: `https://your-domain.com/api/v1/webhook/chat/webchat/media`
- Status: `https://your-domain.com/api/v1/webhook/chat/webchat/status`

## 🧪 Testing

### Test Script
Run the comprehensive test script:
```bash
python test_chat_webhooks.py
```

### Manual Testing
1. **WhatsApp Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/chat/whatsapp" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=whatsapp:+1234567890&To=whatsapp:+0987654321&Body=Test message&MessageSid=test_123"
   ```

2. **Telegram Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/chat/telegram" \
        -H "Content-Type: application/json" \
        -d '{"update_id": 123456789, "message": {"message_id": 123, "from": {"id": 987654321}, "chat": {"id": 987654321}, "text": "Test message"}}'
   ```

3. **WebChat Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/chat/webchat" \
        -H "Content-Type: application/json" \
        -d '{"session_id": "test_123", "message": "Test message", "user_id": "user_123", "user_name": "John Doe", "brand_id": 1}'
   ```

## 🔄 Workflow Examples

### Complete Chat Complaint Flow

1. **User sends message via any channel**
2. **System receives webhook and processes message**
3. **AI analyzes message content and intent**
4. **System creates or updates ticket**
5. **System generates appropriate response**
6. **Response is sent back to user**
7. **Conversation continues until resolution**

### Media Upload Flow

1. **User uploads media file (image, document, voice)**
2. **System receives media webhook**
3. **System downloads and processes media**
4. **AI analyzes media content (if applicable)**
5. **System creates ticket with media attachment**
6. **System acknowledges media receipt**
7. **Conversation continues with media context**

### Status Update Flow

1. **Message delivery status changes**
2. **System receives status webhook**
3. **System updates message status in database**
4. **System logs status change for analytics**
5. **System triggers appropriate actions (if needed)**

## 🎯 Best Practices

### 1. Error Handling
- Always provide fallback responses
- Log errors for debugging
- Implement retry mechanisms

### 2. Performance
- Optimize response times
- Cache frequently used data
- Monitor webhook performance

### 3. Security
- Validate all incoming data
- Implement rate limiting
- Use HTTPS for all webhooks

### 4. User Experience
- Provide clear responses
- Handle media gracefully
- Maintain conversation context

## 📈 Future Enhancements

### 1. Additional Channels
- Support for more messaging platforms
- Channel-specific optimizations
- Unified channel interface

### 2. Advanced Features
- Multi-language support
- Rich media responses
- Advanced conversation flows

### 3. Analytics
- Real-time message analytics
- Performance dashboards
- Predictive response routing

## 🔗 Related Documentation

- [Multi-Channel Integration Guide](MULTI_CHANNEL_INTEGRATION_GUIDE.md)
- [Phone Call Webhook Documentation](PHONE_CALL_WEBHOOK_DOCUMENTATION.md)
- [Interactive Complaint Collection Documentation](INTERACTIVE_COMPLAINT_COLLECTION_DOCUMENTATION.md)
- [AI Voice Integration Guide](AI_VOICE_INTEGRATION_GUIDE.md)

---

**Note**: This implementation provides comprehensive chat/message webhook support across multiple messaging platforms, ensuring seamless complaint collection and management for the Brand Complaint Management System. 