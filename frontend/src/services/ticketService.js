// --- MOCKED TICKET SERVICE FOR UI TESTING ---

// We are defining a fake list of tickets to return.
const mockTickets = [
  {
    id: 1,
    title: "Late Delivery for Order #123",
    status: "new",
    brand: { name: "E-Commerce Inc." },
    owner: { full_name: "John Doe" },
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    title: "Product arrived damaged",
    status: "in-progress",
    brand: { name: "E-Commerce Inc." },
    owner: { full_name: "Jane Smith" },
    created_at: new Date().toISOString(),
  },
  {
    id: 3,
    title: "Cannot reset my password",
    status: "resolved",
    brand: { name: "SaaS Platform" },
    owner: { full_name: "Peter Jones" },
    created_at: new Date().toISOString(),
  },
];

const getTickets = async () => {
  console.log("Mocking API call: Returning fake ticket data.");
  // The function now immediately returns our mock data instead of calling the backend.
  return Promise.resolve(mockTickets);
};

const getTicketById = async (ticketId) => {
    console.log(`Mocking API call for ticket ID: ${ticketId}`);
    // Find the ticket in our mock list or return the first one as a fallback.
    const ticket = mockTickets.find(t => t.id === parseInt(ticketId)) || mockTickets[0];
    return Promise.resolve(ticket);
};

const createTicket = async (ticketData) => {
    console.log("Mocking API call: createTicket", ticketData);
    return Promise.resolve({ ...ticketData, id: Math.floor(Math.random() * 1000) });
};

const updateTicket = async (ticketId, updateData) => {
    console.log(`Mocking API call: updateTicket ${ticketId}`, updateData);
    return Promise.resolve({ id: ticketId, ...updateData });
};


export default {
  getTickets,
  getTicketById,
  createTicket,
  updateTicket,
};