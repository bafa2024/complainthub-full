// frontend/src/components/brand/BrandPhoneNumbers.jsx

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import brandService from '../../services/brandService';
import LoadingSpinner from '../shared/LoadingSpinner';
import './BrandPhoneNumbers.css';

const BrandPhoneNumbers = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [phoneNumbers, setPhoneNumbers] = useState([]);
  const [availableNumbers, setAvailableNumbers] = useState([]);
  const [providers, setProviders] = useState([]);
  const [searchParams, setSearchParams] = useState({
    country_code: 'IN',
    number_type: 'toll-free',
    capabilities: ['voice', 'sms'],
    provider: 'twilio'
  });
  const [purchasing, setPurchasing] = useState(false);
  const [activeTab, setActiveTab] = useState('my-numbers');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [numbersData, providersData] = await Promise.all([
        brandService.getPhoneNumbers(),
        brandService.getTelephonyProviders()
      ]);
      
      setPhoneNumbers(numbersData || []);
      setProviders(providersData || []);
    } catch (err) {
      console.error('Error loading phone numbers:', err);
      setError('Failed to load phone number data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleSearchNumbers = async () => {
    try {
      setLoading(true);
      setError('');
      
      const numbers = await brandService.searchAvailableNumbers(searchParams);
      setAvailableNumbers(numbers || []);
    } catch (err) {
      console.error('Error searching numbers:', err);
      setError('Failed to search available numbers: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handlePurchaseNumber = async (phoneNumber) => {
    if (!window.confirm(`Are you sure you want to purchase ${phoneNumber.phone_number}? This will cost ₹${phoneNumber.monthly_cost}/month.`)) {
      return;
    }

    try {
      setPurchasing(true);
      setError('');
      
      const result = await brandService.purchasePhoneNumber({
        phone_number: phoneNumber.phone_number,
        provider: phoneNumber.provider,
        capabilities: phoneNumber.capabilities,
        auto_approve: true
      });
      
      if (result.success) {
        alert(`Successfully purchased ${phoneNumber.phone_number}!`);
        loadData(); // Refresh the list
      } else {
        throw new Error(result.error || 'Purchase failed');
      }
    } catch (err) {
      console.error('Error purchasing number:', err);
      setError('Failed to purchase number: ' + (err.message || 'Unknown error'));
    } finally {
      setPurchasing(false);
    }
  };

  const handleUpdateNumberStatus = async (phoneNumber, newStatus) => {
    try {
      setLoading(true);
      setError('');
      
      await brandService.updatePhoneNumberStatus(phoneNumber.phone_number, {
        status: newStatus
      });
      
      loadData(); // Refresh the list
    } catch (err) {
      console.error('Error updating number status:', err);
      setError('Failed to update number status: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const handleReleaseNumber = async (phoneNumber) => {
    if (!window.confirm(`Are you sure you want to release ${phoneNumber.phone_number}? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      await brandService.releasePhoneNumber(phoneNumber.phone_number);
      alert(`Successfully released ${phoneNumber.phone_number}!`);
      loadData(); // Refresh the list
    } catch (err) {
      console.error('Error releasing number:', err);
      setError('Failed to release number: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const formatPhoneNumber = (number) => {
    // Format phone number for display
    if (number.startsWith('+91')) {
      return number.replace('+91', '+91-');
    }
    return number;
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active': return 'badge-success';
      case 'inactive': return 'badge-secondary';
      case 'pending': return 'badge-warning';
      default: return 'badge-light';
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="brand-phone-numbers-container">
      <div className="page-header">
        <h1>Phone Number Management</h1>
        <p>Search, purchase, and manage virtual phone numbers for your brand</p>
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
          <button onClick={() => setError('')} className="close-btn">&times;</button>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-btn ${activeTab === 'my-numbers' ? 'active' : ''}`}
          onClick={() => setActiveTab('my-numbers')}
        >
          My Numbers ({phoneNumbers.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'search-numbers' ? 'active' : ''}`}
          onClick={() => setActiveTab('search-numbers')}
        >
          Search & Purchase
        </button>
      </div>

      {/* My Numbers Tab */}
      {activeTab === 'my-numbers' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Your Phone Numbers</h2>
            <button 
              className="btn btn-primary"
              onClick={() => setActiveTab('search-numbers')}
            >
              Purchase New Number
            </button>
          </div>

          {phoneNumbers.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📞</div>
              <h3>No Phone Numbers Yet</h3>
              <p>You haven't purchased any phone numbers yet. Start by searching for available numbers.</p>
              <button 
                className="btn btn-primary"
                onClick={() => setActiveTab('search-numbers')}
              >
                Search Numbers
              </button>
            </div>
          ) : (
            <div className="phone-numbers-grid">
              {phoneNumbers.map((number) => (
                <div key={number.id} className="phone-number-card">
                  <div className="number-header">
                    <h3>{formatPhoneNumber(number.phone_number)}</h3>
                    <span className={`status-badge ${getStatusBadgeClass(number.status)}`}>
                      {number.status.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="number-details">
                    <p><strong>Provider:</strong> {number.provider}</p>
                    <p><strong>Type:</strong> {number.number_type}</p>
                    <p><strong>Capabilities:</strong> {number.capabilities?.join(', ')}</p>
                    <p><strong>Monthly Cost:</strong> ₹{number.monthly_cost}</p>
                    <p><strong>Webhook:</strong> {number.webhook_url}</p>
                  </div>
                  
                  <div className="number-actions">
                    {number.status === 'active' ? (
                      <button 
                        className="btn btn-sm btn-warning"
                        onClick={() => handleUpdateNumberStatus(number, 'inactive')}
                        disabled={loading}
                      >
                        Deactivate
                      </button>
                    ) : (
                      <button 
                        className="btn btn-sm btn-success"
                        onClick={() => handleUpdateNumberStatus(number, 'active')}
                        disabled={loading}
                      >
                        Activate
                      </button>
                    )}
                    
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleReleaseNumber(number)}
                      disabled={loading}
                    >
                      Release
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Search Numbers Tab */}
      {activeTab === 'search-numbers' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Search Available Numbers</h2>
          </div>

          {/* Search Form */}
          <div className="search-form">
            <div className="form-row">
              <div className="form-group">
                <label>Country Code:</label>
                <select 
                  value={searchParams.country_code}
                  onChange={(e) => setSearchParams({...searchParams, country_code: e.target.value})}
                >
                  <option value="IN">India (+91)</option>
                  <option value="US">United States (+1)</option>
                  <option value="GB">United Kingdom (+44)</option>
                  <option value="CA">Canada (+1)</option>
                  <option value="AU">Australia (+61)</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Number Type:</label>
                <select 
                  value={searchParams.number_type}
                  onChange={(e) => setSearchParams({...searchParams, number_type: e.target.value})}
                >
                  <option value="toll-free">Toll-Free</option>
                  <option value="local">Local</option>
                  <option value="mobile">Mobile</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Provider:</label>
                <select 
                  value={searchParams.provider}
                  onChange={(e) => setSearchParams({...searchParams, provider: e.target.value})}
                >
                  {providers.map((provider) => (
                    <option key={provider.name} value={provider.name}>
                      {provider.display_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Capabilities:</label>
                <div className="checkbox-group">
                  <label>
                    <input 
                      type="checkbox"
                      checked={searchParams.capabilities.includes('voice')}
                      onChange={(e) => {
                        const caps = e.target.checked 
                          ? [...searchParams.capabilities, 'voice']
                          : searchParams.capabilities.filter(c => c !== 'voice');
                        setSearchParams({...searchParams, capabilities: caps});
                      }}
                    />
                    Voice
                  </label>
                  <label>
                    <input 
                      type="checkbox"
                      checked={searchParams.capabilities.includes('sms')}
                      onChange={(e) => {
                        const caps = e.target.checked 
                          ? [...searchParams.capabilities, 'sms']
                          : searchParams.capabilities.filter(c => c !== 'sms');
                        setSearchParams({...searchParams, capabilities: caps});
                      }}
                    />
                    SMS
                  </label>
                  <label>
                    <input 
                      type="checkbox"
                      checked={searchParams.capabilities.includes('whatsapp')}
                      onChange={(e) => {
                        const caps = e.target.checked 
                          ? [...searchParams.capabilities, 'whatsapp']
                          : searchParams.capabilities.filter(c => c !== 'whatsapp');
                        setSearchParams({...searchParams, capabilities: caps});
                      }}
                    />
                    WhatsApp
                  </label>
                </div>
              </div>
            </div>
            
            <button 
              className="btn btn-primary"
              onClick={handleSearchNumbers}
              disabled={loading || searchParams.capabilities.length === 0}
            >
              {loading ? 'Searching...' : 'Search Numbers'}
            </button>
          </div>

          {/* Search Results */}
          {availableNumbers.length > 0 && (
            <div className="search-results">
              <h3>Available Numbers ({availableNumbers.length})</h3>
              <div className="numbers-grid">
                {availableNumbers.map((number, index) => (
                  <div key={index} className="available-number-card">
                    <div className="number-info">
                      <h4>{formatPhoneNumber(number.phone_number)}</h4>
                      <p><strong>Provider:</strong> {number.provider}</p>
                      <p><strong>Type:</strong> {number.number_type}</p>
                      <p><strong>Capabilities:</strong> {number.capabilities.join(', ')}</p>
                      <p><strong>Monthly Cost:</strong> ₹{number.monthly_cost}</p>
                      {number.setup_cost > 0 && (
                        <p><strong>Setup Cost:</strong> ₹{number.setup_cost}</p>
                      )}
                    </div>
                    
                    <div className="number-actions">
                      <button 
                        className="btn btn-success"
                        onClick={() => handlePurchaseNumber(number)}
                        disabled={purchasing}
                      >
                        {purchasing ? 'Purchasing...' : 'Purchase'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {availableNumbers.length === 0 && !loading && (
            <div className="empty-state">
              <div className="empty-icon">🔍</div>
              <h3>No Numbers Found</h3>
              <p>Try adjusting your search criteria to find available numbers.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BrandPhoneNumbers; 