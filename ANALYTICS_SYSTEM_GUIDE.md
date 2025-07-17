# Advanced Analytics & Reporting System Guide

## 📊 Overview

The Advanced Analytics & Reporting System provides comprehensive insights into complaint management performance, user behavior, and system health. This system includes real-time metrics, predictive analytics, trend analysis, and detailed reporting capabilities.

## 🚀 Features

### Core Analytics Features
- **System Overview Analytics**: Comprehensive system-wide metrics
- **Brand-Specific Analytics**: Detailed performance metrics for individual brands
- **User Analytics**: Individual user behavior and complaint patterns
- **Real-time Metrics**: Live system performance indicators
- **Predictive Analytics**: Forecasting for ticket volume and trends
- **Trend Analysis**: Historical data analysis and growth patterns
- **Metric Comparison**: Period-over-period performance comparison
- **Report Generation**: Automated report creation in multiple formats
- **Dashboard Integration**: Unified analytics dashboard
- **System Health Monitoring**: Real-time system status and performance

### Advanced Capabilities
- **Multi-dimensional Analysis**: Channel, category, sentiment, and time-based analysis
- **Custom Date Ranges**: Flexible time period selection (7d, 30d, 90d, 1y)
- **Export Functionality**: JSON, CSV, and PDF export options
- **Access Control**: Role-based analytics access
- **Real-time Updates**: Live data refresh capabilities
- **Performance Optimization**: Efficient data aggregation and caching

## 🏗️ Architecture

### Backend Components

#### Analytics Service (`backend/app/services/analytics.py`)
```python
class AnalyticsService:
    def get_system_overview(self, date_range: str) -> Dict[str, Any]
    def get_brand_analytics(self, brand_id: int, date_range: str) -> Dict[str, Any]
    def get_user_analytics(self, user_id: int, date_range: str) -> Dict[str, Any]
    def get_real_time_metrics(self) -> Dict[str, Any]
    def generate_report(self, report_type: str, filters: Dict[str, Any]) -> Dict[str, Any]
    def get_predictive_analytics(self, metric: str, days: int) -> Dict[str, Any]
```

#### API Endpoints (`backend/app/api/v1/endpoints/analytics.py`)
- `GET /analytics/overview` - System overview analytics
- `GET /analytics/brand/{brand_id}` - Brand-specific analytics
- `GET /analytics/user/{user_id}` - User-specific analytics
- `GET /analytics/realtime` - Real-time metrics
- `POST /analytics/reports/{report_type}` - Generate reports
- `GET /analytics/predictive/{metric}` - Predictive analytics
- `GET /analytics/trends` - Trend analysis
- `GET /analytics/comparison` - Metric comparison
- `GET /analytics/export/{report_type}` - Export reports
- `GET /analytics/dashboard` - Dashboard data
- `GET /analytics/health` - System health

### Frontend Components

#### Admin Analytics (`frontend/src/components/admin/AdminAnalytics.jsx`)
- Real-time dashboard with live updates
- Interactive charts and visualizations
- Export functionality
- Multi-tab interface (Overview, Real-time, Trends, Brands, Channels)

#### Analytics Service (`frontend/src/services/adminService.js`)
```javascript
const getAnalyticsOverview = async (dateRange) => Promise<Object>
const getRealTimeMetrics = async () => Promise<Object>
const generateReport = async (reportType, filters) => Promise<Object>
const getPredictiveAnalytics = async (metric, days) => Promise<Object>
const getTrends = async (dateRange, metric) => Promise<Object>
const compareMetrics = async (metric, period1, period2, brandId) => Promise<Object>
const exportReport = async (reportType, format, filters) => Promise<Object>
const getDashboardData = async (dateRange) => Promise<Object>
const getAnalyticsHealth = async () => Promise<Object>
```

## 📈 Analytics Metrics

### System Overview Metrics
- **Total Users**: Number of registered users
- **Total Brands**: Number of active brands
- **Total Tickets**: Total complaints received
- **Active Tickets**: Currently open complaints
- **Resolved Tickets**: Successfully resolved complaints
- **Resolution Rate**: Percentage of resolved complaints
- **Average Resolution Time**: Mean time to resolve complaints
- **Average Satisfaction**: Overall customer satisfaction score
- **Total Revenue**: System revenue generated

### Real-time Metrics
- **Today's Tickets**: Complaints received today
- **Last Hour Tickets**: Complaints in the last hour
- **Active Conversations**: Currently active chat sessions
- **Pending Tickets**: Tickets awaiting response
- **Recent Activity**: Latest system activities
- **System Health**: System performance indicators

### Brand Analytics
- **Brand Performance**: Individual brand metrics
- **Channel Performance**: Performance by communication channel
- **Category Analysis**: Complaint distribution by category
- **Sentiment Trends**: Customer sentiment over time
- **Agent Performance**: Team member performance metrics

### User Analytics
- **Complaint History**: User's complaint patterns
- **Channel Usage**: Preferred communication channels
- **Category Preferences**: Most common complaint categories
- **Satisfaction History**: User satisfaction trends
- **Recent Activity**: User's recent interactions

## 🔧 Setup and Configuration

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Database Setup**
```bash
python init_db.py
```

3. **Start Server**
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

### Environment Variables

Add these to your `.env` file:
```env
# Analytics Configuration
ANALYTICS_CACHE_TTL=300
ANALYTICS_REAL_TIME_UPDATE_INTERVAL=30
ANALYTICS_MAX_DATE_RANGE=365
ANALYTICS_PREDICTION_DAYS=30

# Database Configuration
DATABASE_URL=sqlite:///./voicebot.db

# API Configuration
API_BASE_URL=http://localhost:8000
```

## 📊 API Reference

### System Overview Analytics

**Endpoint**: `GET /api/v1/analytics/overview`

**Parameters**:
- `date_range` (string): Date range for analysis (7d, 30d, 90d, 1y)

**Response**:
```json
{
  "status": "success",
  "data": {
    "overview": {
      "total_users": 2847,
      "total_brands": 156,
      "total_tickets": 1247,
      "active_tickets": 58,
      "resolved_tickets": 1189,
      "resolution_rate": 95.3,
      "avg_resolution_time": 2.3,
      "avg_satisfaction": 4.2,
      "total_revenue": 45600
    },
    "status_breakdown": {
      "new": 13,
      "in-progress": 45,
      "resolved": 1189,
      "closed": 0
    },
    "channel_distribution": {
      "whatsapp": 456,
      "telegram": 234,
      "webchat": 345,
      "voice": 156,
      "email": 56
    },
    "category_distribution": {
      "Technical Issues": 456,
      "Billing": 234,
      "Service Quality": 198,
      "Product Issues": 156,
      "Other": 203
    },
    "sentiment_metrics": {
      "avg_sentiment": 3.8,
      "sentiment_distribution": {
        "positive": 789,
        "neutral": 234,
        "negative": 224
      },
      "avg_satisfaction": 4.2
    },
    "trends": {
      "daily_tickets": [
        {"date": "2024-01-01", "count": 45},
        {"date": "2024-01-02", "count": 52}
      ],
      "growth_rate": 12.5
    }
  }
}
```

### Real-time Metrics

**Endpoint**: `GET /api/v1/analytics/realtime`

**Response**:
```json
{
  "status": "success",
  "data": {
    "today_tickets": 67,
    "last_hour_tickets": 8,
    "active_conversations": 23,
    "pending_tickets": 45,
    "recent_activity": [
      {
        "ticket_id": 1247,
        "title": "Payment processing issue",
        "status": "new",
        "brand_id": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "channel": "whatsapp"
      }
    ],
    "system_health": {
      "status": "healthy",
      "recent_activity": 67,
      "error_rate": 0.02,
      "avg_response_time": 245
    }
  }
}
```

### Report Generation

**Endpoint**: `POST /api/v1/analytics/reports/{report_type}`

**Report Types**:
- `performance` - Performance metrics report
- `trends` - Trend analysis report
- `financial` - Financial metrics report
- `customer_satisfaction` - Satisfaction analysis report
- `channel_analysis` - Channel performance report

**Request Body**:
```json
{
  "date_range": "30d",
  "brand_id": 1,
  "filters": {
    "category": "Technical Issues",
    "channel": "whatsapp"
  }
}
```

### Predictive Analytics

**Endpoint**: `GET /api/v1/analytics/predictive/{metric}`

**Metrics**:
- `ticket_volume` - Predict ticket volume
- `resolution_time` - Predict resolution times
- `satisfaction` - Predict satisfaction trends

**Parameters**:
- `days` (integer): Number of days to predict (1-365)

**Response**:
```json
{
  "status": "success",
  "data": {
    "predictions": [
      {
        "date": "2024-01-16",
        "predicted_volume": 45
      }
    ],
    "confidence": 0.75,
    "method": "linear_regression"
  }
}
```

## 🎨 Frontend Usage

### Admin Analytics Dashboard

```jsx
import AdminAnalytics from './components/admin/AdminAnalytics';

// In your admin dashboard
<AdminAnalytics />
```

### Using Analytics Service

```javascript
import adminService from '../services/adminService';

// Get system overview
const overview = await adminService.getAnalyticsOverview('30d');

// Get real-time metrics
const realTime = await adminService.getRealTimeMetrics();

// Generate report
const report = await adminService.generateReport('performance', {
  date_range: '30d',
  brand_id: 1
});

// Get predictive analytics
const predictions = await adminService.getPredictiveAnalytics('ticket_volume', 30);
```

### Custom Analytics Components

```jsx
import React, { useState, useEffect } from 'react';
import adminService from '../services/adminService';

const CustomAnalytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const analyticsData = await adminService.getAnalyticsOverview('30d');
        setData(analyticsData);
      } catch (error) {
        console.error('Error fetching analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Custom Analytics</h2>
      <p>Total Tickets: {data?.overview?.total_tickets}</p>
      <p>Resolution Rate: {data?.overview?.resolution_rate}%</p>
    </div>
  );
};
```

## 🧪 Testing

### Running Analytics Tests

```bash
# Run comprehensive analytics tests
python test_analytics_system.py
```

### Test Coverage

The test suite covers:
- ✅ System overview analytics
- ✅ Brand-specific analytics
- ✅ User analytics
- ✅ Real-time metrics
- ✅ Report generation
- ✅ Predictive analytics
- ✅ Trend analysis
- ✅ Metric comparison
- ✅ Report export
- ✅ Dashboard data
- ✅ System health
- ✅ Access control

### Manual Testing

1. **Start the server**:
```bash
cd backend
uvicorn app.main:app --reload
```

2. **Access the API documentation**:
```
http://localhost:8000/docs
```

3. **Test endpoints manually**:
```bash
# Get system overview
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/analytics/overview?date_range=30d"

# Get real-time metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/analytics/realtime"
```

## 🔒 Security and Access Control

### Role-Based Access

- **Admin Users**: Full access to all analytics
- **Brand Users**: Access to their own brand analytics
- **Regular Users**: Access to their own user analytics

### Authentication

All analytics endpoints require valid JWT tokens:
```javascript
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

### Data Privacy

- User data is anonymized in aggregate reports
- Individual user data is only accessible to the user themselves
- Brand data is restricted to authorized brand users
- Admin access is logged for audit purposes

## 📊 Performance Optimization

### Caching Strategy

- **Real-time data**: 30-second cache
- **Overview analytics**: 5-minute cache
- **Reports**: 1-hour cache
- **Predictive analytics**: 24-hour cache

### Database Optimization

- Indexed queries for date ranges
- Aggregated views for common metrics
- Partitioned tables for historical data
- Connection pooling for high concurrency

### Frontend Optimization

- Lazy loading of analytics components
- Debounced API calls for real-time updates
- Client-side caching of static data
- Progressive loading of large datasets

## 🚨 Troubleshooting

### Common Issues

1. **Analytics data not loading**
   - Check database connection
   - Verify user authentication
   - Check API endpoint availability

2. **Real-time updates not working**
   - Verify WebSocket connection
   - Check browser console for errors
   - Ensure proper authentication

3. **Reports not generating**
   - Check file permissions for export
   - Verify report type is supported
   - Check server logs for errors

4. **Performance issues**
   - Monitor database query performance
   - Check cache hit rates
   - Optimize date range queries

### Debug Mode

Enable debug logging:
```python
# In backend/app/config/settings.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Health Checks

Monitor system health:
```bash
curl "http://localhost:8000/api/v1/analytics/health"
```

## 📈 Monitoring and Alerts

### Key Metrics to Monitor

- **API Response Times**: Should be < 500ms
- **Database Query Performance**: Should be < 100ms
- **Cache Hit Rates**: Should be > 80%
- **Error Rates**: Should be < 1%
- **Real-time Update Latency**: Should be < 30s

### Alerting

Set up alerts for:
- High error rates (> 5%)
- Slow response times (> 2s)
- Cache miss rates (> 50%)
- Database connection failures
- Real-time update failures

## 🔄 Updates and Maintenance

### Regular Maintenance

- **Daily**: Check system health metrics
- **Weekly**: Review performance trends
- **Monthly**: Update predictive models
- **Quarterly**: Optimize database queries

### Version Updates

1. **Backup current data**
2. **Update dependencies**
3. **Run database migrations**
4. **Test all analytics endpoints**
5. **Update frontend components**
6. **Verify real-time functionality**

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Grafana](https://grafana.com/) - Metrics visualization
- [Prometheus](https://prometheus.io/) - Monitoring

### Support
- Check the test results for specific issues
- Review server logs for error details
- Use the API documentation for endpoint details
- Monitor system health for performance issues

---

**Note**: This analytics system is designed to provide comprehensive insights while maintaining performance and security. Regular monitoring and maintenance are essential for optimal operation. 