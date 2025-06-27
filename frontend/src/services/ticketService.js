import apiClient from './apiClient';

const getTickets = async () => {
  try {
    const response = await apiClient.get('/tickets/');
    return response.data;
  } catch (error) {
    console.error('Error fetching tickets:', error);
    // Return empty array as fallback
    return [];
  }
};

const getTicketById = async (ticketId) => {
  try {
    const response = await apiClient.get(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching ticket ${ticketId}:`, error);
    throw error;
  }
};

const createTicket = async (ticketData) => {
  try {
    const response = await apiClient.post('/tickets/', ticketData);
    return response.data;
  } catch (error) {
    console.error('Error creating ticket:', error);
    throw error;
  }
};

const updateTicket = async (ticketId, updateData) => {
  try {
    const response = await apiClient.patch(`/tickets/${ticketId}`, updateData);
    return response.data;
  } catch (error) {
    console.error(`Error updating ticket ${ticketId}:`, error);
    throw error;
  }
};

export default {
  getTickets,
  getTicketById,
  createTicket,
  updateTicket,
};