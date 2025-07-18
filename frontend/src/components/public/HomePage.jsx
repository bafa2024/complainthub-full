import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Helmet, HelmetProvider } from 'react-helmet-async';

const HomePage = () => {
  const [activeTab, setActiveTab] = useState('monthly');
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      setScrolled(isScrolled);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Customer Service Manager",
      company: "TechCorp",
      content: "ComplaintHub has revolutionized how we handle customer feedback. The AI-powered system ensures no complaint goes unnoticed.",
      rating: 5,
      avatar: "SJ"
    },
    {
      name: "Michael Chen",
      role: "Small Business Owner",
      company: "LocalMart",
      content: "As a small business, we couldn't afford expensive CRM systems. ComplaintHub gives us enterprise-level complaint management.",
      rating: 5,
      avatar: "MC"
    },
    {
      name: "Emily Rodriguez",
      role: "Consumer Advocate",
      company: "Consumer Rights",
      content: "Finally, a platform that gives consumers real power. The public visibility feature ensures brands take complaints seriously.",
      rating: 5,
      avatar: "ER"
    }
  ];

  const features = [
    {
      icon: "🤖",
      title: "AI-Powered Bot",
      description: "Our intelligent voice and chatbot captures your complaint details accurately, 24/7, ensuring nothing gets lost in translation.",
      color: "#667eea"
    },
    {
      icon: "👁️",
      title: "Public Visibility",
      description: "Unresolved complaints are made public to encourage brands to respond quickly and maintain their reputation.",
      color: "#f59e0b"
    },
    {
      icon: "📱",
      title: "Multi-Channel Support",
      description: "Lodge your complaint via Phone Call, WhatsApp, Telegram, Web Chat, and more - whatever's convenient for you.",
      color: "#10b981"
    },
    {
      icon: "📊",
      title: "Analytics Dashboard",
      description: "Comprehensive analytics and reporting tools to track complaint resolution times and customer satisfaction.",
      color: "#3b82f6"
    },
    {
      icon: "🔒",
      title: "Secure & Private",
      description: "Your data is protected with enterprise-grade security. We never share your personal information without consent.",
      color: "#ef4444"
    },
    {
      icon: "⚡",
      title: "Real-time Updates",
      description: "Get instant notifications on complaint status updates, brand responses, and resolution progress.",
      color: "#8b5cf6"
    }
  ];

  const pricingPlans = {
    monthly: [
      {
        name: "Starter",
        price: "$29",
        period: "/month",
        features: ["Up to 100 complaints/month", "Basic AI bot", "Email support", "Standard analytics"],
        popular: false,
        color: "#64748b"
      },
      {
        name: "Professional",
        price: "$79",
        period: "/month",
        features: ["Up to 500 complaints/month", "Advanced AI bot", "Priority support", "Advanced analytics", "Multi-channel integration"],
        popular: true,
        color: "#667eea"
      },
      {
        name: "Enterprise",
        price: "$199",
        period: "/month",
        features: ["Unlimited complaints", "Custom AI training", "24/7 support", "Custom integrations", "White-label options"],
        popular: false,
        color: "#1e293b"
      }
    ],
    yearly: [
      {
        name: "Starter",
        price: "$290",
        period: "/year",
        features: ["Up to 100 complaints/month", "Basic AI bot", "Email support", "Standard analytics"],
        popular: false,
        color: "#64748b"
      },
      {
        name: "Professional",
        price: "$790",
        period: "/year",
        features: ["Up to 500 complaints/month", "Advanced AI bot", "Priority support", "Advanced analytics", "Multi-channel integration"],
        popular: true,
        color: "#667eea"
      },
      {
        name: "Enterprise",
        price: "$1990",
        period: "/year",
        features: ["Unlimited complaints", "Custom AI training", "24/7 support", "Custom integrations", "White-label options"],
        popular: false,
        color: "#1e293b"
      }
    ]
  };

  return (
    <HelmetProvider>
      <>
        <Helmet>
          <title>ComplaintHub | Public Complaint Platform</title>
          <meta name="description" content="Lodge complaints, track resolutions, and hold brands accountable. Public complaint platform for consumers and businesses." />
          <meta property="og:title" content="ComplaintHub | Public Complaint Platform" />
          <meta property="og:description" content="Lodge complaints, track resolutions, and hold brands accountable. Public complaint platform for consumers and businesses." />
          <meta property="og:type" content="website" />
          <meta property="og:url" content={window.location.href} />
          <meta property="og:image" content="/complainthub-og.png" />
          <meta name="twitter:card" content="summary_large_image" />
          <meta name="twitter:title" content="ComplaintHub | Public Complaint Platform" />
          <meta name="twitter:description" content="Lodge complaints, track resolutions, and hold brands accountable. Public complaint platform for consumers and businesses." />
          <meta name="twitter:image" content="/complainthub-og.png" />
          <link rel="canonical" href={window.location.href} />
          <script type="application/ld+json">
            {JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": "ComplaintHub",
              "url": window.location.origin,
              "description": "Lodge complaints, track resolutions, and hold brands accountable. Public complaint platform for consumers and businesses."
            })}
          </script>
        </Helmet>
        
        <div className="min-vh-100">
          {/* Hero Section */}
          <section className="bg-gradient-primary text-white py-5">
            <div className="container">
              <div className="row align-items-center min-vh-100">
                <div className="col-lg-6">
                  <div className="mb-4">
                    <span className="badge bg-warning text-dark px-3 py-2 rounded-pill">
                      <i className="bi bi-trophy me-2"></i>
                      Trusted by 500+ brands worldwide
                    </span>
                  </div>
                  
                  <h1 className="display-3 fw-bold mb-4">
                    Your Voice, <span className="text-warning">Amplified</span>
                  </h1>
                  
                  <p className="lead mb-4">
                    Transform customer complaints into powerful insights. Our AI-powered platform ensures 
                    every voice is heard, every issue is tracked, and every brand is held accountable.
                  </p>
                  
                  <div className="d-flex flex-column flex-sm-row gap-3 mb-4">
                    <Link to="/new-complaint" className="btn btn-warning btn-lg px-4 py-3">
                      <i className="bi bi-mic-fill me-2"></i>
                      Lodge a Complaint
                    </Link>
                    <Link to="/track-complaint" className="btn btn-outline-light btn-lg px-4 py-3">
                      <i className="bi bi-search me-2"></i>
                      Track Complaint
                    </Link>
                  </div>
                  
                  <div className="mb-4">
                    <Link to="/complaints" className="text-light text-decoration-none">
                      <i className="bi bi-globe me-2"></i>
                      View Public Complaints
                    </Link>
                  </div>
                  
                  <div className="row text-center">
                    <div className="col-4">
                      <div className="h3 fw-bold text-warning">50K+</div>
                      <div className="small">Complaints Resolved</div>
                    </div>
                    <div className="col-4">
                      <div className="h3 fw-bold text-warning">500+</div>
                      <div className="small">Brands Trust Us</div>
                    </div>
                    <div className="col-4">
                      <div className="h3 fw-bold text-warning">95%</div>
                      <div className="small">Satisfaction Rate</div>
                    </div>
                  </div>
                </div>
                
                <div className="col-lg-6">
                  <div className="card bg-dark bg-opacity-25 border-0 p-4">
                    <div className="card-body">
                      <div className="d-flex align-items-center mb-3">
                        <div className="bg-warning rounded-circle p-2 me-3">🤖</div>
                        <div className="bg-light text-dark p-3 rounded">Hello! How can I help you today?</div>
                      </div>
                      <div className="d-flex justify-content-end mb-3">
                        <div className="bg-warning text-dark p-3 rounded">I have a complaint about my recent order</div>
                      </div>
                      <div className="d-flex align-items-center">
                        <div className="bg-warning rounded-circle p-2 me-3">🤖</div>
                        <div className="bg-light text-dark p-3 rounded">I understand. Let me help you file that complaint...</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Features Section */}
          <section className="py-5 bg-light">
            <div className="container">
              <div className="text-center mb-5">
                <h2 className="display-5 fw-bold mb-3">
                  Everything you need to <span className="text-primary">be heard</span>
                </h2>
                <p className="lead text-muted">
                  Our comprehensive platform combines cutting-edge AI technology with human-centered design 
                  to create the most effective complaint resolution system.
                </p>
              </div>
              
              <div className="row g-4">
                {features.map((feature, index) => (
                  <div key={index} className="col-md-6 col-lg-4">
                    <div className="card h-100 border-0 shadow-sm">
                      <div className="card-body text-center p-4">
                        <div className="display-4 mb-3">{feature.icon}</div>
                        <h5 className="card-title fw-bold mb-3">{feature.title}</h5>
                        <p className="card-text text-muted">{feature.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* How It Works Section */}
          <section className="py-5">
            <div className="container">
              <div className="text-center mb-5">
                <h2 className="display-5 fw-bold mb-3">
                  How it <span className="text-primary">works</span>
                </h2>
                <p className="lead text-muted">
                  From complaint to resolution in four simple steps
                </p>
              </div>
              
              <div className="row g-4">
                <div className="col-md-6 col-lg-3 text-center">
                  <div className="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="bi bi-mic-fill fs-3"></i>
                  </div>
                  <h5 className="fw-bold mb-2">Lodge Your Complaint</h5>
                  <p className="text-muted">Use our AI-powered bot via voice, text, or web chat to submit your complaint 24/7</p>
                </div>
                
                <div className="col-md-6 col-lg-3 text-center">
                  <div className="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="bi bi-robot fs-3"></i>
                  </div>
                  <h5 className="fw-bold mb-2">AI Processing</h5>
                  <p className="text-muted">Our intelligent system categorizes and routes your complaint to the right brand automatically</p>
                </div>
                
                <div className="col-md-6 col-lg-3 text-center">
                  <div className="bg-warning text-dark rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="bi bi-chat-dots fs-3"></i>
                  </div>
                  <h5 className="fw-bold mb-2">Brand Response</h5>
                  <p className="text-muted">Brands receive your complaint and respond within 24 hours with a resolution plan</p>
                </div>
                
                <div className="col-md-6 col-lg-3 text-center">
                  <div className="bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{width: '80px', height: '80px'}}>
                    <i className="bi bi-check-circle fs-3"></i>
                  </div>
                  <h5 className="fw-bold mb-2">Resolution & Feedback</h5>
                  <p className="text-muted">Track the resolution progress and provide feedback on the outcome</p>
                </div>
              </div>
            </div>
          </section>

          {/* Testimonials Section */}
          <section className="py-5 bg-light">
            <div className="container">
              <div className="text-center mb-5">
                <h2 className="display-5 fw-bold mb-3">
                  Loved by <span className="text-primary">thousands</span>
                </h2>
                <p className="lead text-muted">
                  See what our users have to say about their experience
                </p>
              </div>
              
              <div className="row g-4">
                {testimonials.map((testimonial, index) => (
                  <div key={index} className="col-md-4">
                    <div className="card h-100 border-0 shadow-sm">
                      <div className="card-body p-4">
                        <div className="text-warning mb-3">
                          {[...Array(testimonial.rating)].map((_, i) => (
                            <i key={i} className="bi bi-star-fill"></i>
                          ))}
                        </div>
                        <p className="card-text mb-3">"{testimonial.content}"</p>
                        <div className="d-flex align-items-center">
                          <div className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style={{width: '40px', height: '40px'}}>
                            {testimonial.avatar}
                          </div>
                          <div>
                            <h6 className="fw-bold mb-0">{testimonial.name}</h6>
                            <small className="text-muted">{testimonial.role} • {testimonial.company}</small>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* Pricing Section */}
          <section className="py-5">
            <div className="container">
              <div className="text-center mb-5">
                <h2 className="display-5 fw-bold mb-3">
                  Choose your <span className="text-primary">plan</span>
                </h2>
                <p className="lead text-muted">
                  Transparent pricing that scales with your business
                </p>
              </div>
              
              <div className="d-flex justify-content-center mb-5">
                <div className="btn-group" role="group">
                  <button
                    className={`btn ${activeTab === 'monthly' ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveTab('monthly')}
                  >
                    Monthly
                  </button>
                  <button
                    className={`btn ${activeTab === 'yearly' ? 'btn-primary' : 'btn-outline-primary'}`}
                    onClick={() => setActiveTab('yearly')}
                  >
                    Yearly
                    <span className="badge bg-warning text-dark ms-2">Save 20%</span>
                  </button>
                </div>
              </div>
              
              <div className="row g-4 justify-content-center">
                {pricingPlans[activeTab].map((plan, index) => (
                  <div key={index} className="col-md-4">
                    <div className={`card h-100 border-0 shadow-sm ${plan.popular ? 'border-primary' : ''}`}>
                      {plan.popular && (
                        <div className="bg-primary text-white text-center py-2 rounded-top">
                          <small className="fw-bold">Most Popular</small>
                        </div>
                      )}
                      <div className="card-body p-4">
                        <div className="text-center mb-4">
                          <h5 className="fw-bold mb-2">{plan.name}</h5>
                          <div className="mb-3">
                            <span className="display-6 fw-bold">{plan.price}</span>
                            <span className="text-muted">{plan.period}</span>
                          </div>
                        </div>
                        <ul className="list-unstyled mb-4">
                          {plan.features.map((feature, i) => (
                            <li key={i} className="mb-2">
                              <i className="bi bi-check-circle-fill text-success me-2"></i>
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                        <Link to="/signup" className="btn btn-primary w-100">
                          Get Started
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* CTA Section */}
          <section className="py-5 bg-primary text-white">
            <div className="container">
              <div className="row align-items-center">
                <div className="col-lg-8">
                  <h2 className="display-5 fw-bold mb-3">
                    Ready to make your voice <span className="text-warning">heard</span>?
                  </h2>
                  <p className="lead mb-4">
                    Join thousands of consumers and businesses who trust ComplaintHub
                  </p>
                  <div className="d-flex flex-column flex-sm-row gap-3 mb-4">
                    <Link to="/signup" className="btn btn-warning btn-lg px-4 py-3">
                      <i className="bi bi-rocket me-2"></i>
                      Get Started Free
                    </Link>
                    <Link to="/contact" className="btn btn-outline-light btn-lg px-4 py-3">
                      <i className="bi bi-headset me-2"></i>
                      Talk to Sales
                    </Link>
                  </div>
                  <p className="mb-0">
                    <i className="bi bi-shield-check me-2"></i>
                    No credit card required • Free 14-day trial
                  </p>
                </div>
                <div className="col-lg-4">
                  <div className="row text-center">
                    <div className="col-4">
                      <i className="bi bi-people display-6 text-warning"></i>
                      <div className="mt-2">
                        <div className="fw-bold">10K+</div>
                        <small>Active Users</small>
                      </div>
                    </div>
                    <div className="col-4">
                      <i className="bi bi-building display-6 text-warning"></i>
                      <div className="mt-2">
                        <div className="fw-bold">500+</div>
                        <small>Brands</small>
                      </div>
                    </div>
                    <div className="col-4">
                      <i className="bi bi-globe display-6 text-warning"></i>
                      <div className="mt-2">
                        <div className="fw-bold">20+</div>
                        <small>Countries</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </>
    </HelmetProvider>
  );
};

export default HomePage;