import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import brandService from '../../services/brandService';
import ticketService from '../../services/ticketService';
import LoadingSpinner from '../shared/LoadingSpinner';
import VoiceRecorder from '../shared/VoiceRecorder';
import './NewComplaint.css';

const NewComplaint = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    brandId: '',
    category: 'complaint',
    urgency: 'medium',
    channel: 'webchat',
    isPublic: false,
    contactPreference: 'email'
  });
  const [brands, setBrands] = useState([]);
  const [audioBlob, setAudioBlob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const navigate = useNavigate();

  const channels = [
    { id: 'webchat', name: 'Web Chat', icon: '💬', description: 'Submit via web form' },
    { id: 'voice', name: 'Voice Call', icon: '📞', description: 'Call and speak your complaint' },
    { id: 'whatsapp', name: 'WhatsApp', icon: '📱', description: 'Send via WhatsApp' },
    { id: 'telegram', name: 'Telegram', icon: '✈️', description: 'Send via Telegram bot' },
    { id: 'email', name: 'Email', icon: '📧', description: 'Send via email' }
  ];

  const categories = [
    { id: 'complaint', name: 'Complaint', description: 'General complaint about service or product' },
    { id: 'technical', name: 'Technical Issue', description: 'Technical problem or bug' },
    { id: 'billing', name: 'Billing Issue', description: 'Payment or billing problem' },
    { id: 'delivery', name: 'Delivery Issue', description: 'Shipping or delivery problem' },
    { id: 'refund', name: 'Refund Request', description: 'Request for refund or return' },
    { id: 'feedback', name: 'Feedback', description: 'General feedback or suggestion' }
  ];

  const urgencyLevels = [
    { id: 'low', name: 'Low', description: 'Not urgent, can wait' },
    { id: 'medium', name: 'Medium', description: 'Moderate urgency' },
    { id: 'high', name: 'High', description: 'Urgent attention needed' },
    { id: 'critical', name: 'Critical', description: 'Immediate attention required' }
  ];

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        setLoading(true);
        const brandsData = await brandService.getPublicBrands();
        setBrands(brandsData || []);
      } catch (err) {
        console.error(err);
        setError('Could not load brand information.');
      } finally {
        setLoading(false);
      }
    };
    fetchBrands();
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.brandId || (!formData.description && !audioBlob)) {
      setError('Please provide a title, select a brand, and either type a description or record a voice note.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccess(false);

    try {
      const ticketData = {
        title: formData.title,
        description: formData.description || '',
        brand_id: parseInt(formData.brandId),
        category: formData.category,
        urgency: formData.urgency,
        channel: formData.channel,
        is_public: formData.isPublic,
        status: 'new'
      };

      const newTicket = await ticketService.createTicket(ticketData);

      if (audioBlob) {
        await ticketService.uploadVoiceNote(newTicket.id, audioBlob);
      }

      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      console.error('Error submitting complaint:', err);
      setError(err.message || 'Failed to submit complaint. Please try again.');
      setSuccess(false);
    } finally {
      setSubmitting(false);
    }
  };

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="new-complaint-container">
      <div className="new-complaint-form">
        {/* Progress Bar */}
        <div className="progress-bar">
          <div className="progress-step">
            <div className={`step-number ${currentStep >= 1 ? 'active' : ''}`}>1</div>
            <span className="step-label">Channel & Brand</span>
          </div>
          <div className="progress-step">
            <div className={`step-number ${currentStep >= 2 ? 'active' : ''}`}>2</div>
            <span className="step-label">Details</span>
          </div>
          <div className="progress-step">
            <div className={`step-number ${currentStep >= 3 ? 'active' : ''}`}>3</div>
            <span className="step-label">Review & Submit</span>
          </div>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="alert alert-success">
            <i className="fas fa-check-circle"></i>
            Complaint submitted successfully! Redirecting to dashboard...
          </div>
        )}
        {error && (
          <div className="alert alert-danger">
            <i className="fas fa-exclamation-circle"></i>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={success ? 'disabled' : ''}>
          {/* Step 1: Channel & Brand Selection */}
          {currentStep === 1 && (
            <div className="step-content">
              <h2>Choose Channel & Brand</h2>
              
              <div className="form-section">
                <h3>How would you like to submit your complaint?</h3>
                <div className="channel-grid">
                  {channels.map(channel => (
                    <div 
                      key={channel.id}
                      className={`channel-option ${formData.channel === channel.id ? 'selected' : ''}`}
                      onClick={() => handleInputChange('channel', channel.id)}
                    >
                      <div className="channel-icon">{channel.icon}</div>
                      <div className="channel-info">
                        <h4>{channel.name}</h4>
                        <p>{channel.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-section">
                <h3>Select the brand you're complaining about</h3>
                <div className="brand-selection">
                  <select 
                    value={formData.brandId} 
                    onChange={(e) => handleInputChange('brandId', e.target.value)}
                    className="form-select"
                    required
                  >
                    <option value="">Select a brand...</option>
                    {brands.map((brand) => (
                      <option key={brand.id} value={brand.id}>
                        {brand.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="step-actions">
                <button type="button" onClick={nextStep} className="btn btn-primary" disabled={!formData.brandId}>
                  Next Step
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Complaint Details */}
          {currentStep === 2 && (
            <div className="step-content">
              <h2>Complaint Details</h2>
              
              <div className="form-section">
                <label className="form-label">Complaint Title *</label>
                <input 
                  type="text" 
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  className="form-control"
                  placeholder="Brief description of your complaint"
                  required
                />
              </div>

              <div className="form-section">
                <label className="form-label">Category</label>
                <select 
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  className="form-select"
                >
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name} - {category.description}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-section">
                <label className="form-label">Urgency Level</label>
                <div className="urgency-grid">
                  {urgencyLevels.map(urgency => (
                    <div 
                      key={urgency.id}
                      className={`urgency-option ${formData.urgency === urgency.id ? 'selected' : ''}`}
                      onClick={() => handleInputChange('urgency', urgency.id)}
                    >
                      <div className="urgency-info">
                        <h4>{urgency.name}</h4>
                        <p>{urgency.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-section">
                <label className="form-label">Description</label>
                <div className="description-options">
                  <div className="option-tabs">
                    <button 
                      type="button" 
                      className={`tab-btn ${!audioBlob ? 'active' : ''}`}
                      onClick={() => setAudioBlob(null)}
                    >
                      <i className="fas fa-keyboard"></i> Type
                    </button>
                    <button 
                      type="button" 
                      className={`tab-btn ${audioBlob ? 'active' : ''}`}
                    >
                      <i className="fas fa-microphone"></i> Voice
                    </button>
                  </div>
                  
                  {!audioBlob ? (
                    <textarea 
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      className="form-control"
                      rows="5"
                      placeholder="Describe your complaint in detail..."
                    />
                  ) : (
                    <div className="voice-recorder-section">
                      <VoiceRecorder onRecordingComplete={setAudioBlob} />
                      {audioBlob && (
                        <div className="audio-preview">
                          <audio controls src={URL.createObjectURL(audioBlob)} />
                          <button 
                            type="button" 
                            onClick={() => setAudioBlob(null)}
                            className="btn btn-outline-secondary btn-sm"
                          >
                            <i className="fas fa-times"></i> Remove
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="form-section">
                <label className="form-label">
                  <input 
                    type="checkbox"
                    checked={formData.isPublic}
                    onChange={(e) => handleInputChange('isPublic', e.target.checked)}
                  />
                  Make this complaint public (visible to others)
                </label>
                <small className="form-text">
                  Public complaints help other users and encourage faster brand responses
                </small>
              </div>

              <div className="step-actions">
                <button type="button" onClick={prevStep} className="btn btn-outline-secondary">
                  Previous
                </button>
                <button type="button" onClick={nextStep} className="btn btn-primary" disabled={!formData.title}>
                  Next Step
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Review & Submit */}
          {currentStep === 3 && (
            <div className="step-content">
              <h2>Review & Submit</h2>
              
              <div className="review-section">
                <h3>Review Your Complaint</h3>
                
                <div className="review-item">
                  <label>Channel:</label>
                  <span>{channels.find(c => c.id === formData.channel)?.name}</span>
                </div>
                
                <div className="review-item">
                  <label>Brand:</label>
                  <span>{brands.find(b => b.id === parseInt(formData.brandId))?.name}</span>
                </div>
                
                <div className="review-item">
                  <label>Title:</label>
                  <span>{formData.title}</span>
                </div>
                
                <div className="review-item">
                  <label>Category:</label>
                  <span>{categories.find(c => c.id === formData.category)?.name}</span>
                </div>
                
                <div className="review-item">
                  <label>Urgency:</label>
                  <span>{urgencyLevels.find(u => u.id === formData.urgency)?.name}</span>
                </div>
                
                <div className="review-item">
                  <label>Description:</label>
                  <span>{formData.description || 'Voice recording provided'}</span>
                </div>
                
                <div className="review-item">
                  <label>Public:</label>
                  <span>{formData.isPublic ? 'Yes' : 'No'}</span>
                </div>
              </div>

              <div className="step-actions">
                <button type="button" onClick={prevStep} className="btn btn-outline-secondary">
                  Previous
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-paper-plane"></i>
                      Submit Complaint
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default NewComplaint;
