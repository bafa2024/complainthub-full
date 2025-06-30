import apiClient from './apiClient';

// Mock data for admin dashboard
const MOCK_USERS = [
  { id: 1, full_name: 'John Doe', email: 'john@example.com', role: 'user' },
  { id: 2, full_name: 'Jane Smith', email: 'jane@example.com', role: 'user' },
  { id: 3, full_name: 'Alice Brown', email: 'alice@example.com', role: 'user' },
  { id: 4, full_name: 'Bob Wilson', email: 'bob@example.com', role: 'user' },
  { id: 5, full_name: 'Carol Davis', email: 'carol@example.com', role: 'user' },
];

const MOCK_BRANDS = [
  { id: 1, name: 'Acme Corp', email: 'contact@acme.com', status: 'active' },
  { id: 2, name: 'ShopEasy', email: 'support@shopeasy.com', status: 'active' },
  { id: 3, name: 'GadgetPro', email: 'help@gadgetpro.com', status: 'active' },
];

const getAllUsers = async () => {
  try {
    const response = await apiClient.get('/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error.message || error);
    // Return mock data as fallback
    return MOCK_USERS;
  }
};

const getAllBrands = async () => {
  try {
    const response = await apiClient.get('/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error.message || error);
    // Return mock data as fallback
    return MOCK_BRANDS;
  }
};

const getSystemStats = async () => {
  try {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching system stats:', error.message || error);
    // Return mock stats as fallback
    return {
      total_users: MOCK_USERS.length,
      total_brands: MOCK_BRANDS.length,
      total_tickets: 15,
      resolved_tickets: 8,
      resolution_rate: 53.3
    };
  }
};

const updateSystemSettings = async (settings) => {
  try {
    const response = await apiClient.put('/admin/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating system settings:', error.message || error);
    throw error;
  }
};

export default {
  getAllUsers,
  getAllBrands,
  getSystemStats,
  updateSystemSettings,
};