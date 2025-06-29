import React from 'react';
import { Link } from 'react-router-dom';
import './BrandDashboard.css';

const transactions = [
  { id: 1, date: '2024-06-01', type: 'Top Up', amount: 1000, status: 'Completed' },
  { id: 2, date: '2024-05-25', type: 'Complaint Charge', amount: -50, status: 'Completed' },
  { id: 3, date: '2024-05-20', type: 'Top Up', amount: 500, status: 'Completed' },
  { id: 4, date: '2024-05-18', type: 'Complaint Charge', amount: -50, status: 'Completed' },
];

export default function BrandBilling() {
  return (
    <div className="container-fluid brand-dashboard-container">
      <Link to="/brand/dashboard" className="btn btn-link mb-3">&larr; Back to Dashboard</Link>
      <h1 className="mb-4">Manage Billing</h1>

      {/* Credit Balance Card */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card stat-card-brand shadow-sm">
            <div className="card-body text-center">
              <div className="stat-icon credits mb-2" style={{ fontSize: 40 }}>&#128179;</div>
              <h6 className="text-muted mb-1">Current Credit Balance</h6>
              <h2 className="fw-bold mb-3">1,250</h2>
              <Link to="/brand/topup" className="btn btn-primary w-100">Top Up Credits</Link>
            </div>
          </div>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="card shadow-sm mb-4">
        <div className="card-header">
          <h4 className="mb-0">Recent Transactions</h4>
        </div>
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(tx => (
                  <tr key={tx.id}>
                    <td>{tx.date}</td>
                    <td>{tx.type}</td>
                    <td className={tx.amount < 0 ? 'text-danger' : 'text-success'}>
                      {tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount)}
                    </td>
                    <td><span className="badge bg-success">{tx.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Billing Info Section */}
      <div className="card shadow-sm mb-4">
        <div className="card-header">
          <h4 className="mb-0">How Billing Works</h4>
        </div>
        <div className="card-body">
          <ul className="mb-0">
            <li>Top up your credits to handle complaint charges and platform fees.</li>
            <li>Each unresolved complaint after 24 hours deducts $50 from your balance.</li>
            <li>Complaints resolved within 24 hours are free.</li>
            <li>Low balance alerts are sent when credits fall below $100.</li>
            <li>Contact support for billing questions or custom plans.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}