import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TestUtils } from '../../utils/testUtils';
import './ContactPage.css';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
    category: 'general'
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [testResults, setTestResults] = useState([]);

  // Contact methods
  const contactMethods = [
    {
      icon: '📧',
      title: 'Email Support',
      description: 'Get help via email',
      value: 'support@complainthub.com',
      action: 'mailto:support@complainthub.com'
    },
    {
      icon: '📱',
      title: 'WhatsApp',
      description: 'Chat with us on WhatsApp',
      value: '+1 (555) 123-4567',
      action: 'https://wa.me/15551234567'
    },
    {
      icon: '💬',
      title: 'Live Chat',
      description: 'Available 24/7',
      value: 'Start Chat',
      action: '#live-chat'
    },
    {
      icon: '📞',
      title: 'Phone Support',
      description: 'Call us directly',
      value: '+1 (555) 123-4567',
      action: 'tel:+15551234567'
    }
  ];

  // FAQ data
  const faqs = [
    {
      question: 'How do I lodge a complaint?',
      answer: 'You can lodge a complaint through multiple channels: voice call, WhatsApp, Telegram, web chat, or our website. Simply choose your preferred method and follow the guided process.'
    },
    {
      question: 'How long does it take to resolve a complaint?',
      answer: 'Resolution times vary depending on the complexity of the issue and brand responsiveness. Most complaints are resolved within 3-7 business days.'
    },
    {
      question: 'Can I remain anonymous when filing a complaint?',
      answer: 'Yes, you can choose to file complaints anonymously. However, providing contact information helps us keep you updated on the progress.'
    },
    {
      question: 'What if a brand doesn\'t respond to my complaint?',
      answer: 'If a brand doesn\'t respond within the specified timeframe, your complaint becomes public on our platform, which often encourages faster resolution.'
    },
    {
      question: 'Is my personal information secure?',
      answer: 'Yes, we use enterprise-grade security measures to protect your personal information. We never share your data without your explicit consent.'
    },
    {
      question: 'Can I track the status of my complaint?',
      answer: 'Yes, you can track your complaint status in real-time through your dashboard or by using the tracking number provided when you filed the complaint.'
    }
  ];

  // Form validation rules
  const validationRules = {
    name: { required: true, minLength: 2, maxLength: 50 },
    email: { required: true, email: true },
    phone: { required: false },
    subject: { required: true, minLength: 5, maxLength: 100 },
    message: { required: true, minLength: 10, maxLength: 1000 },
    category: { required: true }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Run form validation test
    const validationTest = TestUtils.testFormValidation(formData, validationRules);
    setTestResults(prev => [...prev, { name: 'Form Validation', ...validationTest }]);
    
    if (!validationTest.success) {
      setSubmitStatus({ type: 'error', message: validationTest.errors.join(', ') });
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Run performance test
      const performanceTest = TestUtils.testPerformance(() => {
        // Simulate form processing
        console.log('Processing form data:', formData);
      });
      setTestResults(prev => [...prev, { name: 'Form Performance', ...performanceTest }]);
      
      setSubmitStatus({ 
        type: 'success', 
        message: 'Thank you! Your message has been sent successfully. We\'ll get back to you within 24 hours.' 
      });
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: '',
        category: 'general'
      });
      
    } catch (error) {
      setSubmitStatus({ 
        type: 'error', 
        message: 'Sorry, there was an error sending your message. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Run component tests on mount
  useEffect(() => {
    const runComponentTests = async () => {
      const tests = [
        {
          name: 'Local Storage Test',
          fn: () => TestUtils.testLocalStorage()
        },
        {
          name: 'Responsive Design Test',
          fn: () => TestUtils.testResponsiveDesign()
        }
      ];
      
      const results = await TestUtils.runTestSuite(tests);
      setTestResults(results.results);
    };
    
    runComponentTests();
  }, []);

  return (
    <div className="contact-page">
      {/* Header */}
      <div className="contact-header">
        <div className="header-container">
          <div className="logo">ComplaintHub</div>
          <div className="header-nav">
            <Link to="/" className="btn btn-outline">Back to Home</Link>
          </div>
        </div>
      </div>

      <div className="main-container">
        {/* Hero Section */}
        <div className="contact-hero">
          <h1>Get in Touch</h1>
          <p>We're here to help! Contact us through any of the methods below or fill out the form.</p>
        </div>

        {/* Contact Methods Grid */}
        <div className="contact-methods">
          <h2>Contact Methods</h2>
          <div className="methods-grid">
            {contactMethods.map((method, index) => (
              <div key={index} className="method-card">
                <div className="method-icon">{method.icon}</div>
                <h3>{method.title}</h3>
                <p>{method.description}</p>
                <a 
                  href={method.action} 
                  className="method-link"
                  target={method.action.startsWith('http') ? '_blank' : '_self'}
                  rel={method.action.startsWith('http') ? 'noopener noreferrer' : ''}
                >
                  {method.value}
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* Contact Form */}
        <div className="contact-form-section">
          <h2>Send us a Message</h2>
          <form onSubmit={handleSubmit} className="contact-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your full name"
                />
              </div>
              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter your email address"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="Enter your phone number"
                />
              </div>
              <div className="form-group">
                <label htmlFor="category">Category *</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                >
                  <option value="general">General Inquiry</option>
                  <option value="technical">Technical Support</option>
                  <option value="billing">Billing Question</option>
                  <option value="complaint">Complaint About Service</option>
                  <option value="partnership">Partnership Inquiry</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="subject">Subject *</label>
              <input
                type="text"
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleInputChange}
                required
                placeholder="Brief description of your inquiry"
              />
            </div>

            <div className="form-group">
              <label htmlFor="message">Message *</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                required
                rows="6"
                placeholder="Please provide details about your inquiry..."
              ></textarea>
            </div>

            {submitStatus && (
              <div className={`alert alert-${submitStatus.type}`}>
                {submitStatus.message}
              </div>
            )}

            <button 
              type="submit" 
              className="btn btn-primary btn-lg"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>
        </div>

        {/* FAQ Section */}
        <div className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-grid">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <h3>{faq.question}</h3>
                <p>{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Test Results (Development Only) */}
        {process.env.NODE_ENV === 'development' && testResults.length > 0 && (
          <div className="test-results">
            <h3>Component Tests</h3>
            <div className="test-grid">
              {testResults.map((test, index) => (
                <div key={index} className={`test-item ${test.success ? 'success' : 'error'}`}>
                  <strong>{test.name}:</strong> {test.message}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 