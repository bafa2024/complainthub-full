# Scheduled Tasks and Background Jobs Documentation

## Overview

The ComplaintHub Bot system implements a comprehensive scheduled tasks and background job system using Celery and Redis. This system handles automated follow-ups, billing processing, notifications, and email outreach campaigns.

## Architecture

### Components

1. **Celery Worker**: Processes background tasks
2. **Celery Beat**: Schedules periodic tasks
3. **Redis**: Message broker and result backend
4. **Task Modules**: Organized by functionality
5. **Service Layer**: Business logic implementation

### Task Categories

- **Follow-up Tasks**: Automated customer follow-ups
- **Billing Tasks**: Credit deduction and payment processing
- **Notification Tasks**: Multi-channel notification delivery
- **Email Outreach Tasks**: Automated brand outreach campaigns

## Task Details

### 1. Follow-up Tasks (`followup_tasks.py`)

#### `check_pending_followups`
- **Schedule**: Every hour
- **Purpose**: Check for tickets that need follow-up after 24 hours
- **Features**:
  - Multi-channel delivery (voice, WhatsApp, email, Telegram)
  - Fallback channel handling
  - Response tracking and rating collection

#### `auto_close_expired_tickets`
- **Schedule**: Every 15 minutes
- **Purpose**: Auto-close tickets that haven't been resolved after 48 hours
- **Features**:
  - Automatic status updates
  - Notification to brand users
  - Analytics tracking

#### `retry_failed_followups`
- **Schedule**: Every hour at 30 minutes
- **Purpose**: Retry failed follow-up deliveries
- **Features**:
  - Exponential backoff retry
  - Channel fallback
  - Maximum retry limits

#### `cleanup_old_followups`
- **Schedule**: Daily at 2 AM UTC
- **Purpose**: Clean up old follow-up logs
- **Features**:
  - Configurable retention period
  - Database optimization
  - Audit trail preservation

### 2. Billing Tasks (`billing_tasks.py`)

#### `check_complaint_charges`
- **Schedule**: Daily at 2:15 AM UTC
- **Purpose**: Check for unresolved complaints that need charging after 24 hours
- **Features**:
  - Automated credit deduction
  - Low balance alerts
  - Transaction logging

#### `process_pending_charges`
- **Schedule**: Daily at 3 AM UTC
- **Purpose**: Process pending charges when brand balance is sufficient
- **Features**:
  - Balance validation
  - Batch processing
  - Error handling

#### `check_low_balance_brands`
- **Schedule**: Daily at 3:15 AM UTC
- **Purpose**: Alert brands with low credit balance
- **Features**:
  - Threshold-based alerts
  - Multi-channel notifications
  - Top-up suggestions

#### `process_subscription_renewals`
- **Schedule**: Daily at 3:30 AM UTC
- **Purpose**: Process subscription renewals
- **Features**:
  - Stripe integration
  - Automatic billing
  - Failed payment handling

#### `generate_monthly_billing_reports`
- **Schedule**: Monthly on 1st at 7 AM UTC
- **Purpose**: Generate comprehensive billing reports
- **Features**:
  - PDF report generation
  - Email delivery
  - Analytics integration

#### `cleanup_old_transactions`
- **Schedule**: Weekly on Sunday at 6:30 AM UTC
- **Purpose**: Clean up old transaction records
- **Features**:
  - Configurable retention
  - Data archiving
  - Compliance adherence

### 3. Notification Tasks (`notification_tasks.py`)

#### `send_pending_notifications`
- **Schedule**: Daily at 4 AM UTC
- **Purpose**: Send all pending notifications
- **Features**:
  - Multi-channel delivery
  - Priority-based processing
  - Rate limiting

#### `send_scheduled_notifications`
- **Schedule**: Daily at 4:15 AM UTC
- **Purpose**: Send scheduled notifications
- **Features**:
  - Time-based delivery
  - Timezone handling
  - Batch processing

#### `send_daily_digest`
- **Schedule**: Daily at 5 AM UTC
- **Purpose**: Send daily digest to brands
- **Features**:
  - Customizable content
  - Brand-specific data
  - Analytics integration

#### `send_weekly_reports`
- **Schedule**: Weekly on Sunday at 6 AM UTC
- **Purpose**: Send weekly performance reports
- **Features**:
  - Comprehensive analytics
  - Trend analysis
  - Actionable insights

#### `retry_failed_notifications`
- **Schedule**: Every hour at 15 minutes
- **Purpose**: Retry failed notification deliveries
- **Features**:
  - Exponential backoff
  - Channel fallback
  - Error tracking

#### `cleanup_old_notifications`
- **Schedule**: Daily at 2:30 AM UTC
- **Purpose**: Clean up old notification records
- **Features**:
  - Retention policy enforcement
  - Database optimization
  - Compliance adherence

#### `send_urgent_alerts`
- **Schedule**: Daily at 4:30 AM UTC
- **Purpose**: Send urgent system alerts
- **Features**:
  - Priority processing
  - Immediate delivery
  - Escalation handling

### 4. Email Outreach Tasks (`email_outreach_tasks.py`)

#### `discover_brand_contacts`
- **Trigger**: Manual or scheduled
- **Purpose**: Discover support contacts for brands through web scraping
- **Features**:
  - Web scraping automation
  - Contact validation
  - Rate limiting compliance

#### `send_outreach_campaign`
- **Trigger**: Manual or scheduled
- **Purpose**: Send outreach campaigns to brand support contacts
- **Features**:
  - Template-based emails
  - Personalization
  - Tracking and analytics

#### `send_bulk_outreach`
- **Trigger**: Manual or scheduled
- **Purpose**: Send bulk outreach to multiple brands
- **Features**:
  - Batch processing
  - Rate limiting
  - Progress tracking

#### `retry_failed_outreach`
- **Schedule**: Every hour at 30 minutes
- **Purpose**: Retry failed outreach emails
- **Features**:
  - Retry logic
  - Error tracking
  - Success monitoring

#### `generate_outreach_reports`
- **Schedule**: Daily at 5:15 AM UTC
- **Purpose**: Generate outreach analytics reports
- **Features**:
  - Performance metrics
  - Success rates
  - ROI analysis

#### `cleanup_old_outreach_logs`
- **Schedule**: Daily at 2:45 AM UTC
- **Purpose**: Clean up old outreach logs
- **Features**:
  - Retention policy
  - Database optimization
  - Compliance adherence

## Configuration

### Environment Variables

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_ALWAYS_EAGER=false

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=noreply@complainthubbot.com

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Celery Configuration

```python
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 hour
)
```

## Database Models

### EmailOutreachLog
- Tracks email outreach campaigns
- Stores contact information and delivery status
- Supports retry logic and analytics

### Subscription
- Manages brand subscriptions
- Tracks billing cycles and renewals
- Integrates with Stripe

### FollowUpLog
- Tracks follow-up execution
- Stores delivery status and responses
- Supports multi-channel delivery

### Notification
- Manages notification delivery
- Supports multiple channels
- Tracks delivery status

## Service Layer

### BillingService
- Handles credit deduction
- Manages transactions
- Integrates with Stripe

### NotificationService
- Multi-channel notification delivery
- Template management
- Rate limiting and compliance

### EmailOutreachService
- Web scraping for contact discovery
- Email template management
- Campaign tracking and analytics

### FollowUpService
- Multi-channel follow-up delivery
- Response tracking
- Fallback handling

## Monitoring and Maintenance

### Task Monitoring

```bash
# Check worker status
celery -A app.celery_app inspect ping

# Monitor active tasks
celery -A app.celery_app inspect active

# Monitor scheduled tasks
celery -A app.celery_app inspect scheduled

# View task statistics
celery -A app.celery_app inspect stats
```

### Log Management

- Task execution logs
- Error tracking and alerting
- Performance monitoring
- Resource usage tracking

### Health Checks

- Redis connection monitoring
- Database connection health
- External API status
- Task queue monitoring

## Error Handling

### Retry Logic
- Exponential backoff
- Maximum retry limits
- Channel fallback
- Error categorization

### Fallback Mechanisms
- Alternative delivery channels
- Graceful degradation
- Circuit breaker patterns
- Dead letter queues

### Monitoring and Alerting
- Task failure notifications
- Performance degradation alerts
- Resource usage warnings
- System health monitoring

## Performance Optimization

### Database Optimization
- Connection pooling
- Query optimization
- Index management
- Batch processing

### Resource Management
- Memory usage optimization
- CPU utilization monitoring
- Network efficiency
- Storage optimization

### Scalability
- Horizontal scaling
- Load balancing
- Task distribution
- Resource allocation

## Security Considerations

### Data Protection
- Encryption at rest and in transit
- Access control and authentication
- Audit logging
- GDPR compliance

### API Security
- Rate limiting
- Input validation
- Error handling
- Secure communication

### Infrastructure Security
- Network security
- Container security
- Secret management
- Vulnerability scanning

## Testing

### Unit Tests
- Individual task testing
- Service layer testing
- Model validation
- Error handling

### Integration Tests
- End-to-end workflow testing
- External API integration
- Database operations
- Task scheduling

### Performance Tests
- Load testing
- Stress testing
- Scalability testing
- Resource usage testing

## Deployment

### Production Setup
- Redis cluster configuration
- Celery worker scaling
- Monitoring and alerting
- Backup and recovery

### Docker Configuration
- Multi-container setup
- Volume management
- Network configuration
- Resource limits

### CI/CD Pipeline
- Automated testing
- Deployment automation
- Rollback procedures
- Environment management

## Troubleshooting

### Common Issues

1. **Redis Connection Failures**
   - Check Redis server status
   - Verify connection configuration
   - Monitor network connectivity

2. **Task Execution Failures**
   - Review task logs
   - Check external API status
   - Verify database connectivity

3. **Performance Issues**
   - Monitor resource usage
   - Check task queue length
   - Optimize database queries

4. **Scheduling Issues**
   - Verify Celery beat status
   - Check timezone configuration
   - Review task schedules

### Debug Commands

```bash
# Check Redis connection
redis-cli ping

# Monitor Celery tasks
celery -A app.celery_app events

# View task results
celery -A app.celery_app inspect reserved

# Check worker processes
ps aux | grep celery
```

## Future Enhancements

### Planned Features
- Machine learning integration
- Advanced analytics
- Real-time monitoring
- Automated scaling

### Performance Improvements
- Task optimization
- Database enhancements
- Caching strategies
- Resource optimization

### Security Enhancements
- Advanced authentication
- Encryption improvements
- Audit enhancements
- Compliance features

## Conclusion

The scheduled tasks and background job system provides a robust foundation for automated operations in the ComplaintHub Bot system. With comprehensive error handling, monitoring, and scalability features, it ensures reliable and efficient task execution across all system components.

For additional support or questions, please refer to the system documentation or contact the development team. 