// This is a mocked service for the chat functionality.

import apiClient from './apiClient';

const sendMessage = async (message) => {
    try {
        const response = await apiClient.post('/chat/send', { message });
        return response.data;
    } catch (error) {
        console.error('Error sending message:', error);
        throw error;
    }
};

const getChatHistory = async (ticketId) => {
    try {
        const response = await apiClient.get(`/chat/history/${ticketId}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching chat history:', error);
        throw error;
    }
};

const startChat = async (ticketId) => {
    try {
        const response = await apiClient.post(`/chat/start/${ticketId}`);
        return response.data;
    } catch (error) {
        console.error('Error starting chat:', error);
        throw error;
    }
};

export default {
    sendMessage,
    getChatHistory,
    startChat
};