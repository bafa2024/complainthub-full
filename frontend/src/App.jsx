import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
// This import line is now corrected to include AuthProvider
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/shared/Layout';

// Public Components
import HomePage from './components/public/HomePage';
import PublicComplaints from './components/public/PublicComplaints';
import UserLogin from './components/auth/UserLogin';
import UserSignup from './components/auth/UserSignup';
import BrandLogin from './components/auth/BrandLogin';
import AdminLogin from './components/auth/AdminLogin';
import BrandSignup from './components/auth/BrandSignup';

// User Components
import UserDashboard from './components/user/UserDashboard';
import TicketDetail from './components/user/TicketDetail';
import NewComplaint from './components/user/NewComplaint';
import ChatPage from './components/chat/ChatPage';


// Brand Components
import BrandDashboard from './components/brand/BrandDashboard';
import BrandTicketDetail from './components/brand/BrandTicketDetail';

// Admin Components
import AdminDashboard from './components/admin/AdminDashboard';
import AdminBrands from './components/admin/AdminBrands';
import AdminUsers from './components/admin/AdminUsers';

import './App.css';

// A wrapper for routes that require authentication and role checks
const ProtectedRoute = ({ children, roles }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    // You can return a loading spinner here if you have one
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (roles && !roles.includes(user?.role)) {
    return <Navigate to="/unauthorized" />;
  }

  return children;
};


function App() {
  return (
    // This AuthProvider will now be correctly recognized
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

            {/* User-specific Routes */}
            <Route path="/dashboard" element={<ProtectedRoute roles={['user']}><UserDashboard /></ProtectedRoute>} />
            <Route path="/tickets/:ticketId" element={<ProtectedRoute roles={['user', 'admin']}><TicketDetail /></ProtectedRoute>} />
            <Route path="/new-complaint" element={<ProtectedRoute roles={['user']}><NewComplaint /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute roles={['user']}><ChatPage /></ProtectedRoute>} />

            {/* Brand-specific Routes */}
            <Route path="/brand/dashboard" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandDashboard /></ProtectedRoute>} />
            <Route path="/brand/tickets/:ticketId" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandTicketDetail /></ProtectedRoute>} />

            {/* Admin-specific Routes */}
            <Route path="/admin/dashboard" element={<ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/brands" element={<ProtectedRoute roles={['admin']}><AdminBrands /></ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute roles={['admin']}><AdminUsers /></ProtectedRoute>} />

            {/* Fallback Routes */}
            <Route path="/unauthorized" element={<div><h1>403 - Not Authorized</h1></div>} />
            <Route path="*" element={<div><h1>404 - Page Not Found</h1></div>} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;