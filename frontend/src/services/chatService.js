// This is a mocked service for the chat functionality.

import apiClient from './apiClient';

// Mock responses for when backend is not available
const mockResponses = [
    "I understand your concern. Let me help you with that. Could you please provide more details about when this issue occurred?",
    "Thank you for bringing this to our attention. I'm documenting your complaint and will ensure it gets proper attention.",
    "I can see this is important to you. Let me gather some additional information to better assist you.",
    "I'm here to help resolve your issue. Could you please tell me what specific outcome you're looking for?",
    "I appreciate you taking the time to report this. Let me ask a few questions to better understand the situation.",
    "I'm processing your complaint now. To help me assist you better, could you provide any relevant order numbers or reference codes?",
    "Thank you for your patience. I'm working on your case and will make sure it gets the attention it deserves.",
    "I understand this is frustrating. Let me help you get this resolved as quickly as possible."
];

const getRandomMockResponse = () => {
    const randomIndex = Math.floor(Math.random() * mockResponses.length);
    return mockResponses[randomIndex];
};

const sendMessage = async (sessionId, message) => {
    try {
        const response = await apiClient.post(`/chat/send`, { sessionId, message });
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error.message || error);
        throw error;
    }
};

const getMessages = async (sessionId) => {
    try {
        const response = await apiClient.get(`/chat/messages/${sessionId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching messages:', error.message || error);
        throw error;
    }
};

const getChatHistory = async (ticketId) => {
    try {
        const response = await apiClient.get(`/chat/history/${ticketId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching chat history:', error);
        // Return mock chat history
        return {
            messages: [
                {
                    sender: 'bot',
                    text: 'Hello! I\'m here to help you with your complaint. How can I assist you today?',
                    timestamp: new Date().toISOString()
                }
            ]
        };
    }
};

const startChat = async (ticketId) => {
    try {
        const response = await apiClient.post(`/chat/start/${ticketId}`);
        return response.data;
    } catch (error) {
        console.error('Error starting chat:', error.message || error);
        // Return mock success response
        return {
            success: true,
            session_id: 'mock-session-' + Date.now(),
            message: 'Chat session started successfully'
        };
    }
};

export default {
    sendMessage,
    getMessages,
    getChatHistory,
    startChat
};