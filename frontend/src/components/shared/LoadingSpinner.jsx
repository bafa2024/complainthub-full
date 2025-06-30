import React from 'react';

export default function LoadingSpinner() {
  return (
    <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
      <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">Loading...</span>
      </div>
      <span className="ms-3">Loading...</span>
    </div>
  );
}