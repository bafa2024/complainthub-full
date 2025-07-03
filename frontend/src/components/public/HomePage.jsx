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
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section page-container">
        <div className="hero-content">
          <div className="hero-badge">
            <i className="fas fa-rocket me-2"></i>
            <span>Trusted by 500+ brands worldwide</span>
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
              <i className="fas fa-plus me-2"></i>Lodge a Complaint
            </Link>
            <Link to="/track-complaint" className="btn btn-secondary btn-lg">
              <i className="fas fa-search me-2"></i>Track Complaint
            </Link>
            <Link to="/complaints" className="btn btn-outline-secondary btn-lg">
              <i className="fas fa-list me-2"></i>View Public Complaints
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
      <section className="features-section page-container">
        <div className="page-header">
          <h2 className="page-title">A Better Way to Be Heard</h2>
          <p className="page-subtitle">Our platform ensures your issues are documented, seen, and resolved with cutting-edge technology.</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card card">
              <div className="card-body">
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section page-container">
        <div className="page-header">
          <h2 className="page-title">How It Works</h2>
          <p className="page-subtitle">Simple, transparent, and effective complaint resolution process</p>
        </div>
        <div className="steps-container">
          <div className="step card">
            <div className="card-body text-center">
              <div className="step-number">1</div>
              <h3>Lodge Your Complaint</h3>
              <p>Use our AI-powered bot via voice, text, or web chat to submit your complaint 24/7</p>
            </div>
          </div>
          <div className="step-arrow">
            <i className="fas fa-arrow-right"></i>
          </div>
          <div className="step card">
            <div className="card-body text-center">
              <div className="step-number">2</div>
              <h3>AI Processing</h3>
              <p>Our intelligent system categorizes and routes your complaint to the right brand automatically</p>
            </div>
          </div>
          <div className="step-arrow">
            <i className="fas fa-arrow-right"></i>
          </div>
          <div className="step card">
            <div className="card-body text-center">
              <div className="step-number">3</div>
              <h3>Brand Response</h3>
              <p>Brands receive your complaint and respond within 24 hours with a resolution plan</p>
            </div>
          </div>
          <div className="step-arrow">
            <i className="fas fa-arrow-right"></i>
          </div>
          <div className="step card">
            <div className="card-body text-center">
              <div className="step-number">4</div>
              <h3>Resolution & Feedback</h3>
              <p>Track the resolution progress and provide feedback on the outcome</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section page-container">
        <div className="page-header">
          <h2 className="page-title">What Our Users Say</h2>
          <p className="page-subtitle">Real feedback from customers and brands who trust ComplaintHub</p>
        </div>
        <div className="testimonials-grid">
          {testimonials.map((testimonial, index) => (
            <div key={index} className="testimonial-card card">
              <div className="card-body">
                <div className="testimonial-rating">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <i key={i} className="fas fa-star text-warning"></i>
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
            </div>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section page-container">
        <div className="page-header">
          <h2 className="page-title">Simple, Transparent Pricing</h2>
          <p className="page-subtitle">Choose the plan that fits your needs. No hidden fees, no surprises.</p>
        </div>
        
        <div className="pricing-toggle text-center mb-4">
          <div className="btn-group" role="group">
            <button
              type="button"
              className={`btn ${activeTab === 'monthly' ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => setActiveTab('monthly')}
            >
              Monthly
            </button>
            <button
              type="button"
              className={`btn ${activeTab === 'yearly' ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => setActiveTab('yearly')}
            >
              Yearly <span className="badge bg-success ms-1">Save 20%</span>
            </button>
          </div>
        </div>

        <div className="pricing-grid">
          {pricingPlans[activeTab].map((plan, index) => (
            <div key={index} className={`pricing-card card ${plan.popular ? 'popular' : ''}`}>
              {plan.popular && (
                <div className="popular-badge">
                  <span>Most Popular</span>
                </div>
              )}
              <div className="card-body">
                <h3 className="plan-name">{plan.name}</h3>
                <div className="plan-price">
                  <span className="price">{plan.price}</span>
                  <span className="period">{plan.period}</span>
                </div>
                <ul className="plan-features">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex}>
                      <i className="fas fa-check text-success me-2"></i>
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/signup" className="btn btn-primary w-100">
                  Get Started
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section page-container">
        <div className="cta-content text-center">
          <h2>Ready to Get Started?</h2>
          <p>Join thousands of customers and brands who trust ComplaintHub for their complaint management needs.</p>
          <div className="cta-buttons">
            <Link to="/signup" className="btn btn-primary btn-lg">
              <i className="fas fa-user-plus me-2"></i>Sign Up Now
            </Link>
            <Link to="/contact" className="btn btn-outline-secondary btn-lg">
              <i className="fas fa-envelope me-2"></i>Contact Sales
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;