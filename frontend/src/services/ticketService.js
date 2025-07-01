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
        console.log('Creating ticket with data:', ticketData);
        const response = await apiClient.post('/tickets/', ticketData);
        console.log('Ticket created successfully:', response.data);
        return response.data;
    } catch (error) {
        console.error('Error creating ticket:', error.message || error);
        if (error.response) {
            console.error('Backend error response:', error.response);
        }
        
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
        console.log('updateTicket called with:', { ticketId, ticketData });
        
        // Check if we have a token
        const token = localStorage.getItem('token');
        console.log('Auth token:', token ? 'Present' : 'Missing');
        
        const response = await apiClient.patch(`/tickets/${ticketId}`, ticketData);
        console.log('updateTicket response:', response);
        return response.data;
    } catch (error) {
        console.error('Error updating ticket:', error);
        console.error('Error details:', {
            message: error.message,
            status: error.status,
            data: error.data
        });
        
        // Extract specific error message from backend
        let errorMessage = 'Failed to update ticket. Please try again.';
        if (error.response && error.response.data) {
            if (error.response.data.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.response.data.message) {
                errorMessage = error.response.data.message;
            }
        } else if (error.data && error.data.detail) {
            errorMessage = error.data.detail;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        // Throw error with specific message
        throw new Error(errorMessage);
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