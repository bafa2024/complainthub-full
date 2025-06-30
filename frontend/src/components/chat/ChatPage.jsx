import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import chatService from '../../services/chatService';
import './ChatPage.css';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const { user } = useAuth();
  const messagesEndRef = useRef(null);
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const ticketId = params.get('ticketId');
  const sessionId = params.get('sessionId');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Fetch chat history for the ticket on mount
  useEffect(() => {
    const fetchHistory = async () => {
      if (!ticketId) return;
      try {
        const history = await chatService.getChatHistory(ticketId);
        setMessages(history.messages || []);
      } catch (err) {
        setMessages([
          {
            sender: 'bot',
            text: 'Hello! I am the ComplaintHub AI assistant. How can I help you today?',
            timestamp: new Date().toISOString()
          }
        ]);
      }
    };
    fetchHistory();
    // eslint-disable-next-line
  }, [ticketId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const userMessage = {
      sender: 'user',
      text: newMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    // Send message to backend with sessionId
    try {
      const botResponse = await chatService.sendMessage(sessionId, newMessage);
      setIsTyping(false);
      setMessages(prev => [...prev, botResponse]);
    } catch (err) {
      setIsTyping(false);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Sorry, there was a problem sending your message. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    }
  };

  return (
    <div className="chat-page-container">
      <div className="chat-window card shadow-lg">
        <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Support Chat</h5>
          <Link to="/dashboard" className="btn-close btn-close-white"></Link>
        </div>
        <div className="card-body chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}>
              <div className="message-bubble">
                {msg.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-row bot-message">
                <div className="message-bubble typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="card-footer">
          <form onSubmit={handleSendMessage} className="d-flex">
            <input
              type="text"
              className="form-control"
              placeholder="Type your message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              disabled={isTyping}
            />
            <button type="submit" className="btn btn-primary ms-2" disabled={isTyping}>
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;