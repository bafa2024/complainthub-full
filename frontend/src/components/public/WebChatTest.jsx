import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../services/apiClient';

const WebChatTest = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setError('');

    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage, timestamp: new Date() }];
    setMessages(newMessages);

    try {
      // Prepare request data
      const requestData = {
        message: userMessage,
        session_id: sessionId,
        brand_id: 1, // Default brand for testing
        channel_type: 'webchat',
        language: 'en',
        brand_context: 'This is a test brand for ComplaintHub'
      };

      console.log('Sending chat request:', requestData);

      // Send to conversation endpoint
      const response = await apiClient.post('/conversation/chat', requestData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Chat response:', response.data);

      if (response.data.success) {
        // Set session ID if returned
        if (response.data.session_id && !sessionId) {
          setSessionId(response.data.session_id);
        }

        // Add AI response to chat
        const aiMessage = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          metadata: response.data.metadata,
          requires_followup: response.data.requires_followup,
          ticket_created: response.data.ticket_created,
          ticket_id: response.data.ticket_id
        };

        setMessages([...newMessages, aiMessage]);

        // Show success message if ticket was created
        if (response.data.ticket_created && response.data.ticket_id) {
          setTimeout(() => {
            setMessages(prev => [...prev, {
              role: 'system',
              content: `✅ Ticket #${response.data.ticket_id} has been created successfully.`,
              timestamp: new Date(),
              isSystem: true
            }]);
          }, 500);
        }
      } else {
        throw new Error('Failed to get AI response');
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      let errorMessage = 'Sorry, I encountered an error. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = `Error: ${error.response.data.detail}`;
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`;
      }

      setError(errorMessage);
      
      // Add error message to chat
      setMessages([...newMessages, {
        role: 'assistant',
        content: errorMessage,
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setSessionId(null);
    setError('');
    setInput('');
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (!user) {
    return (
      <div className="container mt-4">
        <div className="alert alert-warning">
          <h4>Authentication Required</h4>
          <p>Please log in to test the web chat functionality.</p>
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
        <div className="col-md-8 mx-auto">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">
                <i className="fas fa-robot me-2"></i>
                AI Chat Test - ComplaintHub
              </h5>
              <div>
                {sessionId && (
                  <small className="text-muted me-3">Session: {sessionId.slice(0, 8)}...</small>
                )}
                <button className="btn btn-sm btn-outline-secondary" onClick={resetChat}>
                  <i className="fas fa-refresh me-1"></i>
                  Reset
                </button>
              </div>
            </div>
            
            <div className="card-body p-0">
              {/* Chat Messages */}
              <div className="chat-messages" style={{ height: '400px', overflowY: 'auto', padding: '1rem' }}>
                {messages.length === 0 && (
                  <div className="text-center text-muted">
                    <i className="fas fa-comments fa-3x mb-3"></i>
                    <p>Welcome to ComplaintHub AI Assistant!</p>
                    <p>Start by typing your complaint or inquiry below.</p>
                  </div>
                )}
                
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`mb-3 d-flex ${message.role === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
                  >
                    <div
                      className={`max-width-70 ${
                        message.role === 'user'
                          ? 'bg-primary text-white'
                          : message.isSystem
                          ? 'bg-success text-white'
                          : message.isError
                          ? 'bg-danger text-white'
                          : 'bg-light'
                      } rounded p-3`}
                      style={{ maxWidth: '70%' }}
                    >
                      <div className="message-content">
                        {message.content}
                      </div>
                      <div className="message-meta mt-2">
                        <small className={`${message.role === 'user' || message.isSystem || message.isError ? 'text-white-50' : 'text-muted'}`}>
                          {formatTimestamp(message.timestamp)}
                          {message.role === 'assistant' && message.ticket_created && (
                            <span className="ms-2 badge bg-success">Ticket Created</span>
                          )}
                          {message.role === 'assistant' && message.requires_followup && (
                            <span className="ms-2 badge bg-warning">Follow-up</span>
                          )}
                        </small>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="d-flex justify-content-start mb-3">
                    <div className="bg-light rounded p-3">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                      <small className="text-muted">AI is thinking...</small>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>
              
              {/* Error Display */}
              {error && (
                <div className="alert alert-danger m-3 mb-0">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  {error}
                </div>
              )}
            </div>
            
            <div className="card-footer">
              {/* Chat Input */}
              <div className="input-group">
                <textarea
                  className="form-control"
                  placeholder="Type your message here..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  rows="2"
                  disabled={isLoading}
                />
                <button
                  className="btn btn-primary"
                  onClick={sendMessage}
                  disabled={!input.trim() || isLoading}
                >
                  {isLoading ? (
                    <span className="spinner-border spinner-border-sm me-1" />
                  ) : (
                    <i className="fas fa-paper-plane me-1"></i>
                  )}
                  Send
                </button>
              </div>
              
              <div className="mt-2">
                <small className="text-muted">
                  <i className="fas fa-info-circle me-1"></i>
                  Press Enter to send, Shift+Enter for new line. 
                  {user && <span className="ms-2">Logged in as: <strong>{user.email}</strong></span>}
                </small>
              </div>
            </div>
          </div>
          
          {/* Instructions */}
          <div className="mt-4">
            <div className="card">
              <div className="card-header">
                <h6 className="mb-0">
                  <i className="fas fa-lightbulb me-2"></i>
                  Testing Instructions
                </h6>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-6">
                    <h6>Sample Complaints:</h6>
                    <ul className="small">
                      <li>"My order #12345 was damaged when it arrived"</li>
                      <li>"I'm having trouble with your mobile app login"</li>
                      <li>"Your service has been down for 2 hours"</li>
                      <li>"I want to cancel my subscription"</li>
                    </ul>
                  </div>
                  <div className="col-md-6">
                    <h6>AI Features to Test:</h6>
                    <ul className="small">
                      <li>Follow-up questions for incomplete details</li>
                      <li>Automatic ticket creation</li>
                      <li>Sentiment analysis</li>
                      <li>Category classification</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <style jsx>{`
        .typing-indicator {
          display: flex;
          gap: 4px;
        }
        
        .typing-indicator span {
          height: 8px;
          width: 8px;
          background-color: #999;
          border-radius: 50%;
          animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
          0%, 80%, 100% { 
            transform: scale(0);
            opacity: 0.5;
          } 
          40% { 
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default WebChatTest;