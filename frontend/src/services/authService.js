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
    // This is the corrected line. We are now calling the '/users/' endpoint.
    const response = await apiClient.post('/users/', userData);
    return response.data;
};

const getCurrentUser = async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
};

const logout = () => {
    // This is handled in the AuthContext by removing the token.
    console.log("Logged out");
};

export default {
    login,
    signup,
    getCurrentUser,
    logout,
};