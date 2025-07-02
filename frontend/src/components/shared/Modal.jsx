import React from 'react';

const Modal = ({ onClose, title, children }) => {
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0,0,0,0.4)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: '#fff',
        borderRadius: '8px',
        minWidth: '320px',
        maxWidth: '90vw',
        padding: '2rem',
        boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
        position: 'relative'
      }}>
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            background: 'transparent',
            border: 'none',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: '#888'
          }}
          aria-label="Close"
        >
          &times;
        </button>
        {title && <h2 style={{ marginTop: 0 }}>{title}</h2>}
        <div>{children}</div>
      </div>
    </div>
  );
};

export default Modal;
