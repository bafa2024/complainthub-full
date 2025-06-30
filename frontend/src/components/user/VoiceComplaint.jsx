import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './VoiceComplaint.css';

export default function VoiceComplaint() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const [brands] = useState([
    { id: 1, name: 'TechCorp', logo: 'TC', category: 'Technology' },
    { id: 2, name: 'FoodExpress', logo: 'FE', category: 'Food & Beverage' },
    { id: 3, name: 'FashionHub', logo: 'FH', category: 'Fashion' },
    { id: 4, name: 'HomeGoods', logo: 'HG', category: 'Home & Garden' },
    { id: 5, name: 'AutoZone', logo: 'AZ', category: 'Automotive' },
    { id: 6, name: 'HealthPlus', logo: 'HP', category: 'Healthcare' }
  ]);

  const [filteredBrands, setFilteredBrands] = useState(brands);

  useEffect(() => {
    setFilteredBrands(
      brands.filter(brand => 
        brand.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        brand.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
  }, [searchQuery, brands]);

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        setIsProcessing(true);
        
        // Simulate transcription processing
        setTimeout(() => {
          setTranscription('I received a defective smartphone that has several issues including a cracked screen, non-functional camera, and battery that drains within 2 hours. The device was purchased brand new and should be in perfect condition.');
          setIsProcessing(false);
        }, 3000);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    // Stop recording logic would go here
  };

  const retryRecording = () => {
    setAudioBlob(null);
    setAudioUrl('');
    setTranscription('');
    setRecordingTime(0);
    setCurrentStep(2);
  };

  const handleBrandSelect = (brand) => {
    setSelectedBrand(brand);
    setCurrentStep(2);
  };

  const handleSubmit = () => {
    // Submit complaint logic
    navigate('/dashboard', { 
      state: { 
        message: 'Voice complaint submitted successfully!',
        type: 'success'
      }
    });
  };

  const steps = [
    { number: 1, label: 'Select Brand', status: currentStep >= 1 ? 'completed' : 'pending' },
    { number: 2, label: 'Record Complaint', status: currentStep >= 2 ? 'completed' : 'pending' },
    { number: 3, label: 'Review & Submit', status: currentStep >= 3 ? 'completed' : 'pending' }
  ];

  return (
    <div className="voice-complaint-page">
      {/* Header */}
      <div className="header">
        <div className="header-container">
          <div className="logo">ComplaintHub</div>
          <div className="header-nav">
            <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
              Cancel
            </button>
          </div>
        </div>
      </div>

      <div className="main-container">
        <div className="recording-container">
          <div className="recording-header">
            <h1>Voice Complaint</h1>
            <p>Record your complaint using your voice for a faster and more natural experience</p>
          </div>

          {/* Progress Steps */}
          <div className="progress-steps">
            {steps.map((step) => (
              <div key={step.number} className={`step ${step.status}`}>
                <div className="step-circle">
                  {step.status === 'completed' ? '✓' : step.number}
                </div>
                <div className="step-label">{step.label}</div>
              </div>
            ))}
          </div>

          {/* Step Content */}
          <div className="step-content">
            {/* Step 1: Brand Selection */}
            {currentStep === 1 && (
              <div className="step-content active">
                <div className="brand-search">
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Search for a brand..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>

                <div className="brands-grid">
                  {filteredBrands.map((brand) => (
                    <div
                      key={brand.id}
                      className="brand-card"
                      onClick={() => handleBrandSelect(brand)}
                    >
                      <div className="brand-logo">{brand.logo}</div>
                      <div className="brand-info">
                        <div className="brand-name">{brand.name}</div>
                        <div className="brand-category">{brand.category}</div>
                      </div>
                    </div>
                  ))}
                </div>

                {filteredBrands.length === 0 && (
                  <div className="no-results">
                    <p>No brands found matching "{searchQuery}"</p>
                    <button 
                      className="btn btn-outline"
                      onClick={() => setSearchQuery('')}
                    >
                      Clear Search
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Recording */}
            {currentStep === 2 && (
              <div className="step-content active">
                {selectedBrand && (
                  <div className="selected-brand">
                    <div className="brand-logo">{selectedBrand.logo}</div>
                    <div className="brand-info">
                      <div className="brand-name">{selectedBrand.name}</div>
                      <div className="brand-category">{selectedBrand.category}</div>
                    </div>
                  </div>
                )}

                {!audioBlob ? (
                  <div className="recording-interface">
                    <div className="recording-instructions">
                      <h3>Record Your Complaint</h3>
                      <p>Click the record button and speak clearly about your issue. You can record for up to 5 minutes.</p>
                    </div>

                    <div className="recording-controls">
                      {!isRecording ? (
                        <button 
                          className="record-button"
                          onClick={startRecording}
                        >
                          <span className="record-icon">🎤</span>
                          Start Recording
                        </button>
                      ) : (
                        <div className="recording-active">
                          <div className="recording-indicator">
                            <div className="pulse"></div>
                            Recording... {formatTime(recordingTime)}
                          </div>
                          <button 
                            className="stop-button"
                            onClick={stopRecording}
                          >
                            Stop Recording
                          </button>
                        </div>
                      )}
                    </div>

                    <div className="recording-tips">
                      <h4>Tips for better recording:</h4>
                      <ul>
                        <li>Speak clearly and at a normal pace</li>
                        <li>Find a quiet environment</li>
                        <li>Describe the issue in detail</li>
                        <li>Include relevant dates and order numbers</li>
                      </ul>
                    </div>
                  </div>
                ) : (
                  <div className="recording-review">
                    <h3>Review Your Recording</h3>
                    
                    <div className="audio-player">
                      <audio controls src={audioUrl}>
                        Your browser does not support the audio element.
                      </audio>
                    </div>

                    {isProcessing ? (
                      <div className="processing">
                        <div className="processing-spinner"></div>
                        <p>Processing your recording...</p>
                      </div>
                    ) : (
                      <div className="transcription">
                        <h4>Transcription:</h4>
                        <div className="transcription-text">
                          {transcription}
                        </div>
                        <button 
                          className="btn btn-outline"
                          onClick={() => setTranscription('')}
                        >
                          Edit Transcription
                        </button>
                      </div>
                    )}

                    <div className="recording-actions">
                      <button 
                        className="btn btn-outline"
                        onClick={retryRecording}
                      >
                        Record Again
                      </button>
                      <button 
                        className="btn btn-primary"
                        onClick={() => setCurrentStep(3)}
                        disabled={isProcessing}
                      >
                        Continue
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Review & Submit */}
            {currentStep === 3 && (
              <div className="step-content active">
                <div className="review-section">
                  <h3>Review Your Complaint</h3>
                  
                  <div className="review-card">
                    <div className="review-item">
                      <label>Brand:</label>
                      <span>{selectedBrand.name}</span>
                    </div>
                    
                    <div className="review-item">
                      <label>Recording Duration:</label>
                      <span>{formatTime(recordingTime)}</span>
                    </div>
                    
                    <div className="review-item">
                      <label>Transcription:</label>
                      <div className="transcription-preview">
                        {transcription}
                      </div>
                    </div>
                  </div>

                  <div className="submit-actions">
                    <button 
                      className="btn btn-outline"
                      onClick={() => setCurrentStep(2)}
                    >
                      Go Back
                    </button>
                    <button 
                      className="btn btn-success"
                      onClick={handleSubmit}
                    >
                      Submit Complaint
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 