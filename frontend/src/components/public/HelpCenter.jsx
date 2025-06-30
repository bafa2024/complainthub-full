import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TestUtils } from '../../utils/testUtils';
import './HelpCenter.css';

export default function HelpCenter() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedFaqs, setExpandedFaqs] = useState(new Set());
  const [testResults, setTestResults] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Help categories
  const categories = [
    { id: 'all', name: 'All Topics', icon: '📚' },
    { id: 'getting-started', name: 'Getting Started', icon: '🚀' },
    { id: 'complaints', name: 'Filing Complaints', icon: '📝' },
    { id: 'tracking', name: 'Tracking Complaints', icon: '🔍' },
    { id: 'voice', name: 'Voice Complaints', icon: '🎤' },
    { id: 'account', name: 'Account Management', icon: '👤' },
    { id: 'brands', name: 'For Brands', icon: '🏢' },
    { id: 'technical', name: 'Technical Support', icon: '🔧' },
    { id: 'billing', name: 'Billing & Payments', icon: '💳' },
    { id: 'privacy', name: 'Privacy & Security', icon: '🔒' }
  ];

  // Help articles data
  const helpArticles = [
    // Getting Started
    {
      id: 1,
      title: 'How to Create Your First Complaint',
      category: 'getting-started',
      content: `Creating your first complaint is easy! Follow these steps:

1. **Sign up for an account** - Click the "Sign Up" button and fill in your details
2. **Choose your complaint method** - You can file complaints via:
   - Voice call to our AI system
   - WhatsApp message
   - Web chat
   - Our website form
3. **Provide complaint details** - Include:
   - Brand name
   - Product/service details
   - Description of the issue
   - Any supporting evidence
4. **Submit and track** - Get a tracking number and monitor progress

Your complaint will be automatically routed to the relevant brand for response.`,
      tags: ['new-user', 'complaint-filing', 'tutorial'],
      views: 1250,
      helpful: 89
    },
    {
      id: 2,
      title: 'Understanding the Complaint Process',
      category: 'getting-started',
      content: `Our complaint resolution process follows these stages:

**Stage 1: Submission**
- Your complaint is received and categorized
- AI analysis determines urgency and routing
- You receive a unique tracking number

**Stage 2: Brand Notification**
- Brand is automatically notified
- 24-hour response window begins
- Public visibility timer starts

**Stage 3: Resolution**
- Brand responds with solution
- You can accept, reject, or request changes
- Escalation available if needed

**Stage 4: Completion**
- Complaint marked as resolved
- Satisfaction rating collected
- Case closed with documentation`,
      tags: ['process', 'workflow', 'timeline'],
      views: 890,
      helpful: 67
    },

    // Filing Complaints
    {
      id: 3,
      title: 'Best Practices for Filing Effective Complaints',
      category: 'complaints',
      content: `To ensure your complaint gets the attention it deserves:

**Be Specific and Detailed**
- Include exact dates and times
- Provide order numbers or reference codes
- Describe the issue clearly and objectively

**Include Supporting Evidence**
- Screenshots of conversations
- Receipts or invoices
- Photos of damaged products
- Voice recordings (if applicable)

**Set Clear Expectations**
- State what resolution you're seeking
- Be reasonable in your requests
- Provide timeline expectations

**Stay Professional**
- Avoid emotional language
- Focus on facts, not feelings
- Be respectful in your communication

**Follow Up Appropriately**
- Use the tracking system to monitor progress
- Respond promptly to brand inquiries
- Escalate only when necessary`,
      tags: ['tips', 'best-practices', 'effectiveness'],
      views: 2100,
      helpful: 156
    },
    {
      id: 4,
      title: 'Anonymous vs. Public Complaints',
      category: 'complaints',
      content: `You have two options when filing complaints:

**Anonymous Complaints**
- Your identity remains private
- Still get full tracking and updates
- Brands cannot see your personal information
- Good for sensitive issues or privacy concerns

**Public Complaints**
- Visible on our public platform
- Can receive community support
- Often get faster brand responses
- Help other consumers make informed decisions

**When to Choose Each:**

Choose **Anonymous** when:
- Dealing with sensitive personal information
- Concerned about retaliation
- Filing against your employer
- Privacy is your top priority

Choose **Public** when:
- You want to warn other consumers
- Seeking community support
- Want maximum pressure on the brand
- The issue affects many people

You can change your choice before the complaint becomes public.`,
      tags: ['privacy', 'public', 'anonymous', 'choice'],
      views: 1560,
      helpful: 112
    },

    // Voice Complaints
    {
      id: 5,
      title: 'How to File a Voice Complaint',
      category: 'voice',
      content: `Voice complaints offer a natural, convenient way to file complaints:

**Step-by-Step Process:**

1. **Call our AI system**
   - Dial our toll-free number
   - Available 24/7 in multiple languages
   - No waiting in queues

2. **Speak naturally**
   - Describe your issue in your own words
   - AI will ask clarifying questions
   - No need to remember specific formats

3. **Provide details**
   - Brand name and product/service
   - Timeline of events
   - What you've tried so far
   - Your desired resolution

4. **Review and confirm**
   - AI will summarize your complaint
   - Confirm accuracy before submission
   - Make any corrections needed

**Tips for Voice Complaints:**
- Speak clearly and at a normal pace
- Have relevant information ready
- Find a quiet environment
- Be patient with the AI system`,
      tags: ['voice', 'phone', 'ai', 'tutorial'],
      views: 980,
      helpful: 78
    },

    // Tracking
    {
      id: 6,
      title: 'Tracking Your Complaint Status',
      category: 'tracking',
      content: `Stay informed about your complaint progress:

**Tracking Methods:**

1. **Online Dashboard**
   - Log into your account
   - View all your complaints
   - Real-time status updates
   - Response notifications

2. **Tracking Number**
   - Use the number provided when filing
   - Check status without logging in
   - Share with others if needed

3. **Email Notifications**
   - Automatic updates on status changes
   - Brand responses
   - Resolution confirmations

**Status Meanings:**

**Submitted** - Complaint received and being processed
**Under Review** - AI analysis and categorization complete
**Brand Notified** - Brand has been contacted
**Brand Responded** - Brand has provided a response
**In Discussion** - Back-and-forth communication active
**Resolved** - Issue has been resolved
**Closed** - Case completed and archived

**Escalation Process:**
If your complaint isn't resolved satisfactorily, you can escalate it for manual review by our support team.`,
      tags: ['tracking', 'status', 'updates', 'dashboard'],
      views: 1340,
      helpful: 95
    },

    // Account Management
    {
      id: 7,
      title: 'Managing Your Account Settings',
      category: 'account',
      content: `Customize your ComplaintHub experience:

**Profile Settings**
- Update personal information
- Change contact preferences
- Set notification preferences
- Manage privacy settings

**Security Settings**
- Change password
- Enable two-factor authentication
- Review login history
- Manage connected devices

**Communication Preferences**
- Email notification frequency
- SMS notifications (opt-in)
- WhatsApp updates
- Newsletter subscriptions

**Privacy Controls**
- Data sharing preferences
- Public profile visibility
- Complaint history access
- Account deletion options

**Language and Region**
- Interface language
- Time zone settings
- Currency preferences
- Regional complaint categories`,
      tags: ['account', 'settings', 'profile', 'security'],
      views: 720,
      helpful: 45
    },

    // Technical Support
    {
      id: 8,
      title: 'Troubleshooting Common Issues',
      category: 'technical',
      content: `Solutions for common technical problems:

**Website Issues**
- Clear browser cache and cookies
- Try a different browser
- Check internet connection
- Disable browser extensions

**Voice System Problems**
- Check phone connection
- Speak clearly and slowly
- Try calling from a different number
- Use the web alternative

**Mobile App Issues**
- Update to latest version
- Restart the app
- Check device storage
- Reinstall if necessary

**Login Problems**
- Reset password
- Check email for verification
- Clear browser data
- Contact support if locked out

**Payment Issues**
- Verify card information
- Check bank account balance
- Try different payment method
- Contact billing support`,
      tags: ['troubleshooting', 'technical', 'problems', 'solutions'],
      views: 890,
      helpful: 67
    }
  ];

  // FAQ data
  const faqs = [
    {
      question: 'How long does it take to resolve a complaint?',
      answer: 'Most complaints are resolved within 3-7 business days. Complex issues may take longer, but you\'ll always be kept updated on progress.',
      category: 'complaints'
    },
    {
      question: 'Can I file complaints anonymously?',
      answer: 'Yes, you can choose to file complaints anonymously. Your identity will be protected while still receiving full tracking and updates.',
      category: 'privacy'
    },
    {
      question: 'What if a brand doesn\'t respond?',
      answer: 'If a brand doesn\'t respond within 24 hours, your complaint becomes public on our platform, which often encourages faster resolution.',
      category: 'complaints'
    },
    {
      question: 'Is my personal information secure?',
      answer: 'Yes, we use enterprise-grade encryption and never share your data without explicit consent. Your privacy is our top priority.',
      category: 'privacy'
    },
    {
      question: 'Can I track multiple complaints?',
      answer: 'Yes, you can track all your complaints through your dashboard. Each complaint has a unique tracking number for easy reference.',
      category: 'tracking'
    },
    {
      question: 'What languages do you support?',
      answer: 'Our platform supports multiple languages including English, Spanish, French, German, and more. Voice complaints are available in 15+ languages.',
      category: 'technical'
    }
  ];

  // Handle search
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    
    // Simulate search delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const results = helpArticles.filter(article => 
      article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      article.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );
    
    setSearchResults(results);
    setIsSearching(false);
    
    // Run search performance test
    const searchTest = TestUtils.testPerformance(() => {
      console.log('Search completed:', results.length, 'results');
    });
    setTestResults(prev => [...prev, { name: 'Search Performance', ...searchTest }]);
  };

  // Handle FAQ expansion
  const toggleFaq = (index) => {
    const newExpanded = new Set(expandedFaqs);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedFaqs(newExpanded);
  };

  // Filter articles by category
  const filteredArticles = selectedCategory === 'all' 
    ? helpArticles 
    : helpArticles.filter(article => article.category === selectedCategory);

  // Run component tests on mount
  useEffect(() => {
    const runComponentTests = async () => {
      const tests = [
        {
          name: 'Component Rendering',
          fn: () => TestUtils.testComponentRenders(HelpCenter)
        },
        {
          name: 'Local Storage',
          fn: () => TestUtils.testLocalStorage()
        },
        {
          name: 'Responsive Design',
          fn: () => TestUtils.testResponsiveDesign()
        }
      ];
      
      const results = await TestUtils.runTestSuite(tests);
      setTestResults(results.results);
    };
    
    runComponentTests();
  }, []);

  return (
    <div className="help-center-page">
      {/* Header */}
      <div className="help-header">
        <div className="header-container">
          <div className="logo">ComplaintHub</div>
          <div className="header-nav">
            <Link to="/" className="btn btn-outline">Back to Home</Link>
            <Link to="/contact" className="btn btn-primary">Contact Support</Link>
          </div>
        </div>
      </div>

      <div className="main-container">
        {/* Hero Section */}
        <div className="help-hero">
          <h1>Help Center</h1>
          <p>Find answers to your questions and learn how to get the most out of ComplaintHub</p>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-container">
              <input
                type="text"
                placeholder="Search for help articles, FAQs, or topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <button type="submit" className="search-button" disabled={isSearching}>
                {isSearching ? '🔍' : '🔍'}
              </button>
            </div>
          </form>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="search-results">
            <h2>Search Results ({searchResults.length})</h2>
            <div className="results-grid">
              {searchResults.map(article => (
                <div key={article.id} className="result-card">
                  <h3>{article.title}</h3>
                  <p>{article.content.substring(0, 150)}...</p>
                  <div className="result-meta">
                    <span className="category">{categories.find(c => c.id === article.category)?.name}</span>
                    <span className="views">{article.views} views</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Categories */}
        <div className="categories-section">
          <h2>Browse by Category</h2>
          <div className="categories-grid">
            {categories.map(category => (
              <button
                key={category.id}
                className={`category-card ${selectedCategory === category.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(category.id)}
              >
                <div className="category-icon">{category.icon}</div>
                <div className="category-name">{category.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Help Articles */}
        <div className="articles-section">
          <h2>{selectedCategory === 'all' ? 'All Help Articles' : categories.find(c => c.id === selectedCategory)?.name}</h2>
          <div className="articles-grid">
            {filteredArticles.map(article => (
              <div key={article.id} className="article-card">
                <div className="article-header">
                  <h3>{article.title}</h3>
                  <div className="article-meta">
                    <span className="views">{article.views} views</span>
                    <span className="helpful">{article.helpful} found helpful</span>
                  </div>
                </div>
                <div className="article-content">
                  {article.content.split('\n').map((paragraph, index) => (
                    <p key={index}>{paragraph}</p>
                  ))}
                </div>
                <div className="article-tags">
                  {article.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Section */}
        <div className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-list">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <button
                  className="faq-question"
                  onClick={() => toggleFaq(index)}
                >
                  <span>{faq.question}</span>
                  <span className="faq-icon">
                    {expandedFaqs.has(index) ? '−' : '+'}
                  </span>
                </button>
                {expandedFaqs.has(index) && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Still Need Help */}
        <div className="need-help-section">
          <div className="need-help-content">
            <h2>Still Need Help?</h2>
            <p>Can't find what you're looking for? Our support team is here to help.</p>
            <div className="help-actions">
              <Link to="/contact" className="btn btn-primary">Contact Support</Link>
              <Link to="/chat" className="btn btn-outline">Live Chat</Link>
            </div>
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