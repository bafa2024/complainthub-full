import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

export const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Mockup mode configuration
const MOCKUP_MODE = true; // Set to true to enable mockup mode
const MOCK_USER = {
  id: 1,
  email: 'demo@example.com',
  full_name: 'Demo User',
  role: 'user', // Can be 'user', 'brand_user', or 'admin'
  phone_number: '+1234567890'
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [mockupMode, setMockupMode] = useState(MOCKUP_MODE);

  useEffect(() => {
    // Check if user is logged in on mount
    const initAuth = async () => {
      if (mockupMode) {
        // Mockup mode: Set mock user data
        setUser(MOCK_USER);
        setIsAuthenticated(true);
        setToken('mock-token');
        setLoading(false);
        return;
      }

      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setIsAuthenticated(true);
          setToken(storedToken);
        } catch (error) {
          console.error('Failed to get current user:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [mockupMode]);

  const login = async (email, password) => {
    if (mockupMode) {
      // Mockup mode: Return mock user data
      const mockUser = { ...MOCK_USER };
      setUser(mockUser);
      setIsAuthenticated(true);
      setToken('mock-token');
      return mockUser;
    }

    try {
      const response = await authService.login(email, password);
      const { access_token } = response;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Get user data after login
      const userData = await authService.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
      
      return userData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const signup = async (userData) => {
    if (mockupMode) {
      // Mockup mode: Return success response
      return { message: 'Mock signup successful' };
    }

    try {
      const response = await authService.signup(userData);
      return response;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const logout = () => {
    if (mockupMode) {
      // Mockup mode: Reset to mock user
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      setToken('mock-token');
      return;
    }

    authService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setToken(null);
  };

  const switchMockRole = (newRole) => {
    if (mockupMode) {
      const updatedUser = { ...MOCK_USER, role: newRole };
      setUser(updatedUser);
    }
  };

  const toggleMockupMode = () => {
    setMockupMode(!mockupMode);
    if (!mockupMode) {
      // Enable mockup mode
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      setToken('mock-token');
    } else {
      // Disable mockup mode
      setUser(null);
      setIsAuthenticated(false);
      setToken(null);
    }
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    token,
    login,
    logout,
    signup,
    mockupMode,
    switchMockRole,
    toggleMockupMode,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};