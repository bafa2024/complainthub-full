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
const MOCKUP_MODE = false; // Set to false to enable real API calls
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
        // Mockup mode: Set mock user data immediately
        console.log('🔧 Mockup mode enabled - using mock data');
        setUser(MOCK_USER);
        setIsAuthenticated(true);
        setToken('mock-token');
        localStorage.setItem('token', 'mock-token');
        setLoading(false);
        return;
      }

      // Only try API calls if not in mockup mode
      const storedToken = localStorage.getItem('token');
      if (storedToken && storedToken !== 'mock-token') {
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

  const login = async (formData) => {
    if (mockupMode) {
      // Mockup mode: Return mock user data
      console.log('🔧 Mockup login with:', formData.email);
      const mockUser = { ...MOCK_USER, email: formData.email };
      setUser(mockUser);
      setIsAuthenticated(true);
      setToken('mock-token');
      localStorage.setItem('token', 'mock-token');
      return mockUser;
    }

    try {
      const response = await authService.login(formData.email, formData.password);
      const { access_token, user } = response;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      
      return user;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const signup = async (userData) => {
    if (mockupMode) {
      // Mockup mode: Return success response
      console.log('🔧 Mockup signup with:', userData.email);
      const mockUser = {
        id: 2,
        email: userData.email,
        full_name: `${userData.firstName} ${userData.lastName}`,
        role: 'user',
        phone_number: userData.phone
      };
      setUser(mockUser);
      setIsAuthenticated(true);
      setToken('mock-token');
      localStorage.setItem('token', 'mock-token');
      return { message: 'Mock signup successful', user: mockUser };
    }

    try {
      // Transform frontend data to backend format
      const backendData = {
        email: userData.email,
        full_name: `${userData.firstName} ${userData.lastName}`,
        password: userData.password
      };
      
      // Add brand-specific data if this is a brand signup
      if (userData.brand_name) {
        backendData.brand_name = userData.brand_name;
        backendData.role = 'brand_user';
      }
      
      const response = await authService.signup(backendData);
      const { access_token, user } = response;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      setIsAuthenticated(true);
      
      return { message: 'Signup successful', user };
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  };

  const logout = () => {
    if (mockupMode) {
      // Mockup mode: Reset to mock user
      console.log('🔧 Mockup logout');
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      setToken('mock-token');
      localStorage.setItem('token', 'mock-token');
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
      console.log('🔧 Enabling mockup mode');
      setUser(MOCK_USER);
      setIsAuthenticated(true);
      setToken('mock-token');
      localStorage.setItem('token', 'mock-token');
    } else {
      // Disable mockup mode
      console.log('🔧 Disabling mockup mode');
      setUser(null);
      setIsAuthenticated(false);
      setToken(null);
      localStorage.removeItem('token');
    }
  };

  const updateUser = (updatedUserData) => {
    setUser(prevUser => ({ ...prevUser, ...updatedUserData }));
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
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};