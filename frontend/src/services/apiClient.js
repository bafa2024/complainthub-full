// frontend/src/services/authService.js
import apiClient from './apiClient';

const login = async (email, password) => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const response = await apiClient.post('/login/access-token', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
};

const signup = async (userData) => {
    const response = await apiClient.post('/auth/signup', userData);
    return response.data;
};

const getCurrentUser = async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
};

const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
};

export default {
    login,
    signup,
    getCurrentUser,
    logout,
};