import apiClient from './apiClient';

const getAllUsers = async () => {
  try {
    const response = await apiClient.get('/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};

const getAllBrands = async () => {
  try {
    const response = await apiClient.get('/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error);
    throw error;
  }
};

const getSystemStats = async () => {
  try {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching system stats:', error);
    throw error;
  }
};

const updateSystemSettings = async (settings) => {
  try {
    const response = await apiClient.put('/admin/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating system settings:', error);
    throw error;
  }
};

export default {
  getAllUsers,
  getAllBrands,
  getSystemStats,
  updateSystemSettings,
};