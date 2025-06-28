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
import LodgeVoicePage from './components/user/LodgeVoicePage'; // Import the new page
import BrandDashboard from './components/brand/BrandDashboard';
import BrandTicketDetail from './components/brand/BrandTicketDetail';
import AdminDashboard from './components/admin/AdminDashboard';
import AdminBrands from './components/admin/AdminBrands';
import AdminUsers from './components/admin/AdminUsers';
import AdminSettings from './components/admin/AdminSettings';
import AdminBillingLogs from './components/admin/AdminBillingLogs';

import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// A robust wrapper for routes that require authentication
const ProtectedRoute = ({ children, roles }) => {
  const { isAuthenticated, user, loading } = useAuth();
  if (loading) { return <div>Loading...</div>; }
  if (!isAuthenticated) { return <Navigate to="/login" replace />; }
  if (roles && !roles.includes(user?.role)) { return <Navigate to="/unauthorized" replace />; }
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/complaints" element={<PublicComplaints />} />
            <Route path="/login" element={<UserLogin />} />
            <Route path="/signup" element={<UserSignup />} />
            <Route path="/brand/login" element={<BrandLogin />} />
            <Route path="/brand/signup" element={<BrandSignup />} />
            <Route path="/admin/login" element={<AdminLogin />} />

            {/* User Portal Routes */}
            <Route path="/dashboard" element={<ProtectedRoute roles={['user']}><UserDashboard /></ProtectedRoute>} />
            <Route path="/lodge-voice" element={<ProtectedRoute roles={['user']}><LodgeVoicePage /></ProtectedRoute>} />
            <Route path="/new-complaint" element={<ProtectedRoute roles={['user']}><NewComplaint /></ProtectedRoute>} />
            <Route path="/chat" element={<ProtectedRoute roles={['user']}><ChatPage /></ProtectedRoute>} />
            <Route path="/tickets/:ticketId" element={<ProtectedRoute roles={['user']}><TicketDetail /></ProtectedRoute>} />

            {/* Brand Portal Routes */}
            <Route path="/brand/dashboard" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandDashboard /></ProtectedRoute>} />
            <Route path="/brand/tickets/:ticketId" element={<ProtectedRoute roles={['brand_user', 'admin']}><BrandTicketDetail /></ProtectedRoute>} />

            {/* Admin Portal Routes */}
            <Route path="/admin/dashboard" element={<ProtectedRoute roles={['admin']}><AdminDashboard /></ProtectedRoute>} />
            <Route path="/admin/brands" element={<ProtectedRoute roles={['admin']}><AdminBrands /></ProtectedRoute>} />
            <Route path="/admin/users" element={<ProtectedRoute roles={['admin']}><AdminUsers /></ProtectedRoute>} />
            <Route path="/admin/settings" element={<ProtectedRoute roles={['admin']}><AdminSettings /></ProtectedRoute>} />
            <Route path="/admin/billing" element={<ProtectedRoute roles={['admin']}><AdminBillingLogs /></ProtectedRoute>} />

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