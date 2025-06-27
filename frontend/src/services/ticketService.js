// Mock ticket service for demo
const mockTickets = [
  {
    id: 1,
    title: "Late Delivery for Order #123",
    description: "My order was supposed to arrive yesterday but it's still not here.",
    status: "new",
    category: "complaint",
    urgency: "high",
    channel: "web",
    brand: { id: 1, name: "E-Commerce Inc." },
    owner: { id: 1, full_name: "John Doe", email: "john@example.com" },
    created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    title: "Product arrived damaged",
    description: "The package was damaged and the product inside was broken.",
    status: "in-progress",
    category: "complaint",
    urgency: "medium",
    channel: "whatsapp",
    brand: { id: 1, name: "E-Commerce Inc." },
    owner: { id: 2, full_name: "Jane Smith", email: "jane@example.com" },
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
  },
  {
    id: 3,
    title: "Cannot reset my password",
    description: "I've tried multiple times but the reset email never arrives.",
    status: "resolved",
    category: "support",
    urgency: "low",
    channel: "web",
    brand: { id: 2, name: "SaaS Platform" },
    owner: { id: 3, full_name: "Peter Jones", email: "peter@example.com" },
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    resolved_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
  },
];

const getTickets = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  return mockTickets;
};

const getTicketById = async (ticketId) => {
  await new Promise(resolve => setTimeout(resolve, 300));
  const ticket = mockTickets.find(t => t.id === parseInt(ticketId));
  if (!ticket) {
    throw new Error('Ticket not found');
  }
  return ticket;
};

const createTicket = async (ticketData) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const newTicket = {
    ...ticketData,
    id: mockTickets.length + 1,
    status: "new",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  };
  mockTickets.push(newTicket);
  return newTicket;
};

const updateTicket = async (ticketId, updateData) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const ticketIndex = mockTickets.findIndex(t => t.id === parseInt(ticketId));
  if (ticketIndex !== -1) {
    mockTickets[ticketIndex] = {
      ...mockTickets[ticketIndex],
      ...updateData,
      updated_at: new Date().toISOString(),
    };
    return mockTickets[ticketIndex];
  }
  throw new Error('Ticket not found');
};

export default {
  getTickets,
  getTicketById,
  createTicket,
  updateTicket,
};