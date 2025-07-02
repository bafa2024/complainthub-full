import apiClient from './apiClient';

const getBrands = async () => {
  try {
    const response = await apiClient.get('/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error.message || error);
    throw error;
  }
};

const createBrand = async (brandData) => {
  try {
    const response = await apiClient.post('/brands', brandData);
    return response.data;
  } catch (error) {
    console.error('Error creating brand:', error.message || error);
    throw error;
  }
};

const updateBrand = async (brandId, brandData) => {
  try {
    const response = await apiClient.put(`/brands/${brandId}`, brandData);
    return response.data;
  } catch (error) {
    console.error('Error updating brand:', error.message || error);
    throw error;
  }
};

const getBrandById = async (brandId) => {
  try {
    const response = await apiClient.get(`/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching brand:', error.message || error);
    throw error;
  }
};

const getCurrentUserBrand = async () => {
  try {
    // First get the current user to get their brand_id
    const userResponse = await apiClient.get('/auth/me');
    const user = userResponse.data;
    
    if (!user.brand_id) {
      throw new Error('User is not associated with any brand');
    }
    
    // Then get the brand details
    const brandResponse = await apiClient.get(`/brands/${user.brand_id}`);
    return brandResponse.data;
  } catch (error) {
    console.error('Error fetching current user brand:', error.message || error);
    throw error;
  }
};

const updateCurrentUserBrand = async (brandData) => {
  try {
    // First get the current user to get their brand_id
    const userResponse = await apiClient.get('/auth/me');
    const user = userResponse.data;
    
    if (!user.brand_id) {
      throw new Error('User is not associated with any brand');
    }
    
    // Then update the brand
    const response = await apiClient.put(`/brands/${user.brand_id}`, brandData);
    return response.data;
  } catch (error) {
    console.error('Error updating current user brand:', error.message || error);
    throw error;
  }
};

const deleteBrand = async (brandId) => {
  try {
    const response = await apiClient.delete(`/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting brand:', error.message || error);
    throw error;
  }
};

export default {
  getBrands,
  createBrand,
  updateBrand,
  getBrandById,
  getCurrentUserBrand,
  updateCurrentUserBrand,
  deleteBrand,
};