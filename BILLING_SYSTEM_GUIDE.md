# Advanced Billing & Payment Integration Guide

## Overview

The Advanced Billing & Payment Integration system provides comprehensive financial management capabilities for the Brand Complaint Management System. It includes credit-based billing, subscription management, payment processing, and financial reporting.

## 🏦 **Features**

### Core Billing Features
- **Credit System**: Pay-as-you-go credit-based billing
- **Subscription Plans**: Monthly subscription with automatic credit allocation
- **Payment Processing**: Stripe integration for secure payments
- **Complaint Charges**: Automatic charges for unresolved complaints after 24 hours
- **Transaction History**: Complete audit trail of all financial transactions
- **Invoice Generation**: Professional invoice creation and management
- **Refund Processing**: Admin-controlled refund system
- **Billing Analytics**: Comprehensive financial reporting and insights

### Business Model
- **Free Resolution Window**: 24 hours to resolve complaints without charge
- **Complaint Charges**: ₹50 per unresolved complaint after 24 hours
- **Subscription Plans**: Monthly plans with credit allocation
- **Credit Top-ups**: Pay-as-you-go credit purchases

## 🚀 **Quick Start**

### 1. Environment Setup

Add the following environment variables to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Stripe Product IDs (create these in your Stripe dashboard)
STRIPE_BASIC_PLAN_ID=price_basic_plan_id
STRIPE_PRO_PLAN_ID=price_pro_plan_id
STRIPE_ENTERPRISE_PLAN_ID=price_enterprise_plan_id

# Billing Configuration
COMPLAINT_CHARGE_AMOUNT=50.0
FREE_RESOLUTION_WINDOW_HOURS=24
LOW_BALANCE_THRESHOLD=100.0
CURRENCY=INR
```

### 2. Frontend Dependencies

Install Stripe dependencies:

```bash
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### 3. Database Migration

The billing system adds new tables to your database. Run the migration:

```bash
cd backend
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

## 📊 **Database Schema**

### New Tables

#### Transactions
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    ticket_id INTEGER,
    type VARCHAR NOT NULL, -- credit_topup, complaint_charge, subscription_payment, refund, adjustment
    amount FLOAT NOT NULL,
    status VARCHAR NOT NULL, -- pending, completed, failed, cancelled, refunded
    description TEXT,
    payment_intent_id VARCHAR,
    stripe_refund_id VARCHAR,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);
```

#### Subscriptions
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    stripe_subscription_id VARCHAR UNIQUE NOT NULL,
    plan_type VARCHAR NOT NULL, -- basic, professional, enterprise
    status VARCHAR NOT NULL, -- active, cancelled, past_due, unpaid, trialing
    credits_per_month INTEGER NOT NULL,
    monthly_price FLOAT NOT NULL,
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancelled_at TIMESTAMP,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Payment Methods
```sql
CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    stripe_payment_method_id VARCHAR UNIQUE NOT NULL,
    type VARCHAR NOT NULL, -- card, bank_account
    last4 VARCHAR,
    brand VARCHAR,
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Invoices
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER NOT NULL,
    transaction_id INTEGER,
    invoice_number VARCHAR UNIQUE NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR DEFAULT 'INR',
    status VARCHAR DEFAULT 'draft', -- draft, sent, paid, overdue, cancelled
    due_date TIMESTAMP,
    paid_at TIMESTAMP,
    items JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

## 🔧 **API Endpoints**

### Brand User Endpoints

#### Get Billing Summary
```http
GET /api/v1/billing/summary
Authorization: Bearer <token>
```

Response:
```json
{
  "current_balance": 1250.0,
  "subscription": {
    "active": true,
    "plan_type": "professional",
    "credits_per_month": 2500,
    "monthly_price": 2000,
    "next_billing_date": "2024-02-01T00:00:00Z"
  },
  "monthly_spending": 1500.0,
  "pending_charges": 2,
  "recent_transactions": [...]
}
```

#### Get Transaction History
```http
GET /api/v1/billing/transactions?limit=50&offset=0
Authorization: Bearer <token>
```

#### Create Credit Top-up
```http
POST /api/v1/billing/topup
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 1000,
  "payment_method": "stripe"
}
```

#### Confirm Payment
```http
POST /api/v1/billing/confirm-payment
Authorization: Bearer <token>
Content-Type: application/json

{
  "payment_intent_id": "pi_1234567890"
}
```

#### Get Subscription Plans
```http
GET /api/v1/billing/plans
Authorization: Bearer <token>
```

#### Create Subscription
```http
POST /api/v1/billing/subscription/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_type": "professional",
  "payment_method_id": "pm_1234567890"
}
```

#### Get Billing Analytics
```http
GET /api/v1/billing/analytics?date_range=30d
Authorization: Bearer <token>
```

#### Generate Invoice
```http
GET /api/v1/billing/invoice/{transaction_id}
Authorization: Bearer <token>
```

### Admin Endpoints

#### Get Admin Billing Logs
```http
GET /api/v1/billing/admin/billing-logs?brand_id=1&limit=100&offset=0
Authorization: Bearer <admin_token>
```

#### Process Refund
```http
POST /api/v1/billing/refund/{transaction_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "Customer request"
}
```

#### Process Complaint Charge
```http
POST /api/v1/billing/process-complaint-charge/{ticket_id}
Authorization: Bearer <admin_token>
```

#### Export Billing Data
```http
GET /api/v1/billing/admin/export?format=csv&date_range=30d
Authorization: Bearer <admin_token>
```

### Webhook Endpoints

#### Stripe Webhook
```http
POST /api/v1/billing/webhook/stripe
Content-Type: application/json
Stripe-Signature: <signature>
```

## 💳 **Payment Integration**

### Stripe Setup

1. **Create Stripe Account**: Sign up at [stripe.com](https://stripe.com)

2. **Get API Keys**: From your Stripe dashboard
   - Publishable key (frontend)
   - Secret key (backend)
   - Webhook secret

3. **Create Products and Prices**:
   ```bash
   # Basic Plan
   stripe products create --name "Basic Plan" --description "1000 credits/month"
   stripe prices create --product=prod_basic --unit-amount=100000 --currency=inr --recurring[interval]=month
   
   # Professional Plan
   stripe products create --name "Professional Plan" --description "2500 credits/month"
   stripe prices create --product=prod_pro --unit-amount=200000 --currency=inr --recurring[interval]=month
   
   # Enterprise Plan
   stripe products create --name "Enterprise Plan" --description "5000 credits/month"
   stripe prices create --product=prod_enterprise --unit-amount=350000 --currency=inr --recurring[interval]=month
   ```

4. **Configure Webhooks**:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/billing/webhook/stripe
   ```

### Frontend Integration

#### Initialize Stripe
```javascript
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);
```

#### Payment Form Component
```javascript
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';

const CheckoutForm = ({ amount, onSuccess }) => {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Create payment intent
    const response = await fetch('/api/v1/billing/topup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount, payment_method: 'stripe' })
    });
    
    const result = await response.json();
    
    // Confirm payment
    const { error, paymentIntent } = await stripe.confirmCardPayment(
      result.client_secret,
      { payment_method: { card: elements.getElement(CardElement) } }
    );
    
    if (!error) {
      // Confirm with backend
      await fetch('/api/v1/billing/confirm-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_intent_id: result.payment_intent_id })
      });
      
      onSuccess();
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <CardElement />
      <button type="submit">Pay ₹{amount}</button>
    </form>
  );
};
```

## 📈 **Billing Analytics**

### Available Metrics

- **Total Revenue**: Overall platform revenue
- **Monthly Spending**: Brand-specific monthly expenditure
- **Transaction Count**: Number of transactions
- **Credit Utilization**: Credit usage patterns
- **Subscription Metrics**: Active subscriptions and churn
- **Complaint Charges**: Revenue from unresolved complaints

### Analytics API Response
```json
{
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_spent": 50000.0,
    "total_credits_added": 75000.0,
    "total_charges": 25000.0,
    "transaction_count": 150
  },
  "by_type": {
    "credit_topup": {
      "count": 50,
      "total": 75000.0
    },
    "complaint_charge": {
      "count": 100,
      "total": 25000.0
    }
  }
}
```

## 🔄 **Business Logic**

### Complaint Charge Processing

1. **24-Hour Free Window**: Complaints resolved within 24 hours are free
2. **Automatic Charging**: After 24 hours, ₹50 is charged per unresolved complaint
3. **Balance Check**: If insufficient balance, charge is marked as pending
4. **Low Balance Alerts**: Notifications sent when balance falls below ₹100

### Subscription Management

1. **Monthly Credits**: Credits added automatically on subscription renewal
2. **Credit Rollover**: Unused credits carry forward to next month
3. **Plan Changes**: Can upgrade/downgrade anytime
4. **Cancellation**: Immediate access to remaining credits

### Payment Flow

1. **Credit Top-up**:
   - User selects amount
   - Payment intent created
   - Payment processed via Stripe
   - Credits added to balance
   - Transaction recorded

2. **Subscription Payment**:
   - Monthly automatic billing
   - Credits allocated to brand
   - Transaction recorded
   - Invoice generated

3. **Complaint Charge**:
   - Automatic after 24 hours
   - Balance checked
   - Charge processed or marked pending
   - Transaction recorded

## 🛡️ **Security Considerations**

### Payment Security
- **PCI Compliance**: Stripe handles all card data
- **Webhook Verification**: Stripe signature verification
- **HTTPS Only**: All payment endpoints require HTTPS
- **Token-based Auth**: JWT tokens for API access

### Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Audit Trail**: Complete transaction history
- **Access Control**: Role-based permissions
- **Data Retention**: Configurable retention policies

### Fraud Prevention
- **Rate Limiting**: API rate limits
- **Amount Limits**: Configurable payment limits
- **Suspicious Activity**: Automated detection
- **Manual Review**: Admin oversight for large transactions

## 🧪 **Testing**

### Run Test Script
```bash
python test_billing_system.py
```

### Test Coverage
- ✅ Authentication and authorization
- ✅ Credit top-up creation
- ✅ Payment confirmation
- ✅ Subscription management
- ✅ Transaction history
- ✅ Billing analytics
- ✅ Invoice generation
- ✅ Refund processing
- ✅ Admin billing logs
- ✅ Complaint charge processing
- ✅ Stripe webhook handling
- ✅ Data export functionality

### Manual Testing Checklist

#### Brand User Tests
- [ ] View billing summary
- [ ] Check transaction history
- [ ] View subscription plans
- [ ] Create credit top-up
- [ ] Process payment
- [ ] View billing analytics
- [ ] Generate invoice

#### Admin Tests
- [ ] View all billing logs
- [ ] Process refunds
- [ ] Export billing data
- [ ] Monitor complaint charges
- [ ] View financial analytics

#### Integration Tests
- [ ] Stripe webhook processing
- [ ] Payment confirmation flow
- [ ] Subscription renewal
- [ ] Low balance notifications
- [ ] Invoice generation

## 🚨 **Troubleshooting**

### Common Issues

#### Payment Failures
```bash
# Check Stripe logs
stripe logs tail

# Verify webhook configuration
stripe webhooks list
```

#### Database Issues
```bash
# Check database connection
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Verify table structure
python -c "from app.models import Transaction, Subscription; print('Tables exist')"
```

#### Frontend Issues
```bash
# Check Stripe initialization
console.log('Stripe loaded:', !!window.Stripe);

# Verify API calls
# Check browser network tab for failed requests
```

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Invalid payment data | Check request format |
| 401 | Unauthorized | Verify authentication token |
| 403 | Insufficient permissions | Check user role |
| 404 | Resource not found | Verify resource ID |
| 422 | Validation error | Check request data |
| 500 | Server error | Check server logs |

### Logs and Monitoring

#### Backend Logs
```bash
# View application logs
tail -f backend/app.log

# Check Stripe integration logs
grep "stripe" backend/app.log
```

#### Frontend Logs
```javascript
// Enable debug logging
localStorage.setItem('debug', 'stripe:*');
```

## 📚 **API Reference**

### Billing Service Methods

#### `process_complaint_charge(ticket_id, brand_id)`
Process charge for unresolved complaint after 24 hours.

#### `process_credit_topup(brand_id, amount, payment_method)`
Process credit top-up payment.

#### `confirm_payment(payment_intent_id)`
Confirm payment and add credits to brand balance.

#### `create_subscription(brand_id, plan_type, payment_method_id)`
Create subscription for a brand.

#### `get_brand_billing_summary(brand_id)`
Get comprehensive billing summary for a brand.

#### `get_transaction_history(brand_id, limit, offset)`
Get detailed transaction history for a brand.

#### `create_refund(transaction_id, reason)`
Create refund for a transaction.

#### `generate_invoice(transaction_id)`
Generate invoice for a transaction.

#### `get_billing_analytics(brand_id, date_range)`
Get billing analytics for a brand.

### Frontend Service Methods

#### `getBillingSummary()`
Get billing summary for current brand.

#### `getTransactionHistory(limit, offset)`
Get transaction history.

#### `createCreditTopup(amount, paymentMethod)`
Create credit top-up.

#### `confirmPayment(paymentIntentId)`
Confirm payment.

#### `createSubscription(planType, paymentMethodId)`
Create subscription.

#### `getSubscriptionPlans()`
Get available subscription plans.

#### `getBillingAnalytics(dateRange)`
Get billing analytics.

#### `generateInvoice(transactionId)`
Generate invoice.

#### `createRefund(transactionId, reason)`
Create refund.

## 🔄 **Maintenance**

### Regular Tasks

#### Daily
- Monitor payment failures
- Check webhook processing
- Review pending charges

#### Weekly
- Analyze billing analytics
- Review subscription renewals
- Check low balance alerts

#### Monthly
- Generate financial reports
- Review pricing strategy
- Update subscription plans

### Backup and Recovery

#### Database Backup
```bash
# Backup billing tables
pg_dump -t transactions -t subscriptions -t payment_methods -t invoices database_name > billing_backup.sql
```

#### Configuration Backup
```bash
# Backup environment variables
cp .env .env.backup
```

### Performance Optimization

#### Database Indexes
```sql
-- Add indexes for better performance
CREATE INDEX idx_transactions_brand_id ON transactions(brand_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_subscriptions_brand_id ON subscriptions(brand_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
```

#### Caching
```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_brand_balance(brand_id):
    # Implementation
    pass
```

## 📞 **Support**

### Getting Help
- **Documentation**: Check this guide first
- **Logs**: Review application logs for errors
- **Testing**: Run test script to verify functionality
- **Community**: Check project issues and discussions

### Contact Information
- **Technical Issues**: Create GitHub issue
- **Billing Questions**: Contact support team
- **Stripe Support**: [stripe.com/support](https://stripe.com/support)

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Compatibility**: Backend v1.0+, Frontend v1.0+ 