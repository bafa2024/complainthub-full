import React, { createContext, useState, useContext, useEffect } from 'react';

// --- MOCKED AUTH CONTEXT FOR UI TESTING ---
export const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [loading, setLoading] = useState(false);

  // 2. We create a fake user object. Change the role here to test different portals.
  const [user, setUser] = useState({
    full_name: "Test User",
    email: "test@user.com",
    // To test the User Dashboard, change this line to "user"
    role: "user", 
  });

  // ... (the rest of the file remains the same)

  const login = async (email, password) => { console.log("Login function is disabled for UI testing."); return user; };
  const logout = () => { console.log("Logout function is disabled for UI testing."); };
  const signup = async (userData) => { console.log("Signup function is disabled for UI testing."); return { success: true }; };

  const value = { isAuthenticated, user, loading, login, logout, signup };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};