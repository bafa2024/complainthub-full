# Follow-up Automation System Guide

## Overview

The Follow-up Automation System is a comprehensive solution that automatically handles post-resolution customer follow-ups according to the SRS requirements. It implements the complete workflow described in the specification, including automated outbound calls, WhatsApp messages, email notifications, and intelligent response handling.

## 🎯 Key Features Implemented

### ✅ Complete SRS Compliance
- **24-hour follow-up scheduling**: Automatic follow-up 24 hours after ticket resolution
- **Multi-channel follow-ups**: Voice calls, WhatsApp, email, Telegram, WebChat
- **48-hour auto-closure**: Automatic ticket closure after 48 hours of no response
- **Response handling**: Process user confirmations and reopen tickets if needed
- **Satisfaction rating**: Collect 0-5 ratings from customers
- **Brand notifications**: Alert brands when tickets are reopened

### ✅ Advanced Automation
- **Celery background tasks**: Reliable scheduling and execution
- **Retry mechanism**: Exponential backoff for failed follow-ups
- **Multi-channel fallback**: Automatic fallback to secondary channels
- **Intelligent routing**: Channel-specific follow-up strategies
- **Comprehensive logging**: Full audit trail of all follow-up activities

## 🏗️ Architecture

### Core Components

1. **FollowUpService** (`backend/app/services/followup_service.py`)
   - Main service for follow-up orchestration
   - Handles scheduling, execution, and response processing
   - Manages multi-channel communication

2. **Celery Tasks** (`backend/app/tasks/followup_tasks.py`)
   - Background task execution
   - Scheduled follow-up processing
   - Retry and cleanup operations

3. **Database Models** (`backend/app/models.py`)
   - `FollowUpLog`: Tracks all follow-up activities
   - Enhanced `Ticket` model with follow-up relationships

4. **API Endpoints** (`backend/app/api/v1/endpoints/followup.py`)
   - RESTful API for follow-up management
   - Webhook endpoints for response handling
   - Statistics and reporting endpoints

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install celery redis
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_ALWAYS_EAGER=false

# Follow-up Configuration
FOLLOW_UP_DELAY_HOURS=24
SECONDARY_FOLLOW_UP_DELAY_HOURS=4
AUTO_CLOSE_HOURS=48
MAX_FOLLOW_UP_RETRIES=3
FOLLOW_UP_RETENTION_DAYS=90
```

### 3. Start Redis Server

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

### 4. Start Celery Workers

```bash
# Start Celery worker
celery -A app.celery_app worker --loglevel=info

# Start Celery beat scheduler (in another terminal)
celery -A app.celery_app beat --loglevel=info
```

### 5. Run Database Migrations

```bash
# Create new tables for follow-up system
python init_db.py
```

## 📋 API Endpoints

### Follow-up Management

#### Schedule Follow-up
```http
POST /api/v1/followup/schedule/{ticket_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "delay_hours": 24
}
```

#### Execute Follow-up
```http
POST /api/v1/followup/execute/{follow_up_id}
Authorization: Bearer <token>
```

#### List Follow-ups
```http
GET /api/v1/followup/list?ticket_id=123&status=completed&limit=50
Authorization: Bearer <token>
```

#### Get Follow-up Statistics
```http
GET /api/v1/followup/stats?brand_id=1&days=30
Authorization: Bearer <token>
```

#### Cancel Follow-up
```http
DELETE /api/v1/followup/{follow_up_id}
Authorization: Bearer <token>
```

### Response Handling

#### Handle Follow-up Response
```http
POST /api/v1/followup/response
Content-Type: application/json

{
  "follow_up_id": 123,
  "response": "resolved",
  "rating": 5
}
```

#### Voice Follow-up Webhook
```http
POST /api/v1/followup/webhook/voice/follow-up-response
Content-Type: application/x-www-form-urlencoded

Digits=1&CallSid=call_123
```

## 🔄 Workflow Implementation

### 1. Ticket Resolution Trigger

When a ticket is marked as resolved:

```python
# In tickets_extended.py
if status == "resolved":
    followup_service = FollowUpService(db)
    followup_service.schedule_follow_up(
        ticket_id=ticket_id,
        delay_hours=24
    )
```

### 2. Follow-up Scheduling

The system automatically schedules follow-ups:

```python
def schedule_follow_up(self, ticket_id: int, delay_hours: int = 24):
    # Calculate follow-up time
    follow_up_time = datetime.utcnow() + timedelta(hours=delay_hours)
    
    # Create follow-up log
    follow_up = FollowUpLog(
        ticket_id=ticket_id,
        scheduled_time=follow_up_time,
        status="scheduled",
        follow_up_type="resolution_confirmation"
    )
    
    # Schedule Celery task
    self._schedule_celery_task(follow_up.id, follow_up_time)
```

### 3. Multi-Channel Execution

Follow-ups are executed based on the original channel:

```python
def _execute_channel_follow_up(self, follow_up, ticket, brand):
    if follow_up.channel == "voice":
        return self._execute_voice_follow_up(follow_up, message, ticket)
    elif follow_up.channel == "whatsapp":
        return self._execute_whatsapp_follow_up(follow_up, message, ticket)
    elif follow_up.channel == "email":
        return self._execute_email_follow_up(follow_up, message, ticket)
    # ... other channels
```

### 4. Response Processing

User responses are processed intelligently:

```python
def handle_follow_up_response(self, follow_up_id: int, response: str, rating: int = None):
    if response.lower() in ["resolved", "1", "yes"]:
        # Mark ticket as confirmed resolved
        ticket.status = "confirmed_resolved"
    elif response.lower() in ["not_resolved", "2", "no"]:
        # Reopen ticket and notify brand
        ticket.status = "reopened"
        self._notify_brand_reopening(ticket)
```

### 5. Auto-closure

Tickets are automatically closed after 48 hours:

```python
def auto_close_ticket(self, ticket_id: int):
    if (datetime.utcnow() - ticket.updated_at).total_seconds() > 48 * 3600:
        ticket.status = "auto_closed"
        ticket.auto_closed = True
```

## 🎯 Channel-Specific Features

### Voice Follow-ups
- **TwiML Generation**: Dynamic voice prompts
- **IVR Integration**: Press 1 for resolved, 2 for not resolved
- **Rating Collection**: Press 3 for rating collection
- **Fallback**: WhatsApp if call fails

### WhatsApp Follow-ups
- **Quick Reply Buttons**: Pre-defined response options
- **Template Messages**: Brand-specific templates
- **Media Support**: Images and documents
- **Fallback**: Email if WhatsApp fails

### Email Follow-ups
- **HTML Templates**: Professional email templates
- **Action Buttons**: Direct links for responses
- **Rating Collection**: Star rating system
- **Branding**: Customizable templates

### Telegram Follow-ups
- **Inline Keyboards**: Interactive response buttons
- **Rich Media**: Images, videos, documents
- **Callback Queries**: Handle button presses

### WebChat Follow-ups
- **Real-time Messages**: WebSocket notifications
- **In-app Actions**: Direct response buttons
- **Session Management**: Persistent chat sessions

## 📊 Monitoring and Analytics

### Follow-up Statistics

```python
def get_follow_up_stats(self, brand_id: int = None, days: int = 30):
    return {
        "total_follow_ups": 150,
        "successful": 120,
        "failed": 15,
        "pending": 15,
        "success_rate": 80.0,
        "channels": {
            "whatsapp": {"total": 80, "successful": 70, "failed": 10},
            "email": {"total": 50, "successful": 40, "failed": 5},
            "voice": {"total": 20, "successful": 10, "failed": 0}
        }
    }
```

### Key Metrics
- **Success Rate**: Percentage of successful follow-ups
- **Channel Performance**: Success rates by channel
- **Response Time**: Time to first response
- **Resolution Rate**: Percentage of confirmed resolutions
- **Satisfaction Scores**: Average customer ratings

## 🔧 Configuration Options

### Follow-up Timing
```python
FOLLOW_UP_DELAY_HOURS = 24  # Primary follow-up delay
SECONDARY_FOLLOW_UP_DELAY_HOURS = 4  # Secondary follow-up delay
AUTO_CLOSE_HOURS = 48  # Auto-closure delay
```

### Retry Settings
```python
MAX_FOLLOW_UP_RETRIES = 3  # Maximum retry attempts
FOLLOW_UP_RETENTION_DAYS = 90  # Log retention period
```

### Channel Priorities
```python
CHANNEL_PRIORITIES = {
    "voice": 1,
    "whatsapp": 2,
    "telegram": 3,
    "email": 4,
    "webchat": 5
}
```

## 🧪 Testing

### Run Test Script
```bash
cd backend
python test_followup_automation.py
```

### Manual Testing
```bash
# Test follow-up scheduling
curl -X POST "http://localhost:8000/api/v1/followup/schedule/123" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"delay_hours": 0}'

# Test follow-up execution
curl -X POST "http://localhost:8000/api/v1/followup/execute/456" \
  -H "Authorization: Bearer <token>"

# Test response handling
curl -X POST "http://localhost:8000/api/v1/followup/response" \
  -H "Content-Type: application/json" \
  -d '{"follow_up_id": 456, "response": "resolved", "rating": 5}'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Celery Tasks Not Running
```bash
# Check Celery worker status
celery -A app.celery_app inspect active

# Check Redis connection
redis-cli ping
```

#### 2. Follow-ups Not Scheduled
- Verify ticket status is "resolved"
- Check Celery beat scheduler is running
- Review database for follow-up log entries

#### 3. Channel Failures
- Verify API credentials for each channel
- Check webhook URLs are accessible
- Review channel-specific error logs

#### 4. Auto-closure Not Working
- Verify Celery beat scheduler is running
- Check auto-close task is scheduled
- Review ticket timestamps

### Debug Commands
```bash
# Check Celery task status
celery -A app.celery_app inspect scheduled

# View Celery logs
tail -f celery.log

# Check Redis queue
redis-cli llen celery

# Test Celery connection
celery -A app.celery_app inspect ping
```

## 📈 Performance Optimization

### Database Optimization
- Index on `scheduled_time` for efficient querying
- Partition follow-up logs by date
- Archive old follow-up logs

### Celery Optimization
- Use multiple workers for high throughput
- Configure task routing for different channels
- Implement task result backend for monitoring

### Channel Optimization
- Implement rate limiting per channel
- Use connection pooling for external APIs
- Cache channel configurations

## 🔒 Security Considerations

### Data Protection
- Encrypt sensitive follow-up data
- Implement GDPR compliance for data retention
- Secure webhook endpoints

### Access Control
- Role-based access to follow-up management
- Audit logging for all follow-up activities
- IP whitelisting for admin functions

### API Security
- Rate limiting on follow-up endpoints
- Input validation for all parameters
- Secure token-based authentication

## 🎉 Success Metrics

The follow-up automation system is considered successful when:

1. **95%+ Follow-up Success Rate**: Most follow-ups are delivered successfully
2. **80%+ Response Rate**: Customers respond to follow-ups
3. **90%+ Resolution Confirmation**: Most resolved tickets are confirmed
4. **<2% Reopening Rate**: Low rate of ticket reopenings
5. **4.0+ Average Rating**: High customer satisfaction scores

## 📚 Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [Twilio TwiML Reference](https://www.twilio.com/docs/voice/twiml)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Celery and Redis logs
3. Test with the provided test script
4. Consult the API documentation
5. Check channel-specific configuration

The Follow-up Automation System is now fully implemented and ready for production use, providing complete compliance with the SRS requirements for automated customer follow-ups. 