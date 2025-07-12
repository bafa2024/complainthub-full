# AI & Voice Processing Integration Guide

This guide covers the enhanced AI and Voice Processing features implemented in the Brand Complaint Management System.

## 🎯 Overview

The AI & Voice Processing integration provides:

- **Advanced AI Analysis**: OpenAI ChatGPT integration with Google Cloud Natural Language
- **Speech-to-Text**: Deepgram integration with sentiment analysis
- **Text-to-Speech**: Google Cloud TTS with unique voice per user
- **Multilingual Support**: Support for 30+ languages
- **Self-Learning**: Brand-specific knowledge accumulation
- **Sentiment Analysis**: Real-time sentiment and toxicity detection

## 🚀 Features Implemented

### 1. Enhanced AI Engine (`backend/app/core/ai_engine.py`)

**Key Features:**
- OpenAI ChatGPT integration for natural conversations
- Google Cloud Natural Language for advanced sentiment analysis
- Content classification and entity extraction
- Toxicity detection and abuse flagging
- Language detection and translation support

**Usage:**
```python
from app.core.ai_engine import AIEngine

ai_engine = AIEngine()

# Analyze text with full AI processing
analysis = ai_engine.classify_intent_and_extract_details("I'm very angry about poor service!")

# Generate follow-up questions
question = ai_engine.generate_follow_up_question(conversation_history)

# Detect language
language = ai_engine.detect_language("Hello world")
```

### 2. Deepgram Speech-to-Text (`backend/app/services/speech/deepgram.py`)

**Key Features:**
- Real-time audio transcription
- Built-in sentiment analysis
- Language detection
- Support for 30+ languages
- Word-level timing and confidence scores

**Usage:**
```python
from app.services.speech.deepgram import deepgram_service

# Transcribe audio file
result = await deepgram_service.transcribe_audio_file("audio.wav", "en")

# Transcribe audio bytes
result = await deepgram_service.transcribe_audio_bytes(audio_bytes, "hi")

# Get supported languages
languages = deepgram_service.get_supported_languages()
```

### 3. Text-to-Speech Service (`backend/app/services/speech/tts.py`)

**Key Features:**
- Google Cloud Text-to-Speech integration
- Unique voice assignment per user
- Multiple language support
- Voice statistics and management
- Audio file generation and storage

**Usage:**
```python
from app.services.speech.tts import tts_service

# Assign voice to user
voice_name = tts_service.assign_voice_to_user("user123", "female", "en")

# Synthesize speech
result = await tts_service.synthesize_speech("Hello world", "user123", "en")

# Get available voices
voices = tts_service.get_available_voices("en")
```

### 4. Enhanced Conversation Manager (`backend/app/core/conversation_manager.py`)

**Key Features:**
- Self-learning capabilities
- Returning user recognition
- Multilingual conversation support
- Brand-specific knowledge accumulation
- Conversation statistics and analytics

**Usage:**
```python
from app.core.conversation_manager import ConversationManager

conversation_manager = ConversationManager(db, ai_engine)

# Process message with language support
response = conversation_manager.process_message(
    session_id="user123",
    user_message="Hello, I have a complaint",
    brand_id=1,
    channel="webchat",
    language="en"
)

# Get conversation statistics
stats = conversation_manager.get_conversation_stats()
```

## 🔧 API Endpoints

### Voice Processing Endpoints

#### 1. Upload Voice Complaint
```http
POST /api/v1/tickets_extended/voice
Content-Type: multipart/form-data

Parameters:
- audio: Audio file (WAV, MP3, etc.)
- metadata: JSON string with complaint details
```

#### 2. Transcribe Audio Only
```http
POST /api/v1/tickets_extended/voice/transcribe
Content-Type: multipart/form-data

Parameters:
- audio: Audio file
- language: Language code (default: "en")
```

#### 3. Analyze Voice Sentiment
```http
POST /api/v1/tickets_extended/voice/analyze
Content-Type: multipart/form-data

Parameters:
- audio: Audio file
- language: Language code (default: "en")
```

#### 4. Get Supported Languages
```http
GET /api/v1/tickets_extended/voice/languages
```

### Chat Endpoints

#### 1. Send Chat Message
```http
POST /api/v1/chat/send
Content-Type: application/json

{
  "message": "User message",
  "sessionId": "unique_session_id"
}
```

## 🌍 Multilingual Support

### Supported Languages

The system supports 30+ languages including:

- **English (en)**: Primary language
- **Hindi (hi)**: Indian regional language
- **Spanish (es)**: Spanish
- **French (fr)**: French
- **German (de)**: German
- **And 25+ more languages**

### Language Detection

The system automatically detects the language of:
- Text messages
- Voice recordings
- User input

### Translation Support

Text can be translated between supported languages using Google Cloud Translate.

## 🧠 Self-Learning Features

### Brand-Specific Knowledge

The system learns from each brand's interactions:

- **Common Questions**: Frequently asked questions are identified and stored
- **Resolution Patterns**: Successful resolution strategies are tracked
- **User Preferences**: Individual user preferences and history
- **Context Awareness**: Brand-specific context and terminology

### Knowledge Accumulation

```python
# Self-learning data structure
SELF_LEARNING_STORE = {
    "brand_knowledge": {
        "brand_id": {
            "common_questions": {},
            "resolution_patterns": {},
            "context": "",
            "ticket_count": 0
        }
    }
}
```

## 📊 Sentiment Analysis

### Deepgram Sentiment

- **Real-time Analysis**: Sentiment analysis during transcription
- **Score Range**: -1.0 (very negative) to +1.0 (very positive)
- **Labels**: positive, neutral, negative

### Google Cloud Natural Language

- **Advanced Analysis**: Entity recognition, content classification
- **Toxicity Detection**: Abuse and profanity detection
- **Entity Extraction**: Names, places, organizations, etc.

## 🎤 Voice Features

### Unique Voice per User

Each user gets assigned a consistent voice:

- **Voice Assignment**: Automatic assignment on first interaction
- **Voice Persistence**: Voice remains consistent across sessions
- **Voice Management**: Users can change their assigned voice
- **Statistics**: Voice usage analytics and distribution

### Voice Profiles

```python
voice_profiles = {
    "male": [
        {"name": "en-US-Standard-A", "language": "en", "gender": "male"},
        {"name": "en-US-Wavenet-A", "language": "en", "gender": "male"},
        # ... more voices
    ],
    "female": [
        {"name": "en-US-Standard-B", "language": "en", "gender": "female"},
        {"name": "en-US-Wavenet-B", "language": "en", "gender": "female"},
        # ... more voices
    ]
}
```

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```env
# AI Services
OPENAI_API_KEY=your_openai_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Google Cloud credentials file
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### API Keys Setup

#### 1. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get API key
3. Add to environment variables

#### 2. Deepgram API Key
1. Visit [Deepgram Console](https://console.deepgram.com/)
2. Create account and get API key
3. Add to environment variables

#### 3. Google Cloud API Key
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable required APIs:
   - Natural Language API
   - Text-to-Speech API
   - Speech-to-Text API
   - Translate API
3. Create API key and add to environment variables

## 🧪 Testing

### Run Integration Tests

```bash
cd backend
python test_ai_voice_integration.py
```

### Test Individual Components

```python
# Test AI Engine
from app.core.ai_engine import AIEngine
ai_engine = AIEngine()
analysis = ai_engine.classify_intent_and_extract_details("Test message")

# Test Deepgram
from app.services.speech.deepgram import deepgram_service
result = await deepgram_service.transcribe_audio_file("test.wav", "en")

# Test TTS
from app.services.speech.tts import tts_service
result = await tts_service.synthesize_speech("Hello world", "user123", "en")
```

## 📈 Performance Optimization

### Caching

- **Conversation Cache**: In-memory conversation storage
- **Voice Assignment Cache**: User voice assignments
- **Language Detection Cache**: Cached language detection results

### Async Processing

- **Non-blocking Operations**: All AI and voice processing is async
- **Background Tasks**: Heavy processing runs in background
- **Queue Management**: Task queuing for high-load scenarios

## 🔒 Security Considerations

### Data Privacy

- **User Data Isolation**: Each brand's data is isolated
- **Voice Data Storage**: Audio files stored securely
- **API Key Security**: Environment variable protection
- **Data Encryption**: Sensitive data encrypted at rest

### Rate Limiting

- **API Rate Limits**: Respect external API rate limits
- **Request Throttling**: Implement request throttling
- **Error Handling**: Graceful fallback on API failures

## 🚨 Error Handling

### Fallback Mechanisms

- **OpenAI Fallback**: Fallback responses when OpenAI is unavailable
- **Deepgram Fallback**: Mock transcription when Deepgram fails
- **TTS Fallback**: Default voice when TTS service is down
- **Language Fallback**: Default to English when language detection fails

### Error Logging

All errors are logged with:
- Error details and stack traces
- Context information
- User and session identifiers
- Timestamp and severity levels

## 📚 Best Practices

### 1. API Key Management
- Use environment variables for API keys
- Rotate keys regularly
- Monitor API usage and costs

### 2. Audio Processing
- Use appropriate audio formats (WAV, MP3)
- Limit audio file sizes
- Implement audio quality checks

### 3. Conversation Management
- Set appropriate conversation timeouts
- Clean up old conversation data
- Monitor conversation quality

### 4. Performance Monitoring
- Monitor API response times
- Track error rates
- Monitor resource usage

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Self-Learning**
   - Machine learning model training
   - Predictive analytics
   - Automated response generation

2. **Enhanced Voice Features**
   - Voice cloning capabilities
   - Emotion detection in voice
   - Real-time voice analysis

3. **Advanced NLP**
   - Custom entity recognition
   - Intent classification training
   - Multi-language models

4. **Integration Enhancements**
   - CRM system integration
   - Analytics dashboard
   - Real-time monitoring

## 📞 Support

For issues and questions:

1. Check the logs in `backend/app.log`
2. Run the test script: `python test_ai_voice_integration.py`
3. Verify API keys and configuration
4. Check network connectivity to external services

## 📄 License

This AI & Voice Processing integration is part of the Brand Complaint Management System and follows the same licensing terms. 