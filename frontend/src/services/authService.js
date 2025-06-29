import apiClient from './apiClient';

const login = async (email, password) => {
    try {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const response = await apiClient.post('/login/access-token', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
    } catch (error) {
        console.error('Login failed:', error.message || error);
        throw error;
    }
};

const signup = async (userData) => {
    try {
    const response = await apiClient.post('/users/', userData);
    return response.data;
    } catch (error) {
        console.error('Signup failed:', error.message || error);
        throw error;
    }
};

const getCurrentUser = async () => {
    try {
    const response = await apiClient.get('/users/me');
    return response.data;
    } catch (error) {
        console.error('Fetching current user failed:', error.message || error);
        throw error;
    }
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