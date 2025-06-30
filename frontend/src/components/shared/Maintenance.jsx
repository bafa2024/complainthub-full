import React, { useState, useEffect } from 'react';
import './Maintenance.css';

export default function Maintenance() {
  const [countdown, setCountdown] = useState({
    hours: 2,
    minutes: 30,
    seconds: 0
  });

  const [progress, setProgress] = useState(65);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(prev => {
        let { hours, minutes, seconds } = prev;
        
        if (seconds > 0) {
          seconds--;
        } else if (minutes > 0) {
          minutes--;
          seconds = 59;
        } else if (hours > 0) {
          hours--;
          minutes = 59;
          seconds = 59;
        }
        
        return { hours, minutes, seconds };
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const features = [
    'Enhanced complaint tracking system',
    'Improved AI-powered response generation',
    'Better mobile responsiveness',
    'Advanced analytics dashboard',
    'Real-time notification system',
    'Enhanced security features'
  ];

  const contactMethods = [
    { icon: '📧', method: 'Email', value: 'support@complainthub.com' },
    { icon: '📱', method: 'WhatsApp', value: '+1 (555) 123-4567' },
    { icon: '💬', method: 'Live Chat', value: 'Available 24/7' }
  ];

  return (
    <div className="maintenance-page">
      <div className="maintenance-container">
        <div className="maintenance-icon">🔧</div>
        
        <h1 className="maintenance-title">Under Maintenance</h1>
        <p className="maintenance-message">
          We're currently performing scheduled maintenance to improve your experience. 
          We apologize for any inconvenience and appreciate your patience.
        </p>

        <div className="progress-container">
          <div 
            className="progress-bar" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>

        <div className="estimated-time">
          Estimated completion time: 2 hours 30 minutes
        </div>

        <div className="countdown">
          {String(countdown.hours).padStart(2, '0')}:{String(countdown.minutes).padStart(2, '0')}:{String(countdown.seconds).padStart(2, '0')}
        </div>

        <div className="features-update">
          <h3 className="features-title">What's Being Updated</h3>
          <div className="features-list">
            {features.map((feature, index) => (
              <div key={index} className="feature-item">
                <span className="feature-check">✓</span>
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="contact-info">
          <h3 className="contact-title">Need Immediate Assistance?</h3>
          <div className="contact-methods">
            {contactMethods.map((contact, index) => (
              <div key={index} className="contact-item">
                <span className="contact-icon">{contact.icon}</span>
                <div className="contact-details">
                  <div className="contact-method">{contact.method}</div>
                  <div className="contact-value">{contact.value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="status-updates">
          <h3 className="status-title">Latest Updates</h3>
          <div className="status-timeline">
            <div className="status-item completed">
              <div className="status-time">10:00 AM</div>
              <div className="status-message">Maintenance started - Database optimization in progress</div>
            </div>
            <div className="status-item completed">
              <div className="status-time">10:30 AM</div>
              <div className="status-message">Database optimization completed - UI updates in progress</div>
            </div>
            <div className="status-item current">
              <div className="status-time">11:15 AM</div>
              <div className="status-message">UI updates 65% complete - Testing phase starting soon</div>
            </div>
            <div className="status-item pending">
              <div className="status-time">12:30 PM</div>
              <div className="status-message">Testing phase - Final verification</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 