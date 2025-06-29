import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './BrandDashboard.css';

const packages = [
  { credits: 500, price: 50 },
  { credits: 1000, price: 90 },
  { credits: 2000, price: 170 },
];

export default function TopUpCredit() {
  const [selected, setSelected] = useState(packages[1]);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      // In a real implementation, this would integrate with a payment gateway
      // For now, we'll simulate the API call
      const response = await fetch('/api/v1/billing/topup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          credits: selected.credits,
          amount: selected.price
        })
      });

      if (response.ok) {
        navigate('/brand/billing');
      } else {
        throw new Error('Payment failed');
      }
    } catch (err) {
      console.error('Payment error:', err);
      setError('Payment processing failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const handleProceed = (e) => {
    e.preventDefault();
    navigate('/brand/proceed-payment', { state: { selectedPackage: selected } });
  };

  return (
    <div className="container-fluid brand-dashboard-container">
      <Link to="/brand/billing" className="btn btn-link mb-3">&larr; Back to Billing</Link>
      <h1 className="mb-4">Top Up Credits</h1>
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow-sm">
            <div className="card-body">
              <form onSubmit={handleProceed}>
                <h4 className="mb-4">Select a Credit Package</h4>
                <div className="list-group mb-4">
                  {packages.map(pkg => (
                    <label key={pkg.credits} className={`list-group-item d-flex justify-content-between align-items-center ${selected.credits === pkg.credits ? 'active' : ''}`} style={{ cursor: 'pointer' }}>
                      <div>
                        <input
                          type="radio"
                          name="creditPackage"
                          value={pkg.credits}
                          checked={selected.credits === pkg.credits}
                          onChange={() => setSelected(pkg)}
                          className="form-check-input me-2"
                        />
                        <span className="fw-bold">{pkg.credits.toLocaleString()} Credits</span>
                      </div>
                      <span className="badge bg-primary fs-6">${pkg.price}</span>
                    </label>
                  ))}
                </div>
                <div className="mb-4 p-3 rounded bg-light border">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>Selected Package:</span>
                    <span className="fw-bold">{selected.credits.toLocaleString()} Credits</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <span>Total Price:</span>
                    <span className="fw-bold text-primary fs-5">${selected.price}</span>
                  </div>
                </div>
                <button type="submit" className="btn btn-primary w-100" disabled={processing}>
                  Proceed to Payment
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 