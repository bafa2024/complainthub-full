import apiClient from './apiClient';

const getBrands = async () => {
  try {
    const response = await apiClient.get('/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error);
    throw error;
  }
};

const createBrand = async (brandData) => {
  try {
    const response = await apiClient.post('/brands', brandData);
    return response.data;
  } catch (error) {
    console.error('Error creating brand:', error);
    throw error;
  }
};

const updateBrand = async (brandId, brandData) => {
  try {
    const response = await apiClient.put(`/brands/${brandId}`, brandData);
    return response.data;
  } catch (error) {
    console.error('Error updating brand:', error);
    throw error;
  }
};

const getBrandById = async (brandId) => {
  try {
    const response = await apiClient.get(`/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching brand:', error);
    throw error;
  }
};

export default {
  getBrands,
  createBrand,
  updateBrand,
  getBrandById,
};