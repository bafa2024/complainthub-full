// ==================================================================
// File: frontend/src/contexts/AuthContext.jsx
// This is the mocked version for UI testing without a backend.
// ==================================================================
import React, { createContext, useState, useContext } from 'react';

export const AuthContext = createContext(null);

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  // We immediately set isAuthenticated to true and loading to false.
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [loading, setLoading] = useState(false);

  // We create a fake user object. You can change the 'role' to test different portals.
  // Options: "user", "brand_user", "admin"
  const [user, setUser] = useState({
    full_name: "Test User",
    email: "test@user.com",
    role: "user", 
  });

  // Placeholder functions for the mocked context
  const login = async () => console.log("Login disabled for UI testing.");
  const logout = () => console.log("Logout disabled for UI testing.");
  const signup = async () => console.log("Signup disabled for UI testing.");

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


// ==================================================================
// File: frontend/src/App.jsx
// This file sets up all the application routing.
// ==================================================================
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/shared/Layout';

// Import all page components
import HomePage from './components/public/HomePage';
import PublicComplaints from './components/public/PublicComplaints';
import UserLogin from './components/auth/UserLogin';
import UserSignup from './components/auth/UserSignup';
import BrandLogin from './components/auth/BrandLogin';
import AdminLogin from './components/auth/AdminLogin';
import BrandSignup from './components/auth/BrandSignup';
import UserDashboard from './components/user/UserDashboard';
import TicketDetail from './components/user/TicketDetail';
import NewComplaint from './components/user/NewComplaint';
import ChatPage from './components/chat/ChatPage';
import BrandDashboard from './components/brand/BrandDashboard';
import BrandTicketDetail from './components/brand/BrandTicketDetail';
import AdminDashboard from './components/admin/AdminDashboard';
import AdminBrands from './components/admin/AdminBrands';
import AdminUsers from './components/admin/AdminUsers';

import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

// A robust wrapper for routes that require authentication
const ProtectedRoute = ({ children, roles }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Safely check the user role
  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<UserLogin />} />
            <Route path="/brand/login" element={<BrandLogin />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/signup" element={<UserSignup />} />
            <Route path="/brand/signup" element={<BrandSignup />} />
            <Route path="/complaints" element={<PublicComplaints />} />
            <Route path="/" element={<HomePage />} />

            {/* User Portal Routes */}
            <Route path="/dashboard" element={<ProtectedRoute roles={['user']}><UserDashboard /></ProtectedRoute>} />
            <Route path="/tickets/:ticketId" element={<ProtectedRoute roles={['user']}><TicketDetail /></ProtectedRoute>} />
            <Route path="/new-complaint" element={<ProtectedRoute roles={['user']}><NewComplaint /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute roles={['user']}><ChatPage /></ProtectedRoute>} />

            {/* Brand Portal Routes */}
            <Route path="/brand/dashboard" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandDashboard /></ProtectedRoute>} />
            <Route path="/brand/tickets/:ticketId" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandTicketDetail /></ProtectedRoute>} />

            {/* Admin Portal Routes */}
            <Route path="/admin/dashboard" element={<ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/brands" element={<ProtectedRoute roles={['admin']}><AdminBrands /></ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute roles={['admin']}><AdminUsers /></ProtectedRoute>} />

            {/* Fallback Routes */}
            <Route path="/unauthorized" element={<h1>403 - Not Authorized</h1>} />
            <Route path="*" element={<h1>404 - Page Not Found</h1>} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
