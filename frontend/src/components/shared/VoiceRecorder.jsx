import React, { useState, useRef, useEffect } from 'react';
import './VoiceRecorder.css';

const VoiceRecorder = ({
  onRecordingComplete,
  onRecordingStart,
  onRecordingStop,
  maxDuration = 300, // 5 minutes in seconds
  autoPlay = false,
  showWaveform = true,
  className = '',
  disabled = false,
  placeholder = 'Click to start recording...'
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const audioRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Check if browser supports MediaRecorder
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      setIsSupported(false);
      setError('Voice recording is not supported in this browser');
      return;
    }

    // Check for microphone permission
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => {
        setIsSupported(true);
        setError(null);
      })
      .catch(() => {
        setIsSupported(false);
        setError('Microphone access is required for voice recording');
      });

    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
  };

  const startRecording = async () => {
    if (disabled || !isSupported) return;

    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 44100
        } 
      });
      
      streamRef.current = stream;
      audioChunksRef.current = [];
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') 
          ? 'audio/webm' 
          : 'audio/mp4'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: mediaRecorder.mimeType 
        });
        setAudioBlob(audioBlob);
        
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        
        onRecordingComplete?.(audioBlob, url);
      };
      
      mediaRecorder.onerror = (event) => {
        setError('Recording failed: ' + event.error);
        stopRecording();
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
      
      onRecordingStart?.();
      
    } catch (err) {
      setError('Failed to start recording: ' + err.message);
    }
  };

  const stopRecording = () => {
    if (!isRecording) return;
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    setIsRecording(false);
    onRecordingStop?.();
  };

  const playAudio = () => {
    if (!audioRef.current || !audioUrl) return;
    
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleAudioTimeUpdate = () => {
    // This can be used for progress bar updates
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const deleteRecording = () => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    setAudioBlob(null);
    setAudioUrl(null);
    setRecordingTime(0);
  };

  const downloadRecording = () => {
    if (!audioBlob) return;
    
    const url = URL.createObjectURL(audioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recording-${new Date().toISOString().slice(0, 19)}.webm`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (!isSupported) {
    return (
      <div className={`voice-recorder error ${className}`}>
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`voice-recorder ${className}`}>
      {/* Error Display */}
      {error && (
        <div className="error-banner">
          <i className="fas fa-exclamation-circle"></i>
          <span>{error}</span>
          <button onClick={() => setError(null)} className="error-close">
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}

      {/* Recording Controls */}
      <div className="recording-controls">
        {!audioUrl ? (
          <button
            className={`record-button ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={disabled}
          >
            <div className="record-icon">
              {isRecording ? (
                <i className="fas fa-stop"></i>
              ) : (
                <i className="fas fa-microphone"></i>
              )}
            </div>
            <span className="record-text">
              {isRecording ? 'Stop Recording' : placeholder}
            </span>
          </button>
        ) : (
          <div className="playback-controls">
            <button
              className={`play-button ${isPlaying ? 'playing' : ''}`}
              onClick={playAudio}
              disabled={disabled}
            >
              <i className={`fas ${isPlaying ? 'fa-pause' : 'fa-play'}`}></i>
            </button>
            <div className="audio-info">
              <span className="audio-duration">
                {formatTime(Math.floor(audioRef.current?.duration || 0))}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Recording Timer */}
      {isRecording && (
        <div className="recording-timer">
          <div className="timer-display">
            <i className="fas fa-clock"></i>
            <span>{formatTime(recordingTime)}</span>
          </div>
          <div className="recording-indicator">
            <div className="pulse-dot"></div>
            <span>Recording...</span>
          </div>
        </div>
      )}

      {/* Audio Player */}
      {audioUrl && (
        <div className="audio-player">
          <audio
            ref={audioRef}
            src={audioUrl}
            onEnded={handleAudioEnded}
            onTimeUpdate={handleAudioTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            autoPlay={autoPlay}
          />
          
          {showWaveform && (
            <div className="waveform-container">
              <div className="waveform">
                {/* Simple waveform visualization */}
                {Array.from({ length: 50 }, (_, i) => (
                  <div
                    key={i}
                    className="waveform-bar"
                    style={{
                      height: `${Math.random() * 60 + 20}%`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  ></div>
                ))}
              </div>
            </div>
          )}
          
          <div className="audio-actions">
            <button
              onClick={downloadRecording}
              className="action-button"
              title="Download Recording"
            >
              <i className="fas fa-download"></i>
            </button>
            <button
              onClick={deleteRecording}
              className="action-button delete"
              title="Delete Recording"
            >
              <i className="fas fa-trash"></i>
            </button>
          </div>
        </div>
      )}

      {/* Progress Bar for Max Duration */}
      {isRecording && (
        <div className="progress-container">
          <div 
            className="progress-bar"
            style={{ 
              width: `${(recordingTime / maxDuration) * 100}%` 
            }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;