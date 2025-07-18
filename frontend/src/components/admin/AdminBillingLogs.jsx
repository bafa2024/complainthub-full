import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Admin.css';
import './AdminBillingLogs.css';

export default function AdminBillingLogs() {
  const [billingLogs, setBillingLogs] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [dateRange, setDateRange] = useState('30d');
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalTransactions: 0,
    pendingCharges: 0,
    activeSubscriptions: 0
  });

  useEffect(() => {
    fetchBillingLogs();
    fetchBrands();
    fetchBillingStats();
  }, [selectedBrand, dateRange, filterType, currentPage]);

  const fetchBillingLogs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: 20,
        offset: (currentPage - 1) * 20,
        date_range: dateRange
      });

      if (selectedBrand) params.append('brand_id', selectedBrand);
      if (filterType !== 'all') params.append('type', filterType);
      if (searchTerm) params.append('search', searchTerm);

      const response = await fetch(`/api/v1/billing/admin/billing-logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBillingLogs(data.transactions || []);
        setTotalPages(Math.ceil(data.total_count / 20));
      } else {
        console.error('Failed to fetch billing logs');
      }
    } catch (error) {
      console.error('Error fetching billing logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBrands = async () => {
    try {
      const response = await fetch('/api/v1/admin/brands', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBrands(data.brands || []);
      }
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const fetchBillingStats = async () => {
    try {
      const response = await fetch('/api/v1/analytics/billing/overview', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching billing stats:', error);
    }
  };

  const handleRefund = async (transactionId, reason) => {
    try {
      const response = await fetch(`/api/v1/billing/refund/${transactionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ reason })
      });

      if (response.ok) {
        alert('Refund processed successfully');
        fetchBillingLogs();
        fetchBillingStats();
      } else {
        alert('Failed to process refund');
      }
    } catch (error) {
      console.error('Error processing refund:', error);
      alert('Error processing refund');
    }
  };

  const handleExport = async () => {
    try {
      const params = new URLSearchParams({
        date_range: dateRange,
        format: 'csv'
      });

      if (selectedBrand) params.append('brand_id', selectedBrand);
      if (filterType !== 'all') params.append('type', filterType);

      const response = await fetch(`/api/v1/billing/admin/export?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `billing-logs-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        alert('Failed to export billing logs');
      }
    } catch (error) {
      console.error('Error exporting billing logs:', error);
      alert('Error exporting billing logs');
    }
  };

  const getTransactionTypeBadge = (type) => {
    const badges = {
      'credit_topup': 'success',
      'complaint_charge': 'danger',
      'subscription_payment': 'primary',
      'refund': 'warning',
      'adjustment': 'info'
    };
    return badges[type] || 'secondary';
  };

  const getStatusBadge = (status) => {
    const badges = {
      'completed': 'success',
      'pending': 'warning',
      'failed': 'danger',
      'cancelled': 'secondary',
      'refunded': 'info'
    };
    return badges[status] || 'secondary';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount);
  };

  return (
    <div className="container-fluid admin-container">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-2">Billing Management</h1>
          <p className="text-muted">Monitor and manage billing across all brands</p>
        </div>
        <div>
          <button className="btn btn-outline-primary me-2" onClick={handleExport}>
            <i className="fas fa-download me-2"></i>
            Export CSV
          </button>
          <Link to="/admin/dashboard" className="btn btn-secondary">
            <i className="fas fa-arrow-left me-2"></i>
            Back to Dashboard
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card stat-card">
            <div className="card-body">
              <div className="stat-icon revenue">
                <i className="fas fa-rupee-sign"></i>
              </div>
              <h3 className="stat-value">{formatCurrency(stats.totalRevenue)}</h3>
              <p className="stat-label">Total Revenue</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stat-card">
            <div className="card-body">
              <div className="stat-icon transactions">
                <i className="fas fa-exchange-alt"></i>
              </div>
              <h3 className="stat-value">{stats.totalTransactions}</h3>
              <p className="stat-label">Total Transactions</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stat-card">
            <div className="card-body">
              <div className="stat-icon pending">
                <i className="fas fa-clock"></i>
              </div>
              <h3 className="stat-value">{stats.pendingCharges}</h3>
              <p className="stat-label">Pending Charges</p>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card stat-card">
            <div className="card-body">
              <div className="stat-icon subscriptions">
                <i className="fas fa-credit-card"></i>
              </div>
              <h3 className="stat-value">{stats.activeSubscriptions}</h3>
              <p className="stat-label">Active Subscriptions</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <label className="form-label">Brand</label>
              <select 
                className="form-select"
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
              >
                <option value="">All Brands</option>
                {brands.map(brand => (
                  <option key={brand.id} value={brand.id}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Date Range</label>
              <select 
                className="form-select"
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
              >
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
                <option value="1y">Last Year</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Transaction Type</label>
              <select 
                className="form-select"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="all">All Types</option>
                <option value="credit_topup">Credit Top-up</option>
                <option value="complaint_charge">Complaint Charge</option>
                <option value="subscription_payment">Subscription Payment</option>
                <option value="refund">Refund</option>
                <option value="adjustment">Adjustment</option>
              </select>
            </div>
            <div className="col-md-3">
              <label className="form-label">Search</label>
              <input
                type="text"
                className="form-control"
                placeholder="Search transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Billing Logs Table */}
      <div className="card">
        <div className="card-header">
          <h4 className="mb-0">Billing Transactions</h4>
        </div>
        <div className="card-body">
          {loading ? (
            <div className="text-center py-4">
              <div className="spinner-border" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <>
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Brand</th>
                      <th>Type</th>
                      <th>Description</th>
                      <th>Amount</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {billingLogs.map(transaction => (
                      <tr key={transaction.id}>
                        <td>{new Date(transaction.created_at).toLocaleDateString()}</td>
                        <td>
                          <Link to={`/admin/brands/${transaction.brand_id}`}>
                            {transaction.brand_name || `Brand ${transaction.brand_id}`}
                          </Link>
                        </td>
                        <td>
                          <span className={`badge bg-${getTransactionTypeBadge(transaction.type)}`}>
                            {transaction.type.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>
                        <td>{transaction.description}</td>
                        <td className={transaction.amount < 0 ? 'text-danger' : 'text-success'}>
                          {formatCurrency(Math.abs(transaction.amount))}
                        </td>
                        <td>
                          <span className={`badge bg-${getStatusBadge(transaction.status)}`}>
                            {transaction.status}
                          </span>
                        </td>
                        <td>
                          <div className="btn-group btn-group-sm">
                            <button
                              className="btn btn-outline-primary"
                              onClick={() => {
                                const reason = prompt('Enter refund reason:');
                                if (reason) {
                                  handleRefund(transaction.id, reason);
                                }
                              }}
                              disabled={transaction.status !== 'completed' || transaction.type === 'refund'}
                              title="Process Refund"
                            >
                              <i className="fas fa-undo"></i>
                            </button>
                            <button
                              className="btn btn-outline-info"
                              onClick={() => {
                                // Generate invoice
                                window.open(`/api/v1/billing/invoice/${transaction.id}`, '_blank');
                              }}
                              title="Generate Invoice"
                            >
                              <i className="fas fa-file-invoice"></i>
                            </button>
                            <button
                              className="btn btn-outline-secondary"
                              onClick={() => {
                                // View details
                                alert(`Transaction Details:\nID: ${transaction.id}\nType: ${transaction.type}\nAmount: ${formatCurrency(transaction.amount)}\nStatus: ${transaction.status}\nCreated: ${new Date(transaction.created_at).toLocaleString()}`);
                              }}
                              title="View Details"
                            >
                              <i className="fas fa-eye"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <nav className="mt-4">
                  <ul className="pagination justify-content-center">
                    <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => setCurrentPage(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        Previous
                      </button>
                    </li>
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                      <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                        <button
                          className="page-link"
                          onClick={() => setCurrentPage(page)}
                        >
                          {page}
                        </button>
                      </li>
                    ))}
                    <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                      <button
                        className="page-link"
                        onClick={() => setCurrentPage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                      >
                        Next
                      </button>
                    </li>
                  </ul>
                </nav>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}