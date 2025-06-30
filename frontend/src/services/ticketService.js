import apiClient from './apiClient';

// Mockup ticket data
const MOCK_TICKETS = [
  {
    id: 1,
    title: 'Order not delivered',
    description: 'I placed an order two weeks ago and it has not arrived.',
    status: 'new',
    brand: { name: 'Acme Corp' },
    owner: { full_name: 'John Doe', email: 'john@example.com' },
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    title: 'Refund not processed',
    description: 'Requested a refund but have not received it yet.',
    status: 'in-progress',
    brand: { name: 'ShopEasy' },
    owner: { full_name: 'Jane Smith', email: 'jane@example.com' },
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 3,
    title: 'Product was defective',
    description: 'The product stopped working after one day.',
    status: 'resolved',
    brand: { name: 'GadgetPro' },
    owner: { full_name: 'Alice Brown', email: 'alice@example.com' },
    created_at: new Date(Date.now() - 2 * 86400000).toISOString(),
  },
];

const getTickets = async () => {
  try {
    const response = await apiClient.get('/tickets/');
    return response.data;
  } catch (error) {
    console.error('Error fetching tickets:', error.message || error);
    // Return mockup data as fallback
    return MOCK_TICKETS;
  }
};

const getTicketById = async (ticketId) => {
  try {
    const response = await apiClient.get(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching ticket:', error.message || error);
    // Optionally return a mock ticket or error
    return MOCK_TICKETS.find(t => t.id === ticketId) || null;
  }
};

const createTicket = async (ticketData) => {
    try {
        const response = await apiClient.post('/tickets/', ticketData);
        return response.data;
    } catch (error) {
        console.error('Error creating ticket:', error.message || error);
        
        // Extract specific error message from backend
        let errorMessage = 'Failed to create ticket. Please try again.';
        if (error.response && error.response.data) {
            if (error.response.data.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.response.data.message) {
                errorMessage = error.response.data.message;
            }
        }
        
        // Throw error with specific message
        throw new Error(errorMessage);
    }
};

const updateTicket = async (ticketId, ticketData) => {
    try {
        const response = await apiClient.put(`/tickets/${ticketId}`, ticketData);
        return response.data;
    } catch (error) {
        console.error('Error updating ticket:', error.message || error);
        throw error;
    }
};

const uploadVoiceNote = async (ticketId, formData) => {
    try {
        const response = await apiClient.post(`/tickets/${ticketId}/voice`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading voice note:', error.message || error);
        throw error;
    }
};

export default {
  getTickets,
  getTicketById,
  createTicket,
  updateTicket,
  uploadVoiceNote,
};