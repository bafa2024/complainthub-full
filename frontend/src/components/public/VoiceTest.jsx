import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../services/apiClient';

const VoiceTest = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [error, setError] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [voiceProfile, setVoiceProfile] = useState(null);
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const audioRef = useRef(null);
  const responseAudioRef = useRef(null);
  
  const { user, token } = useAuth();

  useEffect(() => {
    if (user && token) {
      loadVoiceProfile();
      loadSupportedLanguages();
    }
  }, [user, token]);

  const loadVoiceProfile = async () => {
    try {
      const response = await apiClient.get('/voice/user-voice-profile', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.success) {
        setVoiceProfile(response.data);
      }
    } catch (error) {
      console.error('Error loading voice profile:', error);
    }
  };

  const loadSupportedLanguages = async () => {
    try {
      const response = await apiClient.get('/voice/supported-languages', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.success) {
        setSupportedLanguages(response.data.common_languages);
      }
    } catch (error) {
      console.error('Error loading supported languages:', error);
    }
  };

  const startRecording = async () => {
    try {
      setError('');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
        setAudioBlob(blob);
        
        // Create audio URL for playback
        const audioUrl = URL.createObjectURL(blob);
        if (audioRef.current) {
          audioRef.current.src = audioUrl;
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
      
    } catch (error) {
      console.error('Error starting recording:', error);
      setError('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceMessage = async () => {
    if (!audioBlob) {
      setError('No audio recorded');
      return;
    }

    setIsProcessing(true);
    setError('');
    setTranscription('');
    setAiResponse('');

    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.wav');
      formData.append('language', selectedLanguage);
      formData.append('brand_id', 1); // Default brand for testing
      formData.append('brand_context', 'This is a test brand for ComplaintHub voice processing');
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      console.log('Sending voice processing request...');

      const response = await apiClient.post('/voice/speech-to-text', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      console.log('Voice processing response:', response.data);

      if (response.data.success) {
        setTranscription(response.data.transcript);
        setAiResponse(response.data.ai_response);
        
        // Set session ID for conversation continuity
        if (response.data.session_id) {
          setSessionId(response.data.session_id);
        }

        // Play AI response audio if available
        if (response.data.audio_response) {
          const audioData = response.data.audio_response;
          const audioBlob = new Blob(
            [Uint8Array.from(atob(audioData), c => c.charCodeAt(0))], 
            { type: 'audio/mp3' }
          );
          const audioUrl = URL.createObjectURL(audioBlob);
          
          if (responseAudioRef.current) {
            responseAudioRef.current.src = audioUrl;
            responseAudioRef.current.play().catch(e => console.log('Audio play failed:', e));
          }
        }

        // Show success message if ticket was created
        if (response.data.ticket_created && response.data.ticket_id) {
          setTimeout(() => {
            setError(`✅ Ticket #${response.data.ticket_id} has been created successfully.`);
          }, 1000);
        }

      } else {
        throw new Error('Voice processing failed');
      }

    } catch (error) {
      console.error('Voice processing error:', error);
      
      let errorMessage = 'Sorry, voice processing failed. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = `Error: ${error.response.data.detail}`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }

      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const transcribeOnly = async () => {
    if (!audioBlob) {
      setError('No audio recorded');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.wav');
      formData.append('language', selectedLanguage);
      formData.append('detect_language', 'false');

      const response = await apiClient.post('/voice/transcribe-only', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        setTranscription(response.data.transcript);
        setAiResponse(`Transcription completed. Confidence: ${response.data.confidence}, Sentiment: ${response.data.sentiment}`);
      }

    } catch (error) {
      console.error('Transcription error:', error);
      setError('Transcription failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetSession = () => {
    setAudioBlob(null);
    setTranscription('');
    setAiResponse('');
    setError('');
    setSessionId(null);
    
    if (audioRef.current) {
      audioRef.current.src = '';
    }
    if (responseAudioRef.current) {
      responseAudioRef.current.src = '';
    }
  };

  if (!user) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          <h4>Authentication Required</h4>
          <p>Please log in to test the voice processing functionality.</p>
          <div className="mt-3">
            <a href="/login" className="btn btn-primary me-2">User Login</a>
            <a href="/admin/login" className="btn btn-secondary">Admin Login</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-md-10 mx-auto">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <i className="fas fa-microphone me-2"></i>
                Voice Processing Test - ComplaintHub
              </h5>
              <div>
                {sessionId && (
                  <small className="text-muted me-3">Session: {sessionId.slice(0, 8)}...</small>
                )}
                <button className="btn btn-sm btn-outline-secondary" onClick={resetSession}>
                  <i className="fas fa-refresh me-1"></i>
                  Reset
                </button>
              </div>
            </div>
            
            <div className="card-body">
              {/* Language Selection */}
              <div className="row mb-4">
                <div className="col-md-6">
                  <label className="form-label">Language:</label>
                  <select 
                    className="form-select" 
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    disabled={isRecording}
                  >
                    {supportedLanguages.map(lang => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name} ({lang.native_name})
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-6">
                  <label className="form-label">Voice Profile:</label>
                  <div className="form-control bg-light">
                    {voiceProfile ? voiceProfile.assigned_voice : 'Loading...'} 
                    <small className="text-muted ms-2">
                      (User: {user.email})
                    </small>
                  </div>
                </div>
              </div>

              {/* Recording Controls */}
              <div className="text-center mb-4">
                <div className="mb-3">
                  <button
                    className={`btn ${isRecording ? 'btn-danger' : 'btn-primary'} btn-lg me-3`}
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing}
                  >
                    <i className={`fas ${isRecording ? 'fa-stop' : 'fa-microphone'} me-2`}></i>
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                  </button>
                  
                  {audioBlob && (
                    <>
                      <button
                        className="btn btn-success me-2"
                        onClick={processVoiceMessage}
                        disabled={isProcessing}
                      >
                        {isProcessing ? (
                          <span className="spinner-border spinner-border-sm me-2" />
                        ) : (
                          <i className="fas fa-robot me-2"></i>
                        )}
                        Process with AI
                      </button>
                      
                      <button
                        className="btn btn-outline-info"
                        onClick={transcribeOnly}
                        disabled={isProcessing}
                      >
                        <i className="fas fa-file-text me-2"></i>
                        Transcribe Only
                      </button>
                    </>
                  )}
                </div>
                
                {isRecording && (
                  <div className="alert alert-info">
                    <i className="fas fa-microphone-alt me-2 text-danger"></i>
                    <strong>Recording...</strong> Speak your complaint or question clearly.
                  </div>
                )}
              </div>

              {/* Audio Playback */}
              {audioBlob && (
                <div className="mb-4">
                  <h6>Your Recording:</h6>
                  <audio ref={audioRef} controls className="w-100" />
                </div>
              )}

              {/* Results */}
              {transcription && (
                <div className="mb-4">
                  <h6>Transcription:</h6>
                  <div className="bg-light p-3 rounded">
                    <i className="fas fa-quote-left me-2 text-muted"></i>
                    {transcription}
                    <i className="fas fa-quote-right ms-2 text-muted"></i>
                  </div>
                </div>
              )}

              {aiResponse && (
                <div className="mb-4">
                  <h6>AI Response:</h6>
                  <div className="bg-primary text-white p-3 rounded">
                    <i className="fas fa-robot me-2"></i>
                    {aiResponse}
                  </div>
                  
                  {/* AI Response Audio */}
                  <div className="mt-2">
                    <small className="text-muted">AI Voice Response:</small>
                    <audio ref={responseAudioRef} controls className="w-100 mt-1" />
                  </div>
                </div>
              )}

              {/* Error Display */}
              {error && (
                <div className={`alert ${error.includes('✅') ? 'alert-success' : 'alert-danger'}`}>
                  <i className={`fas ${error.includes('✅') ? 'fa-check-circle' : 'fa-exclamation-triangle'} me-2`}></i>
                  {error}
                </div>
              )}
            </div>
          </div>
          
          {/* Instructions */}
          <div className="mt-4">
            <div className="card">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="fas fa-info-circle me-2"></i>
                  Voice Processing Features
                </h6>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4">
                    <h6>Speech-to-Text (STT):</h6>
                    <ul className="small">
                      <li>High-accuracy transcription</li>
                      <li>Multi-language support</li>
                      <li>Sentiment analysis</li>
                      <li>Confidence scoring</li>
                    </ul>
                  </div>
                  <div className="col-md-4">
                    <h6>AI Processing:</h6>
                    <ul className="small">
                      <li>Contextual understanding</li>
                      <li>Follow-up questions</li>
                      <li>Automatic ticket creation</li>
                      <li>Intent classification</li>
                    </ul>
                  </div>
                  <div className="col-md-4">
                    <h6>Text-to-Speech (TTS):</h6>
                    <ul className="small">
                      <li>Natural voice synthesis</li>
                      <li>Personalized voices</li>
                      <li>Multi-language output</li>
                      <li>High-quality audio</li>
                    </ul>
                  </div>
                </div>
                
                <div className="mt-3">
                  <h6>Sample Voice Complaints:</h6>
                  <div className="row">
                    <div className="col-md-6">
                      <ul className="small">
                        <li>"My order number 12345 arrived damaged yesterday"</li>
                        <li>"I'm having trouble logging into your mobile app"</li>
                        <li>"Your website has been down for two hours"</li>
                      </ul>
                    </div>
                    <div className="col-md-6">
                      <ul className="small">
                        <li>"I want to cancel my subscription immediately"</li>
                        <li>"The customer service agent was very rude to me"</li>
                        <li>"I was charged twice for the same product"</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceTest;