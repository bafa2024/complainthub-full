# Contextual Follow-Ups and Session Continuity Documentation

## Overview

The Contextual Follow-Ups and Session Continuity feature provides advanced conversation management capabilities that go beyond simple single-turn Q&A. This system maintains persistent conversation sessions, understands context across multiple interactions, and provides intelligent follow-up responses based on conversation history.

## Key Features

### 1. Persistent Session Management
- **Session Creation**: Each conversation gets a unique session ID
- **Session Persistence**: All conversation data is stored in the database
- **Session Resumption**: Users can return to previous conversations
- **Session Context**: Maintains context across multiple turns

### 2. Contextual Understanding
- **Conversation History**: Analyzes previous messages in the session
- **Context Extraction**: Identifies key information from conversation
- **Follow-up Detection**: Recognizes when users are responding to questions
- **Escalation Detection**: Identifies when issues are being repeated or escalated

### 3. Intelligent Follow-Ups
- **Brand-Specific Templates**: Customizable follow-up questions per brand
- **Context-Aware Responses**: Responses that reference previous conversation
- **Missing Information Detection**: Identifies what information is still needed
- **Progressive Information Gathering**: Builds complete understanding step by step

### 4. Session Continuity
- **Cross-Session Memory**: Remembers user preferences and previous issues
- **Resumption Logic**: Smart greetings when users return to conversations
- **Context Summarization**: Provides summaries of ongoing conversations
- **Status Tracking**: Tracks conversation status (active, completed, abandoned)

## Architecture

### Database Models

#### ConversationSession
```python
class ConversationSession(Base):
    __tablename__ = "conversation_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=True)
    channel = Column(String, nullable=False)  # web, telegram, whatsapp, etc.
    language = Column(String, default="en")
    status = Column(String, default="active")  # active, completed, abandoned
    context_summary = Column(Text, nullable=True)  # AI-generated summary
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### ConversationTurn
```python
class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    turn_number = Column(Integer, nullable=False)  # Sequential turn number
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    content_type = Column(String, default="text")  # text, voice, image, file
    ai_analysis = Column(JSON, nullable=True)  # Store AI analysis
    intent_detected = Column(String, nullable=True)
    entities_extracted = Column(JSON, nullable=True)  # Named entities
    sentiment_score = Column(Float, nullable=True)
    urgency_level = Column(String, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_type = Column(String, nullable=True)  # clarification, details, confirmation
    response_effectiveness = Column(Float, nullable=True)  # User satisfaction score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

#### SessionContext
```python
class SessionContext(Base):
    __tablename__ = "session_contexts"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("conversation_sessions.id"), nullable=False)
    context_type = Column(String, nullable=False)  # user_preferences, issue_details, etc.
    context_key = Column(String, nullable=False)
    context_value = Column(JSON, nullable=False)
    confidence_score = Column(Float, default=1.0)
    source_turn = Column(Integer, nullable=True)  # Which turn this context was extracted from
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### FollowUpTemplate
```python
class FollowUpTemplate(Base):
    __tablename__ = "follow_up_templates"
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    trigger_intent = Column(String, nullable=False)  # complaint, feedback, support, etc.
    trigger_urgency = Column(String, nullable=True)  # low, medium, high, critical
    trigger_entities = Column(JSON, nullable=True)  # Required entities to trigger
    follow_up_type = Column(String, nullable=False)  # clarification, details, confirmation, resolution
    template_text = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)  # Template variables like {user_name}
    language = Column(String, default="en")
    priority = Column(Integer, default=1)  # Higher priority templates are used first
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Core Components

#### ConversationManager
The main class that handles all conversation logic:

```python
class ConversationManager:
    def __init__(self, db: Session, ai_engine: AIEngine):
        self.db = db
        self.ai_engine = ai_engine
        self.max_context_turns = 10  # Number of recent turns to include in context

    def process_message(self, session_id: str, user_message: str, brand_id: int, 
                       channel: str, language: str = "en", user_id: Optional[int] = None) -> Dict[str, Any]:
        """Main entry point to process an incoming user message with contextual follow-ups."""
        
    def get_conversation_history(self, session_id: str, brand_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        
    def resume_conversation(self, session_id: str, brand_id: int) -> Dict[str, Any]:
        """Resume an existing conversation."""
        
    def close_conversation(self, session_id: str, brand_id: int, reason: str = "completed") -> bool:
        """Close a conversation session."""
```

#### Enhanced AIEngine
Extended with context-aware analysis:

```python
def analyze_text_with_context(self, text: str, context: str = "", brand_id: Optional[int] = None) -> Dict[str, Any]:
    """Analyze text with conversation context for enhanced understanding."""
    
def _assess_severity_with_context(self, text: str, sentiment_analysis: Dict[str, Any], context: str) -> Dict[str, Any]:
    """Assess severity with conversation context."""
    
def _generate_contextual_insights(self, text: str, context: str, intent_analysis: Dict[str, Any], 
                                sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate insights based on conversation context."""
    
def _analyze_follow_up_needs(self, text: str, context: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze if follow-up questions are needed."""
```

## API Endpoints

### Conversation Management

#### Process Message
```http
POST /conversation/process-message
Content-Type: application/json

{
    "session_id": "string",
    "message": "string",
    "brand_id": "integer",
    "channel": "string",
    "language": "string",
    "user_id": "integer (optional)"
}
```

#### Get Conversation History
```http
GET /conversation/session/{session_id}/history?brand_id={brand_id}&limit={limit}
```

#### Resume Conversation
```http
POST /conversation/session/{session_id}/resume?brand_id={brand_id}
```

#### Close Conversation
```http
DELETE /conversation/session/{session_id}/close?brand_id={brand_id}&reason={reason}
```

#### Get Session Context
```http
GET /conversation/session/{session_id}/context?brand_id={brand_id}
```

### Follow-Up Templates

#### Create Follow-Up Template
```http
POST /conversation/brand/{brand_id}/follow-up-templates
Content-Type: application/json

{
    "trigger_intent": "string",
    "trigger_urgency": "string (optional)",
    "trigger_entities": "object (optional)",
    "follow_up_type": "string",
    "template_text": "string",
    "variables": "array (optional)",
    "language": "string",
    "priority": "integer"
}
```

#### Get Follow-Up Templates
```http
GET /conversation/brand/{brand_id}/follow-up-templates?trigger_intent={intent}&follow_up_type={type}&language={lang}
```

#### Update Follow-Up Template
```http
PUT /conversation/follow-up-templates/{template_id}
Content-Type: application/json

{
    "template_text": "string",
    "priority": "integer",
    "is_active": "boolean"
}
```

#### Delete Follow-Up Template
```http
DELETE /conversation/follow-up-templates/{template_id}
```

### Analytics and Statistics

#### Get Active Sessions
```http
GET /conversation/brand/{brand_id}/active-sessions?limit={limit}
```

#### Analyze Message with Context
```http
POST /conversation/brand/{brand_id}/analyze-context
Content-Type: application/json

{
    "message": "string",
    "context": "string (optional)",
    "session_id": "string (optional)"
}
```

#### Get Conversation Statistics
```http
GET /conversation/brand/{brand_id}/conversation-stats?days={days}
```

## Usage Examples

### Basic Conversation Flow

```python
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine

# Initialize
ai_engine = AIEngine()
conversation_manager = ConversationManager(db, ai_engine)

# Start conversation
session_id = "user_123_session_456"
result1 = conversation_manager.process_message(
    session_id=session_id,
    user_message="I have a complaint about your service",
    brand_id=1,
    channel="web",
    language="en"
)

print(result1['message'])
# Output: "I understand your concern and I'm here to help resolve this issue. 
# Could you please provide your order number or reference number?"

# User provides order number
result2 = conversation_manager.process_message(
    session_id=session_id,
    user_message="My order number is 12345",
    brand_id=1,
    channel="web",
    language="en"
)

print(result2['message'])
# Output: "Thank you for providing the order number: 12345. 
# Could you please tell me which product or service this is about?"
```

### Follow-Up Template Management

```python
# Create a follow-up template
template_data = {
    "trigger_intent": "complaint",
    "follow_up_type": "details",
    "template_text": "Could you please provide your order number?",
    "language": "en",
    "priority": 1
}

# API call to create template
response = requests.post(
    f"/conversation/brand/{brand_id}/follow-up-templates",
    json=template_data
)
```

### Session Resumption

```python
# Resume a conversation after user returns
resume_result = conversation_manager.resume_conversation(session_id, brand_id)

print(resume_result['message'])
# Output: "Welcome back! I see we were discussing: Issue: complaint | Urgency: medium | Order: 12345. 
# How can I help you further?"
```

## Context Analysis Features

### 1. Follow-Up Detection
The system can detect when a user is responding to a previous question:

```python
# Bot asks: "Could you please provide your order number?"
# User responds: "12345"
# System detects this as a follow-up response and acknowledges the information
```

### 2. Repeated Issue Detection
Identifies when users mention the same issue multiple times:

```python
# Turn 1: "I have a complaint about delivery"
# Turn 3: "I'm still having the same delivery problem"
# System detects repetition and escalates response
```

### 3. Escalation Detection
Recognizes when users are becoming frustrated:

```python
# User message: "This is ridiculous! I want to speak to a manager!"
# System detects escalation and provides appropriate response
```

### 4. Context Summarization
Maintains summaries of conversation context:

```python
context_summary = "Issue: complaint | Urgency: medium | Order: 12345 | Product: smartphone"
```

## Configuration

### Environment Variables
```bash
# Database configuration
DATABASE_URL=sqlite:///voicebot.db

# AI Engine configuration
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key

# Session configuration
MAX_CONTEXT_TURNS=10
SESSION_TIMEOUT_HOURS=24
```

### Brand-Specific Settings
```python
# Follow-up template configuration
follow_up_config = {
    "max_templates_per_intent": 5,
    "default_language": "en",
    "auto_escalation_threshold": 3,  # Number of repetitions before escalation
    "context_retention_days": 30
}
```

## Performance Considerations

### Database Optimization
- Indexes on frequently queried fields (session_id, brand_id, created_at)
- Partitioning for large conversation tables
- Regular cleanup of old sessions

### Memory Management
- Limit context turns to prevent memory bloat
- Cache frequently accessed session data
- Implement session timeout and cleanup

### Scalability
- Horizontal scaling with session affinity
- Redis caching for active sessions
- Async processing for non-critical operations

## Security and Privacy

### Data Protection
- Encrypt sensitive conversation data
- Implement data retention policies
- GDPR compliance for user data

### Access Control
- Brand-specific data isolation
- User permission validation
- Audit logging for conversation access

### Session Security
- Secure session ID generation
- Session timeout and cleanup
- Protection against session hijacking

## Monitoring and Analytics

### Key Metrics
- Active sessions count
- Average conversation length
- Follow-up success rate
- Escalation frequency
- Session completion rate

### Health Checks
- Database connection status
- AI engine availability
- Template loading status
- Session cleanup job status

## Troubleshooting

### Common Issues

#### Session Not Found
```python
# Check if session exists
session = db.query(ConversationSession).filter(
    ConversationSession.session_id == session_id
).first()

if not session:
    # Create new session or handle error
    pass
```

#### Context Not Persisting
```python
# Verify context storage
context = conversation_manager._get_session_context(session.id)
if not context:
    # Check database connection and permissions
    pass
```

#### Follow-Up Templates Not Working
```python
# Check template configuration
templates = conversation_manager._get_follow_up_templates(brand_id, intent, urgency)
if not templates:
    # Verify template creation and activation
    pass
```

### Debug Mode
Enable debug logging for detailed conversation flow:

```python
import logging
logging.getLogger('app.core.conversation_manager').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
1. **Multi-language Context Support**: Context analysis in multiple languages
2. **Voice Context Integration**: Context from voice conversations
3. **Advanced Escalation Logic**: Machine learning-based escalation prediction
4. **Context Sharing**: Share context between different channels
5. **Predictive Follow-ups**: AI-generated follow-up questions

### Integration Opportunities
1. **CRM Integration**: Sync conversation context with CRM systems
2. **Analytics Dashboard**: Real-time conversation analytics
3. **A/B Testing**: Test different follow-up strategies
4. **Machine Learning**: Improve context understanding over time

## Conclusion

The Contextual Follow-Ups and Session Continuity feature provides a robust foundation for intelligent conversation management. It enables the system to maintain context across multiple interactions, provide relevant follow-up questions, and deliver a more natural and effective user experience.

The implementation is production-ready with comprehensive error handling, security measures, and monitoring capabilities. The modular design allows for easy extension and customization to meet specific brand requirements. 