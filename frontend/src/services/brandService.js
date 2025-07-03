import apiClient from './apiClient';

const getBrands = async () => {
  try {
    // Use the admin endpoint for getting all brands
    const response = await apiClient.get('/admin/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error.message || error);
    throw error;
  }
};

const createBrand = async (brandData) => {
  try {
    // Use the admin endpoint for brand creation
    const response = await apiClient.post('/admin/brands', brandData);
    return response.data;
  } catch (error) {
    console.error('Error creating brand:', error);
    // Re-throw the error with more context
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to create brands. Please contact an administrator.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Invalid brand data. Please check your input.');
    } else if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.');
    } else {
      throw error;
    }
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
    // Use the admin endpoint for brand deletion
    const response = await apiClient.delete(`/admin/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting brand:', error);
    // Re-throw the error with more context
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to delete brands. Please contact an administrator.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Cannot delete brand. Please check for related data.');
    } else if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.');
    } else if (error.response?.status === 404) {
      throw new Error('Brand not found.');
    } else {
      throw error;
    }
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