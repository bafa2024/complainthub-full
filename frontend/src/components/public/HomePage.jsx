import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const [activeTab, setActiveTab] = useState('monthly');

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Customer Service Manager",
      company: "TechCorp",
      content: "ComplaintHub has revolutionized how we handle customer feedback. The AI-powered system ensures no complaint goes unnoticed.",
      rating: 5
    },
    {
      name: "Michael Chen",
      role: "Small Business Owner",
      company: "LocalMart",
      content: "As a small business, we couldn't afford expensive CRM systems. ComplaintHub gives us enterprise-level complaint management.",
      rating: 5
    },
    {
      name: "Emily Rodriguez",
      role: "Consumer Advocate",
      company: "Consumer Rights",
      content: "Finally, a platform that gives consumers real power. The public visibility feature ensures brands take complaints seriously.",
      rating: 5
    }
  ];

  const features = [
    {
      icon: "🤖",
      title: "AI-Powered Bot",
      description: "Our intelligent voice and chatbot captures your complaint details accurately, 24/7, ensuring nothing gets lost in translation."
    },
    {
      icon: "👁️",
      title: "Public Visibility",
      description: "Unresolved complaints are made public to encourage brands to respond quickly and maintain their reputation."
    },
    {
      icon: "📱",
      title: "Multi-Channel Support",
      description: "Lodge your complaint via Phone Call, WhatsApp, Telegram, Web Chat, and more - whatever's convenient for you."
    },
    {
      icon: "📊",
      title: "Analytics Dashboard",
      description: "Comprehensive analytics and reporting tools to track complaint resolution times and customer satisfaction."
    },
    {
      icon: "🔒",
      title: "Secure & Private",
      description: "Your data is protected with enterprise-grade security. We never share your personal information without consent."
    },
    {
      icon: "⚡",
      title: "Real-time Updates",
      description: "Get instant notifications on complaint status updates, brand responses, and resolution progress."
    }
  ];

  const pricingPlans = {
    monthly: [
      {
        name: "Starter",
        price: "$29",
        period: "/month",
        features: ["Up to 100 complaints/month", "Basic AI bot", "Email support", "Standard analytics"],
        popular: false
      },
      {
        name: "Professional",
        price: "$79",
        period: "/month",
        features: ["Up to 500 complaints/month", "Advanced AI bot", "Priority support", "Advanced analytics", "Multi-channel integration"],
        popular: true
      },
      {
        name: "Enterprise",
        price: "$199",
        period: "/month",
        features: ["Unlimited complaints", "Custom AI training", "24/7 support", "Custom integrations", "White-label options"],
        popular: false
      }
    ],
    yearly: [
      {
        name: "Starter",
        price: "$290",
        period: "/year",
        features: ["Up to 100 complaints/month", "Basic AI bot", "Email support", "Standard analytics"],
        popular: false
      },
      {
        name: "Professional",
        price: "$790",
        period: "/year",
        features: ["Up to 500 complaints/month", "Advanced AI bot", "Priority support", "Advanced analytics", "Multi-channel integration"],
        popular: true
      },
      {
        name: "Enterprise",
        price: "$1990",
        period: "/year",
        features: ["Unlimited complaints", "Custom AI training", "24/7 support", "Custom integrations", "White-label options"],
        popular: false
      }
    ]
  };

  return (
    <div className="homepage-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-badge">
            <span>🚀 Trusted by 500+ brands worldwide</span>
          </div>
          <h1 className="hero-title">
            Your Voice, <span className="highlight">Amplified.</span>
          </h1>
          <p className="hero-subtitle">
            The modern platform for resolving customer complaints with brands, powered by AI. 
            Transform customer feedback into actionable insights.
          </p>
          <div className="hero-cta-buttons">
            <Link to="/new-complaint" className="btn btn-primary btn-lg">
              Lodge a Complaint
            </Link>
            <Link to="/track-complaint" className="btn btn-outline btn-lg">
              Track Complaint
            </Link>
            <Link to="/complaints" className="btn btn-outline btn-lg">
              View Public Complaints
            </Link>
          </div>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-number">50K+</span>
              <span className="stat-label">Complaints Resolved</span>
            </div>
            <div className="stat">
              <span className="stat-number">500+</span>
              <span className="stat-label">Brands Trust Us</span>
            </div>
            <div className="stat">
              <span className="stat-number">95%</span>
              <span className="stat-label">Satisfaction Rate</span>
            </div>
          </div>
        </div>
        <div className="hero-image">
          <div className="floating-card card-1">
            <div className="card-icon">📱</div>
            <div className="card-text">Voice Complaint</div>
          </div>
          <div className="floating-card card-2">
            <div className="card-icon">🤖</div>
            <div className="card-text">AI Processing</div>
          </div>
          <div className="floating-card card-3">
            <div className="card-icon">✅</div>
            <div className="card-text">Resolved</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <h2>A Better Way to Be Heard</h2>
          <p>Our platform ensures your issues are documented, seen, and resolved with cutting-edge technology.</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Simple, transparent, and effective complaint resolution process</p>
        </div>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Lodge Your Complaint</h3>
            <p>Use our AI-powered bot via voice, text, or web chat to submit your complaint 24/7</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>AI Processing</h3>
            <p>Our AI analyzes and categorizes your complaint, ensuring it reaches the right department</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Brand Response</h3>
            <p>Brands receive instant notifications and can respond directly through our platform</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">4</div>
            <h3>Resolution Tracking</h3>
            <p>Track the progress of your complaint and get notified when it's resolved</p>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="section-header">
          <h2>What Our Users Say</h2>
          <p>Join thousands of satisfied customers and brands</p>
        </div>
        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="testimonial-card">
              <div className="testimonial-rating">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <span key={i} className="star">⭐</span>
                ))}
              </div>
              <p className="testimonial-content">"{testimonial.content}"</p>
              <div className="testimonial-author">
                <div className="author-info">
                  <h4>{testimonial.name}</h4>
                  <p>{testimonial.role} at {testimonial.company}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section">
        <div className="section-header">
          <h2>Simple, Transparent Pricing</h2>
          <p>Choose the plan that fits your needs</p>
        </div>
        <div className="pricing-toggle">
          <button 
            className={`toggle-btn ${activeTab === 'monthly' ? 'active' : ''}`}
            onClick={() => setActiveTab('monthly')}
          >
            Monthly
          </button>
          <button 
            className={`toggle-btn ${activeTab === 'yearly' ? 'active' : ''}`}
            onClick={() => setActiveTab('yearly')}
          >
            Yearly <span className="save-badge">Save 20%</span>
          </button>
        </div>
        <div className="pricing-grid">
          {pricingPlans[activeTab].map((plan, index) => (
            <div key={index} className={`pricing-card ${plan.popular ? 'popular' : ''}`}>
              {plan.popular && <div className="popular-badge">Most Popular</div>}
              <h3>{plan.name}</h3>
              <div className="price">
                <span className="price-amount">{plan.price}</span>
                <span className="price-period">{plan.period}</span>
              </div>
              <ul className="features-list">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex}>{feature}</li>
                ))}
              </ul>
              <button className="btn btn-primary btn-full">Get Started</button>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Transform Your Complaint Management?</h2>
          <p>Join thousands of brands and customers who trust ComplaintHub</p>
          <div className="cta-buttons">
            <Link to="/signup" className="btn btn-primary btn-lg">Start Free Trial</Link>
            <Link to="/contact" className="btn btn-outline btn-lg">Contact Sales</Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>ComplaintHub</h3>
            <p>Empowering customers and brands through transparent, AI-powered complaint resolution.</p>
            <div className="social-links">
              <a href="#" className="social-link">📘</a>
              <a href="#" className="social-link">🐦</a>
              <a href="#" className="social-link">💼</a>
              <a href="#" className="social-link">📷</a>
            </div>
          </div>
          
          <div className="footer-section">
            <h4>Product</h4>
            <ul>
              <li><Link to="/features">Features</Link></li>
              <li><Link to="/pricing">Pricing</Link></li>
              <li><Link to="/integrations">Integrations</Link></li>
              <li><Link to="/api">API</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Company</h4>
            <ul>
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/careers">Careers</Link></li>
              <li><Link to="/press">Press</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Support</h4>
            <ul>
              <li><Link to="/help">Help Center</Link></li>
              <li><Link to="/track-complaint">Track Complaint</Link></li>
              <li><Link to="/docs">Documentation</Link></li>
              <li><Link to="/status">System Status</Link></li>
              <li><Link to="/contact">Contact Support</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
              <li><Link to="/cookies">Cookie Policy</Link></li>
              <li><Link to="/gdpr">GDPR</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="footer-bottom-content">
            <p>&copy; 2024 ComplaintHub. All rights reserved.</p>
            <div className="footer-bottom-links">
              <Link to="/sitemap">Sitemap</Link>
              <Link to="/accessibility">Accessibility</Link>
              <Link to="/security">Security</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;