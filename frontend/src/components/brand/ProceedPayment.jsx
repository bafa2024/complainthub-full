import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';

export default function ProceedPayment() {
  const location = useLocation();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Get selected package from location state
  const selected = location.state?.selectedPackage;

  useEffect(() => {
    if (!selected) {
      // If no package, redirect back to topup
      navigate('/brand/topup');
    }
  }, [selected, navigate]);

  const handlePayNow = async () => {
    setProcessing(true);
    setError('');
    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSuccess(true);
      setTimeout(() => {
        navigate('/brand/billing', { state: { paymentSuccess: true } });
      }, 1500);
    } catch (err) {
      setError('Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  if (!selected) return null;

  return (
    <div className="container-fluid brand-dashboard-container">
      <Link to="/brand/topup" className="btn btn-link mb-3">&larr; Back to Top Up</Link>
      <h1 className="mb-4">Proceed to Payment</h1>
      <div className="row justify-content-center">
        <div className="col-md-6 col-lg-5">
          <div className="card shadow-sm">
            <div className="card-body">
              <h4 className="mb-4">Confirm Your Top-Up</h4>
              <div className="mb-4 p-3 rounded bg-light border">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <span>Credits:</span>
                  <span className="fw-bold">{selected.credits.toLocaleString()} Credits</span>
                </div>
                <div className="d-flex justify-content-between align-items-center">
                  <span>Total Price:</span>
                  <span className="fw-bold text-primary fs-5">${selected.price}</span>
                </div>
              </div>
              {error && <div className="alert alert-danger">{error}</div>}
              {success ? (
                <div className="alert alert-success">Payment successful! Redirecting...</div>
              ) : (
                <button
                  className="btn btn-success w-100 mb-2"
                  onClick={handlePayNow}
                  disabled={processing}
                >
                  {processing ? 'Processing Payment...' : 'Pay Now'}
                </button>
              )}
              <Link to="/brand/topup" className="btn btn-outline-secondary w-100">Back</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 