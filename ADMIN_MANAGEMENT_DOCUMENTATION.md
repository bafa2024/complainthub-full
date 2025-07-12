# Admin Management Features Documentation

## Overview

The Admin Management system provides comprehensive administrative capabilities for managing the ComplaintHub Bot platform. This includes system overview, settings management, report generation, and system monitoring.

## Table of Contents

1. [Architecture](#architecture)
2. [Features](#features)
3. [API Endpoints](#api-endpoints)
4. [Frontend Components](#frontend-components)
5. [Database Models](#database-models)
6. [Setup and Configuration](#setup-and-configuration)
7. [Usage Examples](#usage-examples)
8. [Testing](#testing)
9. [Security](#security)
10. [Performance](#performance)
11. [Troubleshooting](#troubleshooting)
12. [Future Enhancements](#future-enhancements)

## Architecture

### Backend Architecture

```
backend/app/
├── api/v1/endpoints/
│   └── admin.py              # Admin API endpoints
├── api/v1/routes/
│   └── admin.py              # Admin router
├── services/
│   └── admin.py              # Admin business logic
├── models.py                 # SystemSettings model
└── schemas.py                # Admin schemas
```

### Frontend Architecture

```
frontend/src/
├── components/admin/
│   ├── AdminDashboard.jsx    # System overview dashboard
│   ├── AdminSettings.jsx     # System settings management
│   ├── AdminReports.jsx      # Report generation
│   └── Admin.css             # Admin styles
└── services/
    └── adminService.js       # Admin API client
```

## Features

### 1. Admin Dashboard

**Purpose**: Provides system overview with real-time metrics and quick access to management functions.

**Key Components**:
- System statistics cards (users, brands, tickets, resolution rate)
- Real-time metrics with live updates
- Performance indicators
- Quick action buttons
- Recent activity feed
- Top performing brands

**Features**:
- Auto-refresh every 30 seconds
- Date range filtering
- Export functionality
- Responsive design

### 2. System Settings Management

**Purpose**: Centralized configuration management for all system parameters.

**Settings Categories**:

#### API Credentials
- OpenAI API Key
- Twilio Account SID and Auth Token
- Deepgram API Key
- Stripe Secret and Publishable Keys

#### Business Rules
- Unresolved complaint fee (credits)
- Free resolution window (hours)
- Maximum tickets per user
- Auto-close after days
- Satisfaction threshold

#### System Configuration
- System name and email
- Timezone settings
- Maintenance mode toggle
- Debug mode toggle

#### Security Settings
- Session timeout (hours)
- Maximum login attempts
- Minimum password length
- Two-factor authentication requirement
- Allowed email domains

#### Notification Settings
- Email notifications toggle
- SMS notifications toggle
- Push notifications toggle
- Notification frequency

#### Integration Settings
- WhatsApp integration toggle
- Telegram integration toggle
- Voice integration toggle
- Email integration toggle

#### Analytics Settings
- Analytics enable/disable
- Data retention period
- User tracking toggle

#### Backup Settings
- Auto backup toggle
- Backup frequency
- Backup retention period

### 3. Report Generation

**Purpose**: Comprehensive reporting system for business intelligence and analytics.

**Report Types**:

#### Overview Report
- System-wide statistics
- Performance metrics
- Trend analysis
- Key performance indicators

#### Complaints Report
- Status distribution
- Category breakdown
- Brand performance
- Resolution metrics

#### Brands Report
- Brand performance comparison
- Industry analysis
- Revenue metrics
- Customer satisfaction

#### Users Report
- User registration trends
- Activity metrics
- Engagement statistics
- Satisfaction scores

#### Revenue Report
- Revenue trends
- Growth analysis
- Top revenue brands
- Financial metrics

#### System Health Report
- System status
- Performance metrics
- Error rates
- Uptime statistics

### 4. System Monitoring

**Purpose**: Real-time system health monitoring and alerting.

**Monitoring Features**:
- System status indicators
- Performance metrics
- Error rate tracking
- Response time monitoring
- Database health checks
- API status monitoring

### 5. External Service Testing

**Purpose**: Validate external service integrations.

**Supported Services**:
- OpenAI API
- Twilio API
- Deepgram API
- Stripe API

### 6. Backup Management

**Purpose**: System backup and restore functionality.

**Features**:
- Automated backups
- Manual backup creation
- Backup listing
- Backup restoration
- Backup deletion

## API Endpoints

### System Overview

```http
GET /api/v1/admin/stats
GET /api/v1/admin/dashboard?date_range=30d
GET /api/v1/admin/health
```

### Settings Management

```http
GET /api/v1/admin/settings
PUT /api/v1/admin/settings
POST /api/v1/admin/test-connection/{service}
POST /api/v1/admin/restart-system
```

### Report Generation

```http
GET /api/v1/admin/reports/complaints?start_date=2024-01-01&end_date=2024-01-31
GET /api/v1/admin/reports/brands?start_date=2024-01-01&end_date=2024-01-31
GET /api/v1/admin/reports/users?start_date=2024-01-01&end_date=2024-01-31
GET /api/v1/admin/reports/revenue?start_date=2024-01-01&end_date=2024-01-31
POST /api/v1/admin/reports/generate/{report_type}?format=pdf
```

### System Monitoring

```http
GET /api/v1/admin/activity?limit=10
GET /api/v1/admin/top-brands?limit=10
```

### Backup Management

```http
POST /api/v1/admin/backup
GET /api/v1/admin/backups
POST /api/v1/admin/backup/{backup_id}/restore
DELETE /api/v1/admin/backup/{backup_id}
```

## Frontend Components

### AdminDashboard

**Location**: `frontend/src/components/admin/AdminDashboard.jsx`

**Features**:
- Real-time statistics display
- Interactive charts and graphs
- Quick action buttons
- Responsive grid layout
- Auto-refresh functionality

**Key Methods**:
- `fetchDashboardData()` - Load dashboard data
- `startRealTimeUpdates()` - Enable live updates
- `handleDateRangeChange()` - Filter by date range
- `handleExport()` - Export reports

### AdminSettings

**Location**: `frontend/src/components/admin/AdminSettings.jsx`

**Features**:
- Tabbed interface for different setting categories
- Form validation
- Real-time connection testing
- Secure credential storage
- Settings persistence

**Key Methods**:
- `loadSettings()` - Load current settings
- `handleSubmit()` - Save settings
- `handleTestConnection()` - Test external services
- `handleSystemRestart()` - Restart system

### AdminReports

**Location**: `frontend/src/components/admin/AdminReports.jsx`

**Features**:
- Multiple report types
- Date range filtering
- Export in multiple formats (PDF, CSV, JSON)
- Interactive data visualization
- Report scheduling

**Key Methods**:
- `loadReports()` - Load report data
- `generateReport()` - Generate and export reports
- `handleDateRangeChange()` - Filter reports
- `handleTabChange()` - Switch report types

## Database Models

### SystemSettings

```python
class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    settings_data = Column(Text, nullable=False)  # JSON string of settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## Setup and Configuration

### 1. Database Setup

```bash
# Run database migrations
python -m alembic upgrade head

# Initialize system settings
python init_db.py
```

### 2. Environment Variables

```bash
# Admin credentials
ADMIN_EMAIL=admin@complainthub.com
ADMIN_PASSWORD=admin123

# External service keys
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DEEPGRAM_API_KEY=your_deepgram_key
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable
```

### 3. Frontend Configuration

```javascript
// adminService.js configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
```

## Usage Examples

### 1. Accessing Admin Dashboard

```javascript
// Navigate to admin dashboard
window.location.href = '/admin/dashboard';

// Or use React Router
<Link to="/admin/dashboard">Admin Dashboard</Link>
```

### 2. Updating System Settings

```javascript
import adminService from '../services/adminService';

// Get current settings
const settings = await adminService.getSystemSettings();

// Update settings
const updatedSettings = {
  ...settings,
  resolutionWindow: '48',
  systemName: 'Updated System Name'
};

await adminService.updateSystemSettings(updatedSettings);
```

### 3. Generating Reports

```javascript
// Generate complaints report
const filters = {
  startDate: '2024-01-01',
  endDate: '2024-01-31'
};

const report = await adminService.generateReport('complaints', 'pdf', filters);
```

### 4. Testing External Connections

```javascript
// Test OpenAI connection
const result = await adminService.testConnection('openai');
if (result.success) {
  console.log('OpenAI connection successful');
} else {
  console.error('OpenAI connection failed:', result.error);
}
```

### 5. System Health Monitoring

```javascript
// Get system health
const health = await adminService.getSystemHealth();
console.log('System status:', health.status);
console.log('Uptime:', health.uptime);
console.log('Error rate:', health.error_rate);
```

## Testing

### Running Tests

```bash
# Run admin management tests
python test_admin_management_features.py

# Test specific features
python -m pytest tests/test_admin.py -v
```

### Test Coverage

The test suite covers:
- ✅ Admin authentication
- ✅ System statistics
- ✅ Settings management
- ✅ Report generation
- ✅ External service testing
- ✅ System health monitoring
- ✅ Backup management
- ✅ Frontend page availability

### Manual Testing Checklist

- [ ] Admin login functionality
- [ ] Dashboard data loading
- [ ] Settings save/load
- [ ] Connection testing
- [ ] Report generation
- [ ] Export functionality
- [ ] Real-time updates
- [ ] Responsive design
- [ ] Error handling

## Security

### Authentication

- Admin-only access to all endpoints
- JWT token validation
- Session timeout management
- Role-based access control

### Data Protection

- Encrypted credential storage
- Secure API communication
- Input validation and sanitization
- SQL injection prevention

### Access Control

```python
# Admin-only endpoint protection
@router.get("/admin/stats")
async def get_system_stats(
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
```

## Performance

### Optimization Strategies

1. **Caching**: Implement Redis caching for frequently accessed data
2. **Database Indexing**: Optimize database queries with proper indexing
3. **Pagination**: Implement pagination for large datasets
4. **Background Processing**: Use Celery for report generation
5. **CDN**: Use CDN for static assets

### Monitoring

- Real-time performance metrics
- Database query optimization
- API response time tracking
- Error rate monitoring
- Resource usage tracking

## Troubleshooting

### Common Issues

#### 1. Admin Login Fails

**Symptoms**: Cannot access admin dashboard
**Solutions**:
- Verify admin credentials in database
- Check JWT token expiration
- Ensure admin role is properly set

#### 2. Settings Not Saving

**Symptoms**: Settings changes not persisted
**Solutions**:
- Check database connection
- Verify SystemSettings table exists
- Check for validation errors

#### 3. Reports Not Generating

**Symptoms**: Report generation fails
**Solutions**:
- Check date range validity
- Verify database permissions
- Check for memory constraints

#### 4. External Service Tests Fail

**Symptoms**: Connection tests return errors
**Solutions**:
- Verify API keys are correct
- Check network connectivity
- Validate service endpoints

### Debug Mode

Enable debug mode for detailed logging:

```python
# In settings
"debugMode": True

# Check logs
tail -f backend/app.log
```

### Error Logs

Monitor error logs for issues:

```bash
# View recent errors
grep "ERROR" backend/app.log | tail -20

# Monitor real-time logs
tail -f backend/app.log | grep "ERROR"
```

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Machine learning insights
   - Predictive analytics
   - Custom dashboard widgets

2. **Enhanced Reporting**
   - Scheduled reports
   - Email report delivery
   - Custom report builder

3. **System Monitoring**
   - Real-time alerts
   - Performance dashboards
   - Automated health checks

4. **User Management**
   - Advanced user analytics
   - User behavior tracking
   - Permission management

5. **Integration Management**
   - Webhook management
   - API rate limiting
   - Integration health monitoring

### Technical Improvements

1. **Performance**
   - GraphQL implementation
   - WebSocket real-time updates
   - Microservices architecture

2. **Security**
   - Two-factor authentication
   - Audit logging
   - Advanced encryption

3. **Scalability**
   - Horizontal scaling
   - Load balancing
   - Database sharding

### API Enhancements

```python
# Future API endpoints
@router.get("/admin/analytics/advanced")
@router.post("/admin/reports/schedule")
@router.get("/admin/alerts")
@router.post("/admin/webhooks")
@router.get("/admin/audit-logs")
```

## Conclusion

The Admin Management system provides a comprehensive solution for managing the ComplaintHub Bot platform. With features ranging from system overview to detailed reporting, it offers administrators full control and visibility into the platform's operations.

The modular architecture ensures easy maintenance and extensibility, while the comprehensive testing suite guarantees reliability. The system is designed to scale with the platform's growth and can be enhanced with additional features as needed.

For support or questions, please refer to the troubleshooting section or contact the development team. 