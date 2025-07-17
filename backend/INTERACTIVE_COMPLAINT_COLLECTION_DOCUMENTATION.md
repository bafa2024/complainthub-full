# Interactive Complaint Collection Documentation

## Overview

The Interactive Complaint Collection system provides comprehensive connectors for multiple communication channels, enabling users to lodge complaints through various platforms including Twilio, Knowlarity, Exotel, WhatsApp, and Telegram. This system ensures a consistent BOT experience across all channels while maintaining the same ticket creation workflow.

## Supported Channels

### 1. Twilio Integration
- **Voice Calls**: Real-time voice interaction with AI bot
- **SMS**: Text-based complaint collection
- **WhatsApp**: WhatsApp Business API integration
- **Features**: TTS, STT, IVR, recording, transcription

### 2. Knowlarity Integration
- **Voice Calls**: Cloud telephony with AI bot integration
- **SMS**: Text messaging support
- **Features**: Recording, transcription, IVR menus
- **Geographic Focus**: India and other supported regions

### 3. Exotel Integration
- **Voice Calls**: Cloud telephony platform integration
- **SMS**: Text messaging capabilities
- **Features**: Recording, transcription, IVR menus
- **Geographic Focus**: India and other supported regions

### 4. WhatsApp Business API
- **Text Messages**: Rich text messaging
- **Media Support**: Images, documents, audio
- **Quick Replies**: Template-based responses
- **Features**: Message templates, media handling

### 5. Telegram Bot API
- **Text Messages**: Real-time messaging
- **Voice Messages**: Audio complaint support
- **Media Support**: Photos, documents, videos
- **Features**: Inline keyboards, custom commands

## Architecture

### Adapter Pattern
Each communication channel has its own adapter that implements a consistent interface:

```python
class ChannelAdapter:
    def handle_voice_call(self, request_data, conversation_manager, db_session, brand_id)
    def handle_sms(self, request_data, conversation_manager, db_session, brand_id)
    def make_outbound_call(self, to_number, message, voice_id)
    def send_sms(self, to_number, message)
    def create_interactive_voice_response(self, options)
```

### Webhook Processing
All incoming communications are processed through standardized webhook endpoints:

```
POST /api/v1/webhook/{channel}
```

Where `{channel}` can be:
- `twilio` - Twilio voice, SMS, WhatsApp
- `knowlarity` - Knowlarity voice, SMS
- `exotel` - Exotel voice, SMS
- `whatsapp` - WhatsApp Business API
- `telegram` - Telegram Bot API

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890

# Knowlarity Configuration
KNOWLARITY_API_KEY=your_knowlarity_api_key
KNOWLARITY_BASE_URL=https://api.knowlarity.com/v1
KNOWLARITY_FROM_NUMBER=+911800123456

# Exotel Configuration
EXOTEL_SID=your_exotel_sid
EXOTEL_TOKEN=your_exotel_token
EXOTEL_BASE_URL=https://api.exotel.com/v1
EXOTEL_FROM_NUMBER=+911800123456

# WhatsApp Business API
WHATSAPP_BUSINESS_TOKEN=your_whatsapp_business_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/webhook/telegram

# Base URL for webhooks
BASE_URL=http://localhost:8000
```

## API Endpoints

### Webhook Endpoints

#### 1. Twilio Webhook
```
POST /api/v1/webhook/twilio
```

**Supported Events:**
- Voice calls (incoming/outgoing)
- SMS messages
- WhatsApp messages
- Recording callbacks
- Transcription callbacks

**Request Format:**
```json
{
  "From": "+1234567890",
  "To": "+0987654321",
  "CallSid": "call_sid_123",
  "CallStatus": "ringing",
  "Body": "I have a complaint",
  "MessageSid": "msg_sid_123"
}
```

#### 2. Knowlarity Webhook
```
POST /api/v1/webhook/knowlarity
```

**Supported Events:**
- Voice calls
- SMS messages
- Recording callbacks
- Transcription callbacks

**Request Format:**
```json
{
  "from": "+919876543210",
  "to": "+911800123456",
  "call_id": "knowlarity_call_123",
  "status": "ringing",
  "message": "I have a complaint",
  "message_id": "knowlarity_msg_123"
}
```

#### 3. Exotel Webhook
```
POST /api/v1/webhook/exotel
```

**Supported Events:**
- Voice calls
- SMS messages
- Recording callbacks
- Transcription callbacks

**Request Format:**
```json
{
  "From": "+919876543210",
  "To": "+911800123456",
  "CallSid": "exotel_call_123",
  "CallStatus": "ringing",
  "Body": "I have a complaint",
  "MessageSid": "exotel_msg_123"
}
```

#### 4. WhatsApp Webhook
```
POST /api/v1/webhook/whatsapp
```

**Supported Events:**
- Text messages
- Media messages
- Template messages

**Request Format:**
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456789",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "messages": [
              {
                "from": "919876543210",
                "text": {
                  "body": "I have a complaint"
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

#### 5. Telegram Webhook
```
POST /api/v1/webhook/telegram
```

**Supported Events:**
- Text messages
- Voice messages
- Media messages
- Command messages

**Request Format:**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 123,
    "from": {
      "id": 987654321,
      "first_name": "John"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "text": "I have a complaint"
  }
}
```

### Channel Management Endpoints

#### 1. Test Connections
```
POST /api/v1/channels/{provider}/test
```

**Providers:** `twilio`, `knowlarity`, `exotel`, `whatsapp`, `telegram`

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "config_status": "active"
}
```

#### 2. Send SMS
```
POST /api/v1/channels/{provider}/send-sms
```

**Request:**
```json
{
  "to_number": "+919876543210",
  "message": "Thank you for your complaint"
}
```

#### 3. Make Outbound Call
```
POST /api/v1/channels/{provider}/make-call
```

**Request:**
```json
{
  "to_number": "+919876543210",
  "message": "Hello, we are calling to follow up",
  "voice_id": "en-US-Standard-A"
}
```

## Interactive Voice Response (IVR)

### IVR Menu Creation
All voice-enabled channels support Interactive Voice Response menus:

```python
options = [
    {"description": "Lodge a complaint", "response": "Please describe your issue."},
    {"description": "Check complaint status", "response": "Please provide your ticket number."},
    {"description": "Speak to agent", "response": "Connecting you to an agent."}
]

ivr_response = adapter.create_interactive_voice_response(options)
```

### Menu Selection Handling
```python
menu_response = adapter.handle_menu_selection("1", options)
```

## Voice Processing Pipeline

### 1. Speech-to-Text (STT)
- **Deepgram Integration**: Real-time transcription with sentiment analysis
- **Google Cloud Speech**: Fallback transcription service
- **Language Support**: Multiple languages including English, Hindi, and regional languages

### 2. Text-to-Speech (TTS)
- **Google Cloud TTS**: High-quality voice synthesis
- **Voice Selection**: Multiple voices and accents
- **Personalization**: Consistent voice per user

### 3. AI Conversation Management
- **OpenAI GPT Integration**: Natural language understanding
- **Context Management**: Session-based conversation tracking
- **Intent Recognition**: Complaint classification and routing

## Message Flow

### Incoming Message Flow
1. **Webhook Reception**: Channel-specific webhook receives message
2. **Data Extraction**: Extract user message and metadata
3. **Session Management**: Create or retrieve conversation session
4. **AI Processing**: Process through conversation manager
5. **Response Generation**: Generate appropriate response
6. **Channel Delivery**: Send response through original channel

### Outbound Message Flow
1. **Trigger Event**: System event triggers outbound communication
2. **Message Preparation**: Prepare message content and metadata
3. **Channel Selection**: Choose appropriate channel based on user preference
4. **Delivery**: Send message through selected channel
5. **Status Tracking**: Monitor delivery status and handle failures

## Error Handling

### Webhook Verification
All webhooks support verification to ensure security:

```python
def verify_webhook_signature(self, webhook_data: str, signature: str, secret: str) -> bool:
    """Verify webhook signature for security"""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        webhook_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### Fallback Mechanisms
- **Channel Fallback**: If primary channel fails, try alternative channels
- **Retry Logic**: Exponential backoff for failed deliveries
- **Error Logging**: Comprehensive error tracking and monitoring

## Security Considerations

### Authentication
- **API Key Management**: Secure storage of provider API keys
- **Webhook Verification**: Signature verification for all webhooks
- **Rate Limiting**: Prevent abuse and ensure fair usage

### Data Protection
- **Encryption**: All sensitive data encrypted in transit and at rest
- **Privacy**: User data isolation between brands
- **Compliance**: GDPR and local privacy regulation compliance

## Testing

### Test Script
Run the comprehensive test script:
```bash
cd backend
python test_interactive_complaint_collection.py
```

### Test Coverage
- Webhook processing for all channels
- Connection testing for all providers
- Outbound communication testing
- IVR functionality testing
- Error handling and fallback testing

## Monitoring and Analytics

### Health Monitoring
- **Connection Status**: Real-time monitoring of provider connections
- **Delivery Rates**: Track message delivery success rates
- **Response Times**: Monitor system performance and latency

### Analytics Dashboard
- **Channel Usage**: Track usage across different channels
- **User Engagement**: Monitor user interaction patterns
- **Performance Metrics**: System performance and reliability metrics

## Deployment

### Webhook Configuration
Configure webhook URLs in provider dashboards:

```
Twilio: https://your-domain.com/api/v1/webhook/twilio
Knowlarity: https://your-domain.com/api/v1/webhook/knowlarity
Exotel: https://your-domain.com/api/v1/webhook/exotel
WhatsApp: https://your-domain.com/api/v1/webhook/whatsapp
Telegram: https://your-domain.com/api/v1/webhook/telegram
```

### SSL/TLS Requirements
All webhook endpoints require HTTPS for security:
- SSL certificates must be valid
- TLS 1.2 or higher required
- Certificate chain must be complete

## Troubleshooting

### Common Issues

#### Webhook Not Receiving Messages
1. Check webhook URL configuration in provider dashboard
2. Verify SSL certificate validity
3. Check firewall and network connectivity
4. Review webhook logs for errors

#### Message Delivery Failures
1. Verify API credentials and permissions
2. Check rate limits and quotas
3. Review error logs for specific failure reasons
4. Test with provider's test tools

#### Voice Call Issues
1. Verify phone number configuration
2. Check TTS service availability
3. Review audio format compatibility
4. Test with provider's voice testing tools

### Debug Commands
```bash
# Check webhook logs
tail -f app.log | grep webhook

# Test provider connections
curl -X POST http://localhost:8000/api/v1/channels/twilio/test

# Monitor real-time webhook activity
curl -X POST http://localhost:8000/api/v1/webhook/twilio -d "test=1"
```

## Future Enhancements

### Planned Features
- **Multi-language IVR**: Support for multiple languages in voice menus
- **Advanced Analytics**: Detailed conversation analytics and insights
- **Custom Voice Models**: Brand-specific voice customization
- **Integration APIs**: Additional CRM and business system integrations

### Scalability Improvements
- **Load Balancing**: Horizontal scaling for high-volume deployments
- **Caching**: Redis-based caching for improved performance
- **Microservices**: Service decomposition for better maintainability
- **Containerization**: Docker-based deployment for easier scaling

## Conclusion

The Interactive Complaint Collection system provides a comprehensive, multi-channel solution for complaint management. With support for voice, SMS, WhatsApp, and Telegram, it ensures that users can lodge complaints through their preferred communication channel while maintaining a consistent, AI-powered experience.

The system is designed for high availability, security, and scalability, making it suitable for enterprise deployment. All channels are fully integrated with the core complaint management workflow, ensuring seamless ticket creation and tracking regardless of the communication channel used. 