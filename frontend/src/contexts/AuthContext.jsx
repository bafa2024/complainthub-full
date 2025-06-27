import React, { createContext, useState, useContext } from 'react';

export const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  // Always authenticated for demo
  const [isAuthenticated] = useState(true);
  const [loading] = useState(false);
  
  // Mock user - change role to test different dashboards
  // Options: "user", "brand_user", "admin"
  const [user] = useState({
    id: 1,
    full_name: "Demo User",
    email: "demo@example.com",
    role: localStorage.getItem('demoRole') || "user", // Read from localStorage
    brand_id: 1, // For brand_user role
  });

  // Mock functions
  const login = async (email, password) => {
    console.log("Mock login:", email);
    return user;
  };

  const logout = () => {
    console.log("Mock logout");
  };

  const signup = async (userData) => {
    console.log("Mock signup:", userData);
    return { ...user, ...userData };
  };

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    signup,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};