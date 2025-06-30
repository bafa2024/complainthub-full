// frontend/src/services/apiClient.js
import axios from 'axios';

// Set your API base URL here - use Vite's import.meta.env instead of process.env
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create an axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 seconds
});

// Add a request interceptor (optional, e.g., for auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    // Example: Attach token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Request error
    return Promise.reject(error);
  }
);

// Add a response interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log error
    console.error('API Error:', error);
    // Optionally show a toast/notification here
    // Return a consistent error object
    if (error.response) {
      // Server responded with a status outside 2xx
      return Promise.reject({
        message: error.response.data?.detail || error.response.data?.error || error.message,
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      // No response received
      return Promise.reject({
        message: 'No response from server. Please check your network connection.',
        status: null,
        data: null,
      });
    } else {
      // Something else happened
      return Promise.reject({
        message: error.message || 'Unknown error occurred',
        status: null,
        data: null,
      });
    }
  }
);

// Auth functions
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

// Export the axios instance as default
export default apiClient;

// Export auth functions separately
export const authService = {
    login,
    signup,
    getCurrentUser,
    logout,
};