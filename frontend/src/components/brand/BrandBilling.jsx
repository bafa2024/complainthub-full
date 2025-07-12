import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandBilling.css';

const BrandBilling = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [billingData, setBillingData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [topupAmount, setTopupAmount] = useState(1000);
  const [processingPayment, setProcessingPayment] = useState(false);

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [summaryData, transactionsData, plansData] = await Promise.all([
        brandService.getBillingSummary(),
        brandService.getBillingTransactions(),
        brandService.getSubscriptionPlans()
      ]);
      
      setBillingData(summaryData);
      setTransactions(transactionsData || []);
      setSubscriptionPlans(plansData || []);
    } catch (err) {
      console.error('Error loading billing data:', err);
      setError('Failed to load billing data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreditTopup = async () => {
    if (!topupAmount || topupAmount <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    try {
      setProcessingPayment(true);
      setError('');
      
      const result = await brandService.createCreditTopup({
        amount: topupAmount,
        payment_method: 'stripe'
      });
      
      if (result.success) {
        // In a real implementation, you would redirect to Stripe Checkout
        // For now, we'll simulate the payment confirmation
        await handlePaymentConfirmation(result.payment_intent_id);
      } else {
        throw new Error(result.error || 'Payment failed');
      }
    } catch (err) {
      console.error('Error processing topup:', err);
      setError('Failed to process payment: ' + (err.message || 'Unknown error'));
    } finally {
      setProcessingPayment(false);
    }
  };

  const handlePaymentConfirmation = async (paymentIntentId) => {
    try {
      const result = await brandService.confirmPayment(paymentIntentId);
      
      if (result.success) {
        alert(`Payment successful! ${result.credits_added} credits added to your account.`);
        loadBillingData(); // Refresh billing data
      } else {
        throw new Error(result.error || 'Payment confirmation failed');
      }
    } catch (err) {
      console.error('Error confirming payment:', err);
      setError('Failed to confirm payment: ' + (err.message || 'Unknown error'));
    }
  };

  const handleCreateSubscription = async (planType) => {
    if (!window.confirm(`Are you sure you want to subscribe to the ${planType} plan?`)) {
      return;
    }

    try {
      setProcessingPayment(true);
      setError('');
      
      const result = await brandService.createSubscription({
        plan_type: planType,
        payment_method_id: 'pm_default' // In real implementation, this would be selected
      });
      
      if (result.success) {
        alert(`Successfully subscribed to ${planType} plan!`);
        loadBillingData(); // Refresh billing data
      } else {
        throw new Error(result.error || 'Subscription failed');
      }
    } catch (err) {
      console.error('Error creating subscription:', err);
      setError('Failed to create subscription: ' + (err.message || 'Unknown error'));
    } finally {
      setProcessingPayment(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionStatusClass = (status) => {
    switch (status) {
      case 'completed': return 'status-completed';
      case 'pending': return 'status-pending';
      case 'failed': return 'status-failed';
      default: return 'status-unknown';
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="brand-billing-container">
      <div className="page-header">
        <h1>Billing & Credits</h1>
        <p>Manage your credit balance, payments, and subscription</p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
          <button onClick={() => setError('')} className="close-btn">&times;</button>
        </div>
      )}

      {/* Credit Balance Overview */}
      <div className="credit-overview">
        <div className="balance-card">
          <div className="balance-header">
            <h2>Current Balance</h2>
            <div className="balance-amount">
              {billingData?.current_balance ? formatCurrency(billingData.current_balance) : '₹0.00'}
            </div>
          </div>
          
          <div className="balance-details">
            <div className="balance-item">
              <span>Free Resolution Window:</span>
              <span>24 hours</span>
            </div>
            <div className="balance-item">
              <span>Complaint Charge:</span>
              <span>₹50 per unresolved complaint</span>
            </div>
            <div className="balance-item">
              <span>Low Balance Alert:</span>
              <span>₹100</span>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setActiveTab('topup')}
          >
            Add Credits
          </button>
          <button 
            className="btn btn-outline-primary"
            onClick={() => setActiveTab('subscription')}
          >
            View Plans
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-btn ${activeTab === 'topup' ? 'active' : ''}`}
          onClick={() => setActiveTab('topup')}
        >
          Add Credits
        </button>
        <button 
          className={`tab-btn ${activeTab === 'subscription' ? 'active' : ''}`}
          onClick={() => setActiveTab('subscription')}
        >
          Subscription Plans
        </button>
        <button 
          className={`tab-btn ${activeTab === 'transactions' ? 'active' : ''}`}
          onClick={() => setActiveTab('transactions')}
        >
          Transaction History
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="tab-content">
          <div className="overview-grid">
            <div className="overview-card">
              <h3>Monthly Spending</h3>
              <div className="card-value">
                {billingData?.monthly_spending ? formatCurrency(billingData.monthly_spending) : '₹0.00'}
              </div>
            </div>
            
            <div className="overview-card">
              <h3>Pending Charges</h3>
              <div className="card-value">
                {billingData?.pending_charges || 0} complaints
              </div>
            </div>
            
            <div className="overview-card">
              <h3>Subscription Status</h3>
              <div className="card-value">
                {billingData?.subscription?.active ? 'Active' : 'Inactive'}
              </div>
              {billingData?.subscription?.active && (
                <div className="card-subtitle">
                  {billingData.subscription.plan_type} Plan
                </div>
              )}
            </div>
            
            <div className="overview-card">
              <h3>Next Billing</h3>
              <div className="card-value">
                {billingData?.subscription?.next_billing_date 
                  ? formatDate(billingData.subscription.next_billing_date)
                  : 'N/A'
                }
              </div>
            </div>
          </div>

          {billingData?.subscription?.active && (
            <div className="subscription-info">
              <h3>Current Subscription</h3>
              <div className="subscription-details">
                <p><strong>Plan:</strong> {billingData.subscription.plan_type}</p>
                <p><strong>Credits per Month:</strong> {billingData.subscription.credits_per_month}</p>
                <p><strong>Monthly Price:</strong> {formatCurrency(billingData.subscription.monthly_price)}</p>
                <p><strong>Next Billing:</strong> {formatDate(billingData.subscription.next_billing_date)}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add Credits Tab */}
      {activeTab === 'topup' && (
        <div className="tab-content">
          <div className="topup-section">
            <h2>Add Credits to Your Account</h2>
            <p>Purchase credits to handle unresolved complaints. Each unresolved complaint costs ₹50 after 24 hours.</p>
            
            <div className="topup-form">
              <div className="form-group">
                <label>Amount (₹):</label>
                <input 
                  type="number"
                  value={topupAmount}
                  onChange={(e) => setTopupAmount(parseFloat(e.target.value) || 0)}
                  min="100"
                  step="100"
                  className="form-control"
                />
              </div>
              
              <div className="topup-preview">
                <h4>Payment Summary</h4>
                <div className="preview-item">
                  <span>Credits to Add:</span>
                  <span>{topupAmount}</span>
                </div>
                <div className="preview-item">
                  <span>Amount:</span>
                  <span>{formatCurrency(topupAmount)}</span>
                </div>
              </div>
              
              <button 
                className="btn btn-primary btn-lg"
                onClick={handleCreditTopup}
                disabled={processingPayment || topupAmount <= 0}
              >
                {processingPayment ? 'Processing...' : 'Proceed to Payment'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Subscription Plans Tab */}
      {activeTab === 'subscription' && (
        <div className="tab-content">
          <div className="plans-section">
            <h2>Subscription Plans</h2>
            <p>Choose a monthly plan to get automatic credit allocation and better rates.</p>
            
            <div className="plans-grid">
              {subscriptionPlans.map((plan) => (
                <div key={plan.type} className={`plan-card ${billingData?.subscription?.plan_type === plan.type ? 'current-plan' : ''}`}>
                  <div className="plan-header">
                    <h3>{plan.name}</h3>
                    <div className="plan-price">
                      {formatCurrency(plan.monthly_price)}<span>/month</span>
                    </div>
                  </div>
                  
                  <div className="plan-features">
                    <div className="feature">
                      <span>✓</span> {plan.credits_per_month} credits per month
                    </div>
                    <div className="feature">
                      <span>✓</span> Automatic credit allocation
                    </div>
                    <div className="feature">
                      <span>✓</span> Priority support
                    </div>
                    {plan.features?.map((feature, index) => (
                      <div key={index} className="feature">
                        <span>✓</span> {feature}
                      </div>
                    ))}
                  </div>
                  
                  <div className="plan-actions">
                    {billingData?.subscription?.plan_type === plan.type ? (
                      <button className="btn btn-secondary" disabled>
                        Current Plan
                      </button>
                    ) : (
                      <button 
                        className="btn btn-primary"
                        onClick={() => handleCreateSubscription(plan.type)}
                        disabled={processingPayment}
                      >
                        {processingPayment ? 'Processing...' : 'Subscribe'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Transaction History Tab */}
      {activeTab === 'transactions' && (
        <div className="tab-content">
          <div className="transactions-section">
            <h2>Transaction History</h2>
            
            {transactions.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📊</div>
                <h3>No Transactions Yet</h3>
                <p>Your transaction history will appear here once you make payments or receive charges.</p>
              </div>
            ) : (
              <div className="transactions-table">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction) => (
                      <tr key={transaction.id}>
                        <td>{formatDate(transaction.created_at)}</td>
                        <td>{transaction.type.replace('_', ' ').toUpperCase()}</td>
                        <td>{transaction.description}</td>
                        <td className={transaction.amount > 0 ? 'amount-positive' : 'amount-negative'}>
                          {formatCurrency(Math.abs(transaction.amount))}
                        </td>
                        <td>
                          <span className={`status-badge ${getTransactionStatusClass(transaction.status)}`}>
                            {transaction.status.toUpperCase()}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BrandBilling;