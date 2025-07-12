import React, { useState, useEffect, useRef } from 'react';
import './NotificationBell.css';

const NotificationBell = ({
  notifications = [],
  onNotificationClick,
  onMarkAllRead,
  onDeleteNotification,
  className = '',
  disabled = false,
  loading = false,
  maxNotifications = 10,
  showBadge = true,
  badgeCount = null,
  position = 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'top-left'
  size = 'medium' // 'small', 'medium', 'large'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const dropdownRef = useRef(null);

  // Calculate unread count
  useEffect(() => {
    const count = notifications.filter(notification => !notification.read).length;
    setUnreadCount(count);
  }, [notifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Close dropdown on escape key
  useEffect(() => {
    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [isOpen]);

  const handleToggle = () => {
    if (disabled || loading) return;
    setIsOpen(!isOpen);
  };

  const handleNotificationClick = (notification) => {
    onNotificationClick?.(notification);
    setIsOpen(false);
  };

  const handleMarkAllRead = () => {
    onMarkAllRead?.();
  };

  const handleDeleteNotification = (notificationId, event) => {
    event.stopPropagation();
    onDeleteNotification?.(notificationId);
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return 'fas fa-check-circle text-success';
      case 'error':
        return 'fas fa-exclamation-circle text-danger';
      case 'warning':
        return 'fas fa-exclamation-triangle text-warning';
      case 'info':
        return 'fas fa-info-circle text-info';
      case 'ticket':
        return 'fas fa-ticket-alt text-primary';
      case 'payment':
        return 'fas fa-credit-card text-success';
      case 'system':
        return 'fas fa-cog text-secondary';
      default:
        return 'fas fa-bell text-muted';
    }
  };

  const getNotificationClass = (type) => {
    switch (type) {
      case 'success':
        return 'notification-success';
      case 'error':
        return 'notification-error';
      case 'warning':
        return 'notification-warning';
      case 'info':
        return 'notification-info';
      case 'ticket':
        return 'notification-ticket';
      case 'payment':
        return 'notification-payment';
      case 'system':
        return 'notification-system';
      default:
        return 'notification-default';
    }
  };

  const formatTime = (timestamp) => {
    const now = new Date();
    const notificationTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - notificationTime) / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInMinutes < 1) {
      return 'Just now';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else if (diffInDays < 7) {
      return `${diffInDays}d ago`;
    } else {
      return notificationTime.toLocaleDateString();
    }
  };

  const displayCount = badgeCount !== null ? badgeCount : unreadCount;
  const hasNotifications = notifications.length > 0;
  const hasUnread = unreadCount > 0;

  return (
    <div className={`notification-bell ${className} ${size} ${position}`} ref={dropdownRef}>
      {/* Bell Button */}
      <button
        className={`bell-button ${isOpen ? 'active' : ''} ${hasUnread ? 'has-notifications' : ''}`}
        onClick={handleToggle}
        disabled={disabled}
        aria-label={`Notifications (${displayCount} unread)`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <i className="fas fa-bell"></i>
        
        {/* Badge */}
        {showBadge && displayCount > 0 && (
          <span className="notification-badge">
            {displayCount > 99 ? '99+' : displayCount}
          </span>
        )}
        
        {/* Loading Indicator */}
        {loading && (
          <div className="loading-indicator">
            <div className="spinner-border spinner-border-sm" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="notification-dropdown">
          <div className="dropdown-header">
            <h3>Notifications</h3>
            {hasUnread && (
              <button
                onClick={handleMarkAllRead}
                className="mark-all-read"
                title="Mark all as read"
              >
                <i className="fas fa-check-double"></i>
                Mark all read
              </button>
            )}
          </div>

          <div className="notification-list">
            {!hasNotifications ? (
              <div className="empty-state">
                <i className="fas fa-bell-slash"></i>
                <p>No notifications</p>
                <span>You're all caught up!</span>
              </div>
            ) : (
              notifications.slice(0, maxNotifications).map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item ${getNotificationClass(notification.type)} ${
                    !notification.read ? 'unread' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  <div className="notification-icon">
                    <i className={getNotificationIcon(notification.type)}></i>
                  </div>
                  
                  <div className="notification-content">
                    <div className="notification-title">
                      {notification.title}
                    </div>
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    <div className="notification-time">
                      {formatTime(notification.timestamp)}
                    </div>
                  </div>
                  
                  <div className="notification-actions">
                    {!notification.read && (
                      <div className="unread-indicator"></div>
                    )}
                    <button
                      onClick={(e) => handleDeleteNotification(notification.id, e)}
                      className="delete-notification"
                      title="Delete notification"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {hasNotifications && notifications.length > maxNotifications && (
            <div className="dropdown-footer">
              <button className="view-all-notifications">
                View all notifications ({notifications.length})
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Notification Item Component
export const NotificationItem = ({ notification, onClick, onDelete }) => {
  const handleClick = () => {
    onClick?.(notification);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    onDelete?.(notification.id);
  };

  return (
    <div
      className={`notification-item ${!notification.read ? 'unread' : ''}`}
      onClick={handleClick}
    >
      <div className="notification-icon">
        <i className={`fas fa-${notification.icon || 'bell'}`}></i>
      </div>
      
      <div className="notification-content">
        <div className="notification-title">{notification.title}</div>
        <div className="notification-message">{notification.message}</div>
        <div className="notification-time">
          {new Date(notification.timestamp).toLocaleString()}
        </div>
      </div>
      
      {onDelete && (
        <button onClick={handleDelete} className="delete-notification">
          <i className="fas fa-times"></i>
        </button>
      )}
    </div>
  );
};

export default NotificationBell; 