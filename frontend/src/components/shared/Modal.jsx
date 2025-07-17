import React, { useEffect, useRef } from 'react';
import './Modal.css';

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  className = '',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  type = 'default', // 'default', 'confirm', 'alert', 'form'
  loading = false,
  disabled = false
}) => {
  const modalRef = useRef(null);
  const overlayRef = useRef(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
      }
    };

    const handleClickOutside = (e) => {
      if (e.target === overlayRef.current && closeOnOverlayClick) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('mousedown', handleClickOutside);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, closeOnEscape, closeOnOverlayClick]);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (!disabled && !loading && onConfirm) {
      onConfirm();
    }
  };

  const handleCancel = () => {
    if (!disabled && !loading) {
      if (onCancel) {
        onCancel();
      } else {
        onClose();
      }
    }
  };

  const getModalIcon = () => {
    switch (type) {
      case 'confirm':
        return <i className="fas fa-question-circle modal-icon confirm"></i>;
      case 'alert':
        return <i className="fas fa-exclamation-triangle modal-icon alert"></i>;
      case 'success':
        return <i className="fas fa-check-circle modal-icon success"></i>;
      case 'error':
        return <i className="fas fa-times-circle modal-icon error"></i>;
      case 'warning':
        return <i className="fas fa-exclamation-circle modal-icon warning"></i>;
      default:
        return null;
    }
  };

  const getModalClass = () => {
    const baseClass = `modal-content modal-${size} modal-${type}`;
    return `${baseClass} ${className}`.trim();
  };

  return (
    <div className="modal-overlay" ref={overlayRef}>
      <div 
        className={getModalClass()} 
        ref={modalRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? "modal-title" : undefined}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="modal-header">
            {getModalIcon()}
            {title && (
              <h2 id="modal-title" className="modal-title">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="modal-close"
                aria-label="Close modal"
                disabled={disabled || loading}
              >
                <i className="fas fa-times"></i>
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className="modal-body">
          {children}
        </div>

        {/* Footer */}
        {(type === 'confirm' || onConfirm || onCancel) && (
          <div className="modal-footer">
            {type === 'confirm' && (
              <button
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={disabled || loading}
              >
                {cancelText}
              </button>
            )}
            {onConfirm && (
              <button
                onClick={handleConfirm}
                className={`btn btn-primary ${type === 'confirm' ? 'btn-confirm' : ''}`}
                disabled={disabled || loading}
              >
                {loading ? (
                  <>
                    <i className="fas fa-spinner fa-spin"></i>
                    Loading...
                  </>
                ) : (
                  confirmText
                )}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Confirmation Modal Component
export const ConfirmModal = ({ 
  isOpen, 
  onClose, 
  title = 'Confirm Action', 
  message, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  onConfirm,
  type = 'confirm',
  loading = false,
  disabled = false
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      type={type}
      confirmText={confirmText}
      cancelText={cancelText}
      onConfirm={onConfirm}
      onCancel={onClose}
      loading={loading}
      disabled={disabled}
    >
      <div className="confirm-message">
        {message}
      </div>
    </Modal>
  );
};

// Alert Modal Component
export const AlertModal = ({ 
  isOpen, 
  onClose, 
  title = 'Alert', 
  message, 
  type = 'alert',
  confirmText = 'OK'
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      type={type}
      confirmText={confirmText}
      onConfirm={onClose}
      showCloseButton={false}
      closeOnOverlayClick={false}
    >
      <div className="alert-message">
        {message}
      </div>
    </Modal>
  );
};

// Form Modal Component
export const FormModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  onSubmit,
  submitText = 'Submit',
  cancelText = 'Cancel',
  loading = false,
  disabled = false
}) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!disabled && !loading && onSubmit) {
      onSubmit(e);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      type="form"
      confirmText={submitText}
      cancelText={cancelText}
      onConfirm={handleSubmit}
      onCancel={onClose}
      loading={loading}
      disabled={disabled}
    >
      <form onSubmit={handleSubmit} className="modal-form">
        {children}
      </form>
    </Modal>
  );
};

export default Modal;
