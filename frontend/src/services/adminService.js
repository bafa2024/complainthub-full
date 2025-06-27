// frontend/src/services/adminService.js

import apiClient from './apiClient';

const getAllUsers = async () => {
    try {
        const response = await apiClient.get('/admin/users');
        return response.data;
    } catch (error) {
        console.error('Error fetching users:', error.response?.data);
        throw error;
    }
};

const getAllBrands = async () => {
    try {
        const response = await apiClient.get('/admin/brands');
        return response.data;
    } catch (error) {
        console.error('Error fetching brands:', error.response?.data);
        throw error;
    }
};

// We can use the existing brandService for creation
// and the admin endpoint for updates

export default {
    getAllUsers,
    getAllBrands,
};