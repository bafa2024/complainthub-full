import React, { useState, useEffect } from 'react';
import brandService from '../../services/brandService';

export default function BrandBilling() {
  const [creditBalance, setCreditBalance] = useState(2450);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState('500');

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      // Mock data for now
      setTransactions([
        {
          id: 1,
          date: '2024-12-15',
          description: 'Complaint charge - Exceeded 24h',
          ticketId: 'CMP-2024-089',
          amount: -50,
          balance: 2450
        },
        {
          id: 2,
          date: '2024-12-14',
          description: 'Credit top-up',
          ticketId: null,
          amount: 500,
          balance: 2500
        },
        {
          id: 3,
          date: '2024-12-13',
          description: 'Complaint charge - Exceeded 24h',
          ticketId: 'CMP-2024-087',
          amount: -50,
          balance: 2000
        },
        {
          id: 4,
          date: '2024-12-12',
          description: 'Complaint charge - Exceeded 24h',
          ticketId: 'CMP-2024-085',
          amount: -50,
          balance: 2050
        },
        {
          id: 5,
          date: '2024-12-10',
          description: 'Credit top-up',
          ticketId: null,
          amount: 1000,
          balance: 2100
        }
      ]);
    } catch (error) {
      console.error('Failed to load billing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTopUp = async () => {
    try {
      // In production, this would integrate with payment gateway
      await brandService.addCredits(1, parseFloat(topUpAmount));
      setCreditBalance(prev => prev + parseFloat(topUpAmount));
      setShowTopUpModal(false);
      alert('Credits added successfully!');
      loadBillingData();
    } catch (error) {
      console.error('Failed to add credits:', error);
      alert('Failed to add credits. Please try again.');
    }
  };

  const getTransactionColor = (amount) => {
    return amount < 0 ? '#e74c3c' : '#27ae60';
  };

  if (loading) {
    return <div style={styles.loading}>Loading billing information...</div>;
  }

  return (
    <div style={styles.container}>
      {/* Credit Balance Card */}
      <div style={styles.balanceCard}>
        <div style={styles.balanceContent}>
          <div>
            <div style={styles.balanceLabel}>Available Credits</div>
            <div style={styles.balanceAmount}>₹ {creditBalance.toLocaleString()}</div>
            <div style={styles.balanceNote}>
              Charges apply only for unresolved complaints after 24 hours
            </div>
          </div>
          <button 
            style={styles.topUpBtn}
            onClick={() => setShowTopUpModal(true)}
          >
            + Add Credits
          </button>
        </div>
        
        {creditBalance < 500 && (
          <div style={styles.lowBalanceWarning}>
            ⚠️ Low balance alert! Top up to avoid service interruption.
          </div>
        )}
      </div>

      {/* Billing Stats */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>📊</div>
          <div style={styles.statValue}>₹850</div>
          <div style={styles.statLabel}>This Month's Charges</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>💳</div>
          <div style={styles.statValue}>17</div>
          <div style={styles.statLabel}>Charged Complaints</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>✅</div>
          <div style={styles.statValue}>142</div>
          <div style={styles.statLabel}>Free Resolutions</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statIcon}>📈</div>
          <div style={styles.statValue}>89.3%</div>
          <div style={styles.statLabel}>Free Resolution Rate</div>
        </div>
      </div>

      {/* Transaction History */}
      <div style={styles.section}>
        <div style={styles.sectionHeader}>
          <h3 style={styles.sectionTitle}>Transaction History</h3>
          <button style={styles.downloadBtn}>
            📥 Download Statement
          </button>
        </div>
        
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Date</th>
                <th style={styles.th}>Description</th>
                <th style={styles.th}>Ticket ID</th>
                <th style={styles.th}>Amount</th>
                <th style={styles.th}>Balance</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td style={styles.td}>{transaction.date}</td>
                  <td style={styles.td}>{transaction.description}</td>
                  <td style={styles.td}>
                    {transaction.ticketId ? (
                      <a href={`/brand/ticket/${transaction.ticketId}`} style={styles.ticketLink}>
                        #{transaction.ticketId}
                      </a>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td style={{
                    ...styles.td,
                    color: getTransactionColor(transaction.amount),
                    fontWeight: '600'
                  }}>
                    {transaction.amount > 0 ? '+' : ''}₹{Math.abs(transaction.amount)}
                  </td>
                  <td style={styles.td}>₹{transaction.balance}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div style={styles.pagination}>
          <button style={styles.pageBtn}>Previous</button>
          <span style={styles.pageInfo}>Page 1 of 5</span>
          <button style={styles.pageBtn}>Next</button>
        </div>
      </div>

      {/* Billing Information */}
      <div style={styles.billingInfo}>
        <h3 style={styles.sectionTitle}>Billing Information</h3>
        <div style={styles.infoGrid}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Charge per Complaint</span>
            <span style={styles.infoValue}>₹50</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Free Resolution Window</span>
            <span style={styles.infoValue}>24 hours</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Billing Cycle</span>
            <span style={styles.infoValue}>Pay-as-you-go</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Payment Method</span>
            <span style={styles.infoValue}>Credit Balance</span>
          </div>
        </div>
        
        <div style={styles.faqSection}>
          <h4 style={styles.faqTitle}>How Billing Works</h4>
          <ul style={styles.faqList}>
            <li>Feedback, suggestions, and support tickets are always free</li>
            <li>Complaints resolved within 24 hours incur no charges</li>
            <li>Unresolved complaints after 24 hours are charged ₹50 each</li>
            <li>Credits are automatically deducted from your balance</li>
            <li>Low balance alerts are sent when credits fall below ₹500</li>
          </ul>
        </div>
      </div>

      {/* Top-up Modal */}
      {showTopUpModal && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <div style={styles.modalHeader}>
              <h3 style={styles.modalTitle}>Add Credits</h3>
              <button 
                style={styles.modalClose}
                onClick={() => setShowTopUpModal(false)}
              >
                ×
              </button>
            </div>
            
            <div style={styles.amountOptions}>
              <button 
                style={topUpAmount === '500' ? styles.amountBtnActive : styles.amountBtn}
                onClick={() => setTopUpAmount('500')}
              >
                ₹500
              </button>
              <button 
                style={topUpAmount === '1000' ? styles.amountBtnActive : styles.amountBtn}
                onClick={() => setTopUpAmount('1000')}
              >
                ₹1,000
              </button>
              <button 
                style={topUpAmount === '2500' ? styles.amountBtnActive : styles.amountBtn}
                onClick={() => setTopUpAmount('2500')}
              >
                ₹2,500
              </button>
              <button 
                style={topUpAmount === '5000' ? styles.amountBtnActive : styles.amountBtn}
                onClick={() => setTopUpAmount('5000')}
              >
                ₹5,000
              </button>
            </div>
            
            <div style={styles.customAmount}>
              <label style={styles.customLabel}>Or enter custom amount:</label>
              <input 
                type="number"
                value={topUpAmount}
                onChange={(e) => setTopUpAmount(e.target.value)}
                style={styles.customInput}
                min="100"
                step="100"
              />
            </div>
            
            <div style={styles.summary}>
              <div style={styles.summaryRow}>
                <span>Credits to add:</span>
                <span>₹{topUpAmount}</span>
              </div>
              <div style={styles.summaryRow}>
                <span>GST (18%):</span>
                <span>₹{(parseFloat(topUpAmount) * 0.18).toFixed(2)}</span>
              </div>
              <div style={{...styles.summaryRow, ...styles.summaryTotal}}>
                <span>Total Amount:</span>
                <span>₹{(parseFloat(topUpAmount) * 1.18).toFixed(2)}</span>
              </div>
            </div>
            
            <button 
              style={styles.payBtn}
              onClick={handleTopUp}
            >
              Proceed to Payment
            </button>
            
            <p style={styles.paymentNote}>
              You will be redirected to secure payment gateway
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    padding: '20px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  loading: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
    fontSize: '18px',
    color: '#7f8c8d',
  },
  balanceCard: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: '30px',
    borderRadius: '12px',
    marginBottom: '30px',
    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
  },
  balanceContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  balanceLabel: {
    fontSize: '18px',
    marginBottom: '10px',
    opacity: 0.9,
  },
  balanceAmount: {
    fontSize: '48px',
    fontWeight: '700',
    marginBottom: '10px',
  },
  balanceNote: {
    fontSize: '14px',
    opacity: 0.8,
  },
  topUpBtn: {
    background: 'white',
    color: '#667eea',
    padding: '12px 24px',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
  },
  lowBalanceWarning: {
    background: 'rgba(255,255,255,0.2)',
    padding: '15px',
    borderRadius: '8px',
    marginTop: '20px',
    fontSize: '14px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px',
  },
  statCard: {
    background: 'white',
    padding: '25px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    textAlign: 'center',
  },
  statIcon: {
    fontSize: '32px',
    marginBottom: '10px',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#2c3e50',
    marginBottom: '5px',
  },
  statLabel: {
    color: '#7f8c8d',
    fontSize: '14px',
  },
  section: {
    background: 'white',
    padding: '25px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
    marginBottom: '20px',
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#2c3e50',
  },
  downloadBtn: {
    padding: '8px 16px',
    background: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '600',
    fontSize: '14px',
  },
  tableContainer: {
    overflowX: 'auto',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
  },
  th: {
    background: '#f8f9fa',
    padding: '12px',
    textAlign: 'left',
    fontWeight: '600',
    color: '#495057',
    borderBottom: '2px solid #dee2e6',
  },
  td: {
    padding: '12px',
    borderBottom: '1px solid #dee2e6',
  },
  ticketLink: {
    color: '#3498db',
    textDecoration: 'none',
    fontWeight: '500',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '20px',
    marginTop: '20px',
  },
  pageBtn: {
    padding: '8px 16px',
    border: '1px solid #ddd',
    background: 'white',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
  },
  pageInfo: {
    color: '#7f8c8d',
  },
  billingInfo: {
    background: 'white',
    padding: '25px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '30px',
  },
  infoItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '15px',
    background: '#f8f9fa',
    borderRadius: '6px',
  },
  infoLabel: {
    color: '#7f8c8d',
    fontSize: '14px',
  },
  infoValue: {
    fontWeight: '600',
    color: '#2c3e50',
    fontSize: '14px',
  },
  faqSection: {
    marginTop: '30px',
  },
  faqTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#2c3e50',
    marginBottom: '15px',
  },
  faqList: {
    paddingLeft: '25px',
    lineHeight: 1.8,
    color: '#495057',
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0,0,0,0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    background: 'white',
    padding: '30px',
    borderRadius: '12px',
    maxWidth: '500px',
    width: '90%',
  },
  modalHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  modalTitle: {
    fontSize: '24px',
    fontWeight: '600',
    color: '#2c3e50',
  },
  modalClose: {
    background: 'none',
    border: 'none',
    fontSize: '28px',
    color: '#7f8c8d',
    cursor: 'pointer',
  },
  amountOptions: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '10px',
    marginBottom: '20px',
  },
  amountBtn: {
    padding: '15px',
    border: '2px solid #ddd',
    background: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
    transition: 'all 0.3s',
  },
  amountBtnActive: {
    padding: '15px',
    border: '2px solid #667eea',
    background: '#667eea',
    color: 'white',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  customAmount: {
    marginBottom: '20px',
  },
  customLabel: {
    display: 'block',
    marginBottom: '10px',
    fontWeight: '600',
    color: '#495057',
  },
  customInput: {
    width: '100%',
    padding: '12px',
    border: '1px solid #ddd',
    borderRadius: '6px',
    fontSize: '16px',
  },
  summary: {
    background: '#f8f9fa',
    padding: '20px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  summaryRow: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '10px',
    fontSize: '14px',
    color: '#495057',
  },
  summaryTotal: {
    paddingTop: '10px',
    borderTop: '1px solid #dee2e6',
    fontWeight: '600',
    fontSize: '16px',
    color: '#2c3e50',
  },
  payBtn: {
    width: '100%',
    padding: '14px',
    background: '#27ae60',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  paymentNote: {
    textAlign: 'center',
    marginTop: '15px',
    fontSize: '14px',
    color: '#7f8c8d',
  },
};