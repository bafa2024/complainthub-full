# Phone Call Webhook Endpoints Documentation

## Overview

This document describes the implementation of phone call webhook endpoints with `/webhook/voice/{provider}` handlers for the Brand Complaint Management System. The system now supports comprehensive voice call handling across multiple telephony providers including Twilio, Knowlarity, and Exotel.

## 🎯 Supported Providers

### 1. Twilio
- **Webhook Base**: `/api/v1/webhook/voice/twilio`
- **Features**: Voice calls, transcription, recording, IVR, menu selection
- **Response Format**: TwiML (XML)

### 2. Knowlarity
- **Webhook Base**: `/api/v1/webhook/voice/knowlarity`
- **Features**: Voice calls, transcription, recording, IVR, menu selection
- **Response Format**: JSON

### 3. Exotel
- **Webhook Base**: `/api/v1/webhook/voice/exotel`
- **Features**: Voice calls, transcription, recording, IVR, menu selection
- **Response Format**: TwiML (XML)

## 📡 Webhook Endpoints

### Main Voice Webhook
```
POST /api/v1/webhook/voice/{provider}
```

**Supported providers**: `twilio`, `knowlarity`, `exotel`

**Purpose**: Handle incoming voice calls and generate appropriate responses

### Transcription Webhook
```
POST /api/v1/webhook/voice/{provider}/transcription
```

**Purpose**: Handle transcription callbacks from voice recordings

### Recording Webhook
```
POST /api/v1/webhook/voice/{provider}/recording
```

**Purpose**: Handle recording callbacks and process audio files

### IVR Webhook
```
POST /api/v1/webhook/voice/{provider}/ivr
```

**Purpose**: Handle Interactive Voice Response selections

### Menu Webhook
```
POST /api/v1/webhook/voice/{provider}/menu
```

**Purpose**: Handle menu selection responses

## 🔧 Implementation Details

### 1. Provider-Specific Handlers

Each provider has dedicated handlers that:
- Process provider-specific data formats
- Generate appropriate responses (TwiML for Twilio/Exotel, JSON for Knowlarity)
- Handle errors and edge cases
- Integrate with the conversation manager and AI engine

### 2. Data Processing

The webhook handlers:
- Extract call information (caller, recipient, call ID, status)
- Determine brand ID based on phone number mapping
- Process voice recordings and transcriptions
- Handle IVR and menu selections
- Create tickets and manage conversations

### 3. Response Generation

**Twilio/Exotel Responses**:
- Generate TwiML (XML) responses
- Include voice prompts, recording instructions, and menu options
- Handle call transfers and status updates

**Knowlarity Responses**:
- Generate JSON responses
- Include text-to-speech instructions and menu options
- Handle call routing and status updates

## 📋 Webhook Data Formats

### Twilio Voice Call Data
```json
{
  "From": "+1234567890",
  "To": "+0987654321",
  "CallSid": "call_sid_123",
  "CallStatus": "ringing"
}
```

### Twilio Transcription Data
```json
{
  "CallSid": "call_sid_123",
  "TranscriptionText": "I have a complaint about your service",
  "TranscriptionStatus": "completed",
  "TranscriptionUrl": "https://api.twilio.com/transcriptions/TR123"
}
```

### Twilio Recording Data
```json
{
  "CallSid": "call_sid_123",
  "RecordingUrl": "https://api.twilio.com/recordings/RE123",
  "RecordingDuration": "30",
  "RecordingStatus": "completed"
}
```

### Knowlarity Voice Call Data
```json
{
  "from": "+919876543210",
  "to": "+911800123456",
  "call_id": "knowlarity_call_123",
  "status": "ringing"
}
```

### Exotel Voice Call Data
```json
{
  "From": "+919876543210",
  "To": "+911800123456",
  "CallSid": "exotel_call_123",
  "CallStatus": "ringing"
}
```

## 🎯 IVR Menu Options

All providers support the following IVR menu:

1. **Press 1**: Lodge a complaint
2. **Press 2**: Check complaint status
3. **Press 3**: Speak to agent
4. **Press 4**: Hear options again

### Menu Flow

1. **Lodge a complaint**:
   - Records user's complaint
   - Transcribes the recording
   - Creates a ticket
   - Provides confirmation

2. **Check complaint status**:
   - Prompts for ticket number
   - Retrieves ticket status
   - Provides status update

3. **Speak to agent**:
   - Transfers call to support number
   - Handles transfer status
   - Provides fallback message

4. **Hear options again**:
   - Repeats the menu options
   - Allows user to make selection

## 🔌 Integration Points

### 1. Conversation Manager
- Manages conversation state and context
- Handles returning user recognition
- Maintains conversation history

### 2. AI Engine
- Analyzes voice transcriptions
- Classifies complaints and extracts details
- Determines sentiment and urgency

### 3. Ticket Management
- Creates tickets from voice complaints
- Updates ticket status based on IVR selections
- Manages ticket lifecycle

### 4. Brand Management
- Determines brand ID from phone number
- Applies brand-specific configurations
- Routes calls to appropriate brand

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

### 1. Call Metrics
- Call duration tracking
- Success/failure rates
- Provider performance comparison

### 2. Quality Metrics
- Transcription accuracy
- User satisfaction ratings
- Resolution times

### 3. Error Tracking
- Failed webhook attempts
- Provider-specific errors
- System performance issues

## 🚀 Configuration

### Environment Variables
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Knowlarity Configuration
KNOWLARITY_API_KEY=your_knowlarity_api_key
KNOWLARITY_API_SECRET=your_knowlarity_api_secret
KNOWLARITY_PHONE_NUMBER=+911800123456

# Exotel Configuration
EXOTEL_SID=your_exotel_sid
EXOTEL_TOKEN=your_exotel_token
EXOTEL_PHONE_NUMBER=+911800123456

# Support Configuration
SUPPORT_PHONE_NUMBER=+1234567890
```

### Webhook URLs
Configure these webhook URLs in your telephony provider dashboard:

**Twilio**:
- Voice: `https://your-domain.com/api/v1/webhook/voice/twilio`
- Transcription: `https://your-domain.com/api/v1/webhook/voice/twilio/transcription`
- Recording: `https://your-domain.com/api/v1/webhook/voice/twilio/recording`

**Knowlarity**:
- Voice: `https://your-domain.com/api/v1/webhook/voice/knowlarity`
- Transcription: `https://your-domain.com/api/v1/webhook/voice/knowlarity/transcription`
- Recording: `https://your-domain.com/api/v1/webhook/voice/knowlarity/recording`

**Exotel**:
- Voice: `https://your-domain.com/api/v1/webhook/voice/exotel`
- Transcription: `https://your-domain.com/api/v1/webhook/voice/exotel/transcription`
- Recording: `https://your-domain.com/api/v1/webhook/voice/exotel/recording`

## 🧪 Testing

### Test Script
Run the comprehensive test script:
```bash
python test_phone_call_webhooks.py
```

### Manual Testing
1. **Twilio Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/voice/twilio" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=+1234567890&To=+0987654321&CallSid=test_123&CallStatus=ringing"
   ```

2. **Knowlarity Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/voice/knowlarity" \
        -H "Content-Type: application/json" \
        -d '{"from": "+919876543210", "to": "+911800123456", "call_id": "test_123", "status": "ringing"}'
   ```

3. **Exotel Testing**:
   ```bash
   curl -X POST "https://your-domain.com/api/v1/webhook/voice/exotel" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "From=+919876543210&To=+911800123456&CallSid=test_123&CallStatus=ringing"
   ```

## 🔄 Workflow Examples

### Complete Voice Complaint Flow

1. **User calls toll-free number**
2. **System answers with welcome message**
3. **User selects "Lodge a complaint" (presses 1)**
4. **System prompts for complaint description**
5. **User records complaint (up to 60 seconds)**
6. **System transcribes recording**
7. **AI analyzes transcription and creates ticket**
8. **System confirms ticket creation**
9. **Call ends with satisfaction rating request**

### Status Check Flow

1. **User calls toll-free number**
2. **System answers with welcome message**
3. **User selects "Check complaint status" (presses 2)**
4. **System prompts for ticket number**
5. **User enters ticket number via keypad**
6. **System retrieves and announces ticket status**
7. **Call ends**

### Agent Transfer Flow

1. **User calls toll-free number**
2. **System answers with welcome message**
3. **User selects "Speak to agent" (presses 3)**
4. **System transfers call to support number**
5. **If agent available, call connects**
6. **If no agent available, system provides fallback message**

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
- Provide clear voice prompts
- Offer multiple menu options
- Handle edge cases gracefully

## 📈 Future Enhancements

### 1. Additional Providers
- Support for more telephony providers
- Provider-specific optimizations
- Unified provider interface

### 2. Advanced Features
- Multi-language IVR support
- Dynamic menu generation
- Advanced call routing

### 3. Analytics
- Real-time call analytics
- Performance dashboards
- Predictive call routing

## 🔗 Related Documentation

- [Multi-Channel Integration Guide](MULTI_CHANNEL_INTEGRATION_GUIDE.md)
- [AI Voice Integration Guide](AI_VOICE_INTEGRATION_GUIDE.md)
- [Interactive Complaint Collection Documentation](INTERACTIVE_COMPLAINT_COLLECTION_DOCUMENTATION.md)
- [Telephony Service Documentation](TELEPHONY_SERVICE_DOCUMENTATION.md)

---

**Note**: This implementation provides comprehensive phone call webhook support across multiple providers, ensuring seamless voice complaint collection and management for the Brand Complaint Management System. 