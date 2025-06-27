import apiClient from './apiClient';

const getBrands = async () => {
    try {
        const response = await apiClient.get('/brands/');
        return response.data;
    } catch (error) {
        console.error('Error fetching brands:', error.response?.data);
        throw error;
    }
};

const createBrand = async (brandData) => {
    try {
        // This endpoint is defined in backend/app/api/v1/endpoints/brands.py
        const response = await apiClient.post('/brands/', brandData);
        return response.data;
    } catch (error) {
        console.error('Error creating brand:', error.response?.data);
        throw error;
    }
};

const updateBrand = async (brandId, brandData) => {
    try {
        // This endpoint is defined in backend/app/api/v1/endpoints/admin.py
        const response = await apiClient.put(`/admin/brands/${brandId}`, brandData);
        return response.data;
    } catch (error) {
        console.error(`Error updating brand ${brandId}:`, error.response?.data);
        throw error;
    }
}

export default {
    getBrands,
    createBrand,
    updateBrand,
};