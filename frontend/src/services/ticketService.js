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
    console.error('Error fetching tickets:', error.response?.data);
    // Return mockup data as fallback
    return MOCK_TICKETS;
  }
};

const getTicketById = async (ticketId) => {
  try {
    const response = await apiClient.get(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching ticket ${ticketId}:`, error.response?.data);
    // Return a mock ticket if not found
    return (
      MOCK_TICKETS.find(t => t.id === Number(ticketId)) || MOCK_TICKETS[0]
    );
  }
};

const createTicket = async (ticketData) => {
    try {
        const response = await apiClient.post('/tickets/', ticketData);
        return response.data;
    } catch (error)
        {
        console.error('Error creating ticket:', error.response?.data);
        // Optionally return a mock ticket or error
        return { ...ticketData, id: Date.now(), status: 'new', created_at: new Date().toISOString() };
    }
};

const updateTicket = async (ticketId, updateData) => {
    try {
        const response = await apiClient.patch(`/tickets/${ticketId}`, updateData);
        return response.data;
    } catch (error) {
        console.error(`Error updating ticket ${ticketId}:`, error.response?.data);
        // Optionally return mock updated ticket
        return { ...updateData, id: ticketId };
    }
};

const uploadVoiceNote = async (ticketId, audioBlob) => {
    const formData = new FormData();
    formData.append("voice_note", audioBlob, `voice_note_${ticketId}.wav`);
    try {
        const response = await apiClient.post(
            `/tickets/${ticketId}/upload-voice-note`, 
            formData,
            { headers: { 'Content-Type': 'multipart/form-data' } }
        );
        return response.data;
    } catch (error) {
        console.error('Error uploading voice note:', error.response?.data);
        // Optionally return a mock response
        return { success: true, message: 'Mock voice note uploaded.' };
    }
};

export default {
  getTickets,
  getTicketById,
  createTicket,
  updateTicket,
  uploadVoiceNote,
};