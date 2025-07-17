import React, { useState, useEffect } from 'react';
import './CreditBalance.css';

const CreditBalance = ({
  balance = 0,
  currency = '₹',
  onPurchase,
  onRefresh,
  showPurchaseButton = true,
  showHistory = true,
  className = '',
  loading = false,
  disabled = false,
  size = 'medium', // 'small', 'medium', 'large'
  variant = 'default', // 'default', 'card', 'minimal', 'detailed'
  purchaseOptions = [
    { credits: 100, price: 100, popular: false },
    { credits: 500, price: 450, popular: true, discount: 10 },
    { credits: 1000, price: 800, popular: false, discount: 20 },
    { credits: 2000, price: 1500, popular: false, discount: 25 }
  ]
}) => {
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [purchaseLoading, setPurchaseLoading] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    if (showHistory) {
      // Mock transaction history - in real app, fetch from API
      setTransactions([
        {
          id: 1,
          type: 'purchase',
          amount: 500,
          price: 450,
          date: new Date(Date.now() - 86400000), // 1 day ago
          status: 'completed'
        },
        {
          id: 2,
          type: 'usage',
          amount: -50,
          description: 'Voice complaint processing',
          date: new Date(Date.now() - 3600000), // 1 hour ago
          status: 'completed'
        },
        {
          id: 3,
          type: 'purchase',
          amount: 100,
          price: 100,
          date: new Date(Date.now() - 604800000), // 1 week ago
          status: 'completed'
        }
      ]);
    }
  }, [showHistory]);

  const handlePurchase = async (packageData) => {
    if (disabled || purchaseLoading) return;
    
    setPurchaseLoading(true);
    try {
      await onPurchase?.(packageData);
      setShowPurchaseModal(false);
      setSelectedPackage(null);
    } catch (error) {
      console.error('Purchase failed:', error);
    } finally {
      setPurchaseLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'purchase':
        return 'fas fa-plus-circle text-success';
      case 'usage':
        return 'fas fa-minus-circle text-danger';
      case 'refund':
        return 'fas fa-undo text-warning';
      default:
        return 'fas fa-circle text-muted';
    }
  };

  const getTransactionLabel = (type) => {
    switch (type) {
      case 'purchase':
        return 'Purchase';
      case 'usage':
        return 'Usage';
      case 'refund':
        return 'Refund';
      default:
        return 'Transaction';
    }
  };

  const renderBalance = () => {
    return (
      <div className={`credit-balance ${variant} ${size} ${className}`}>
        <div className="balance-display">
          <div className="balance-icon">
            <i className="fas fa-coins"></i>
          </div>
          <div className="balance-info">
            <div className="balance-label">Available Credits</div>
            <div className="balance-amount">
              {loading ? (
                <div className="balance-loading">
                  <div className="spinner-border spinner-border-sm" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              ) : (
                <>
                  <span className="balance-number">{balance.toLocaleString()}</span>
                  <span className="balance-currency">credits</span>
                </>
              )}
            </div>
          </div>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="refresh-button"
              disabled={loading || disabled}
              title="Refresh balance"
            >
              <i className="fas fa-sync-alt"></i>
            </button>
          )}
        </div>

        {showPurchaseButton && (
          <div className="balance-actions">
            <button
              onClick={() => setShowPurchaseModal(true)}
              className="btn btn-primary purchase-button"
              disabled={disabled}
            >
              <i className="fas fa-plus"></i>
              Add Credits
            </button>
            {showHistory && (
              <button
                onClick={() => setShowHistoryModal(true)}
                className="btn btn-outline-secondary history-button"
                disabled={disabled}
              >
                <i className="fas fa-history"></i>
                History
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  const renderPurchaseModal = () => {
    if (!showPurchaseModal) return null;

    return (
      <div className="modal-overlay" onClick={() => setShowPurchaseModal(false)}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Purchase Credits</h3>
            <button
              onClick={() => setShowPurchaseModal(false)}
              className="modal-close"
              disabled={purchaseLoading}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          <div className="modal-body">
            <div className="package-grid">
              {purchaseOptions.map((pkg) => (
                <div
                  key={pkg.credits}
                  className={`package-card ${pkg.popular ? 'popular' : ''} ${
                    selectedPackage?.credits === pkg.credits ? 'selected' : ''
                  }`}
                  onClick={() => setSelectedPackage(pkg)}
                >
                  {pkg.popular && (
                    <div className="popular-badge">Most Popular</div>
                  )}
                  {pkg.discount && (
                    <div className="discount-badge">{pkg.discount}% OFF</div>
                  )}
                  <div className="package-credits">{pkg.credits.toLocaleString()}</div>
                  <div className="package-label">Credits</div>
                  <div className="package-price">
                    <span className="current-price">{formatCurrency(pkg.price)}</span>
                    {pkg.discount && (
                      <span className="original-price">
                        {formatCurrency(pkg.price / (1 - pkg.discount / 100))}
                      </span>
                    )}
                  </div>
                  <div className="package-rate">
                    {formatCurrency(pkg.price / pkg.credits)} per credit
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="modal-footer">
            <button
              onClick={() => setShowPurchaseModal(false)}
              className="btn btn-secondary"
              disabled={purchaseLoading}
            >
              Cancel
            </button>
            <button
              onClick={() => selectedPackage && handlePurchase(selectedPackage)}
              className="btn btn-primary"
              disabled={!selectedPackage || purchaseLoading}
            >
              {purchaseLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i>
                  Processing...
                </>
              ) : (
                `Purchase ${selectedPackage?.credits.toLocaleString()} Credits`
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderHistoryModal = () => {
    if (!showHistoryModal) return null;

    return (
      <div className="modal-overlay" onClick={() => setShowHistoryModal(false)}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Transaction History</h3>
            <button
              onClick={() => setShowHistoryModal(false)}
              className="modal-close"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          <div className="modal-body">
            <div className="transaction-list">
              {transactions.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-inbox"></i>
                  <p>No transactions found</p>
                </div>
              ) : (
                transactions.map((transaction) => (
                  <div key={transaction.id} className="transaction-item">
                    <div className="transaction-icon">
                      <i className={getTransactionIcon(transaction.type)}></i>
                    </div>
                    <div className="transaction-details">
                      <div className="transaction-title">
                        {getTransactionLabel(transaction.type)}
                        {transaction.description && (
                          <span className="transaction-description">
                            - {transaction.description}
                          </span>
                        )}
                      </div>
                      <div className="transaction-date">
                        {formatDate(transaction.date)}
                      </div>
                    </div>
                    <div className="transaction-amount">
                      <span className={`amount ${transaction.amount > 0 ? 'positive' : 'negative'}`}>
                        {transaction.amount > 0 ? '+' : ''}{transaction.amount.toLocaleString()}
                      </span>
                      {transaction.price && (
                        <span className="transaction-price">
                          {formatCurrency(transaction.price)}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
          
          <div className="modal-footer">
            <button
              onClick={() => setShowHistoryModal(false)}
              className="btn btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <>
      {renderBalance()}
      {renderPurchaseModal()}
      {renderHistoryModal()}
    </>
  );
};

export default CreditBalance; 