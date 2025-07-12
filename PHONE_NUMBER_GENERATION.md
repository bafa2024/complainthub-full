# Phone Number Generation API Documentation

## Overview

The Phone Number Generation API allows brand agents to search, purchase, and manage toll-free and local phone numbers through multiple telephony providers. This feature integrates with popular providers like Twilio, Knowlarity, Exotel, Ozonetel, and MyOperator.

## Features

- **Multi-Provider Support**: Integration with 5+ telephony providers
- **Real-time Number Search**: Search available numbers across providers
- **Instant Purchase**: Purchase numbers directly through the API
- **Brand Management**: Manage all phone numbers for a brand
- **Request System**: Submit and track phone number requests
- **Analytics**: Track usage and costs
- **Webhook Integration**: Automatic webhook URL generation

## Supported Providers

| Provider | Countries | Capabilities | Monthly Cost (Toll-free) |
|----------|-----------|--------------|-------------------------|
| Twilio | US, IN, GB, CA, AU | Voice, SMS, WhatsApp | $1.00 |
| Knowlarity | IN | Voice, SMS | ₹500 |
| Exotel | IN | Voice, SMS | ₹500 |
| Ozonetel | IN | Voice, SMS | ₹500 |
| MyOperator | IN | Voice, SMS | ₹500 |

## Database Schema

### PhoneNumber Model
```sql
CREATE TABLE phone_numbers (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    phone_number VARCHAR UNIQUE NOT NULL,
    provider VARCHAR NOT NULL,
    provider_id VARCHAR,
    country_code VARCHAR DEFAULT 'IN',
    area_code VARCHAR,
    number_type VARCHAR DEFAULT 'toll-free',
    capabilities JSON,
    status VARCHAR DEFAULT 'active',
    monthly_cost FLOAT DEFAULT 0.0,
    setup_cost FLOAT DEFAULT 0.0,
    webhook_url VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PhoneNumberRequest Model
```sql
CREATE TABLE phone_number_requests (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    country_code VARCHAR DEFAULT 'IN',
    area_code VARCHAR,
    number_type VARCHAR DEFAULT 'toll-free',
    capabilities JSON,
    provider_preference VARCHAR,
    status VARCHAR DEFAULT 'pending',
    assigned_number VARCHAR,
    provider_used VARCHAR,
    cost FLOAT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### 1. Get Telephony Providers
```http
GET /api/v1/phone-numbers/providers
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "name": "twilio",
    "display_name": "Twilio",
    "supported_countries": ["US", "IN", "GB", "CA", "AU"],
    "supported_capabilities": ["voice", "sms", "whatsapp"],
    "pricing": {
      "toll-free": {"monthly": 1.0, "setup": 0.0},
      "local": {"monthly": 1.0, "setup": 0.0}
    }
  }
]
```

### 2. Search Available Numbers
```http
GET /api/v1/phone-numbers/search?country_code=IN&number_type=toll-free&capabilities=voice,sms&provider=twilio
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "phone_number": "+91-1800-1234",
    "provider": "twilio",
    "country_code": "IN",
    "number_type": "toll-free",
    "capabilities": ["voice", "sms"],
    "monthly_cost": 1.0,
    "setup_cost": 0.0,
    "features": ["voice", "sms"]
  }
]
```

### 3. Purchase Phone Number
```http
POST /api/v1/phone-numbers/purchase
Authorization: Bearer <token>
Content-Type: application/json

{
  "country_code": "IN",
  "number_type": "toll-free",
  "capabilities": ["voice", "sms"],
  "provider_preference": "twilio",
  "auto_approve": false
}
```

**Response:**
```json
{
  "success": true,
  "phone_number": "+91-1800-1234",
  "provider": "twilio",
  "cost": 1.0,
  "message": "Phone number purchased successfully"
}
```

### 4. Get Brand Phone Numbers
```http
GET /api/v1/phone-numbers/brand
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": 1,
    "brand_id": 1,
    "phone_number": "+91-1800-1234",
    "provider": "twilio",
    "provider_id": "PN123456789",
    "country_code": "IN",
    "number_type": "toll-free",
    "capabilities": {"voice": true, "sms": true},
    "status": "active",
    "monthly_cost": 1.0,
    "setup_cost": 0.0,
    "webhook_url": "http://localhost:3000/api/v1/webhook/twilio",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### 5. Update Phone Number Status
```http
PUT /api/v1/phone-numbers/{phone_number}/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "inactive",
  "webhook_url": "https://new-webhook.com/webhook"
}
```

### 6. Release Phone Number
```http
DELETE /api/v1/phone-numbers/{phone_number}
Authorization: Bearer <token>
```

### 7. Create Phone Number Request
```http
POST /api/v1/phone-numbers/requests
Authorization: Bearer <token>
Content-Type: application/json

{
  "country_code": "IN",
  "number_type": "toll-free",
  "capabilities": ["voice", "sms"],
  "provider_preference": "twilio"
}
```

### 8. Get Phone Number Requests
```http
GET /api/v1/phone-numbers/requests
Authorization: Bearer <token>
```

### 9. Get Phone Number Analytics
```http
GET /api/v1/phone-numbers/analytics
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_numbers": 5,
  "active_numbers": 3,
  "inactive_numbers": 2,
  "monthly_cost": 1500.0,
  "provider_stats": [
    {"provider": "twilio", "count": 2},
    {"provider": "knowlarity", "count": 3}
  ]
}
```

## Frontend Integration

### React Component Usage

```jsx
import BrandPhoneNumbers from './components/brand/BrandPhoneNumbers';

// In your brand dashboard
<BrandPhoneNumbers />
```

### Service Methods

```javascript
import brandService from '../services/brandService';

// Get all phone numbers for the brand
const phoneNumbers = await brandService.getPhoneNumbers();

// Search for available numbers
const availableNumbers = await brandService.searchAvailableNumbers({
  country_code: 'IN',
  number_type: 'toll-free',
  capabilities: 'voice,sms',
  provider: 'twilio'
});

// Purchase a number
const result = await brandService.purchasePhoneNumber({
  country_code: 'IN',
  number_type: 'toll-free',
  capabilities: ['voice', 'sms'],
  provider_preference: 'twilio',
  auto_approve: true
});

// Update number status
await brandService.updatePhoneNumberStatus('+91-1800-1234', {
  status: 'inactive'
});

// Release a number
await brandService.releasePhoneNumber('+91-1800-1234');
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

# Knowlarity Configuration
KNOWLARITY_API_KEY=your_knowlarity_api_key
KNOWLARITY_BASE_URL=https://api.knowlarity.com/v1

# Exotel Configuration
EXOTEL_SID=your_exotel_sid
EXOTEL_TOKEN=your_exotel_token
EXOTEL_BASE_URL=https://api.exotel.com/v1

# Ozonetel Configuration
OZONETEL_API_KEY=your_ozonetel_api_key
OZONETEL_BASE_URL=https://api.ozonetel.com/v1

# MyOperator Configuration
MYOPERATOR_API_KEY=your_myoperator_api_key
MYOPERATOR_BASE_URL=https://api.myoperator.co/v1

# Phone Number Configuration
DEFAULT_COUNTRY_CODE=IN
DEFAULT_NUMBER_TYPE=toll-free
AUTO_APPROVE_NUMBER_REQUESTS=false
MAX_PHONE_NUMBERS_PER_BRAND=10
```

## Webhook Integration

When a phone number is purchased, a webhook URL is automatically generated:

```
http://your-domain.com/api/v1/webhook/{provider}
```

This webhook receives incoming calls and messages from the telephony provider.

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Phone number or request not found
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "error": "Error description",
  "details": "Additional error details",
  "status_code": 400
}
```

## Testing

### Run Test Script

```bash
python test_phone_numbers.py
```

The test script will:
1. Login as a brand user
2. Test provider listing
3. Search for available numbers
4. Purchase a test number
5. Test status updates
6. Test number release
7. Test analytics

### Manual Testing

1. **Login as Brand User**
   ```bash
   curl -X POST http://localhost:8000/api/v1/login \
     -d "username=brand@test.com&password=testpassword123"
   ```

2. **Search Numbers**
   ```bash
   curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/v1/phone-numbers/search?country_code=IN&number_type=toll-free"
   ```

3. **Purchase Number**
   ```bash
   curl -X POST http://localhost:8000/api/v1/phone-numbers/purchase \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"country_code":"IN","number_type":"toll-free","capabilities":["voice","sms"]}'
   ```

## Security Considerations

1. **Authentication**: All endpoints require valid JWT tokens
2. **Authorization**: Users can only access their brand's phone numbers
3. **Rate Limiting**: API endpoints are rate-limited
4. **Input Validation**: All inputs are validated and sanitized
5. **Provider Credentials**: Stored encrypted in database

## Monitoring and Analytics

### Key Metrics

- Total phone numbers per brand
- Active vs inactive numbers
- Monthly costs
- Provider distribution
- Purchase success rate

### Logging

All phone number operations are logged for audit purposes:
- Number purchases
- Status changes
- Number releases
- Failed operations

## Troubleshooting

### Common Issues

1. **Provider API Errors**
   - Check provider credentials
   - Verify API endpoints
   - Check rate limits

2. **Purchase Failures**
   - Verify brand credit balance
   - Check number availability
   - Validate provider status

3. **Webhook Issues**
   - Verify webhook URL accessibility
   - Check SSL certificates
   - Validate webhook signature

### Debug Mode

Enable debug logging by setting:
```python
logging.getLogger('app.services.telephony').setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Additional Providers**: Support for more telephony providers
2. **Number Porting**: Port existing numbers to the system
3. **Advanced Routing**: Intelligent call routing based on criteria
4. **Cost Optimization**: Automatic provider selection based on cost
5. **Bulk Operations**: Purchase multiple numbers at once
6. **Number Pooling**: Shared number pools for multiple brands

## Support

For technical support or questions about the Phone Number Generation API:

1. Check the logs for error details
2. Review the test script for examples
3. Verify configuration settings
4. Contact the development team

---

**Last Updated**: January 2024
**Version**: 1.0.0 