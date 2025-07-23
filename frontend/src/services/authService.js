import apiClient from './apiClient';

const login = async (email, password) => {
    try {
        // The backend expects username and password in form data
        const form = new URLSearchParams();
        form.append('username', email);
        form.append('password', password);
        
        const response = await apiClient.post('/login/access-token', form, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        // The backend returns { access_token, token_type }
        const { access_token } = response.data;
        
        // Store the token
        localStorage.setItem('token', access_token);
        
        // Get user data with the token
        const userResponse = await apiClient.get('/users/me', {
            headers: { 'Authorization': `Bearer ${access_token}` }
        });
        
        // Return the user data for the AuthContext
        return { access_token, user: userResponse.data };
    } catch (error) {
        console.error('Login failed:', error.message || error);
        throw error;
    }
};

const signup = async (userData) => {
    try {
        // Transform the data to match backend expectations
        const signupData = {
            email: userData.email,
            full_name: userData.full_name,
            password: userData.password
        };
        
        // Add brand-specific data if provided
        if (userData.brand_name) {
            signupData.brand_name = userData.brand_name;
            signupData.role = 'brand_user';
        }
        
        const response = await apiClient.post('/auth/signup', signupData);
        
        // Backend returns { access_token, token_type, user }
        const { access_token, user } = response.data;
        
        // Store the token
        localStorage.setItem('token', access_token);
        
        return { access_token, user };
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