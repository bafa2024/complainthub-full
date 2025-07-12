import apiClient from './apiClient';

class UserService {
  // Profile Management
  async getProfile() {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  }

  async updateProfile(profileData) {
    try {
      const response = await apiClient.put('/users/me', profileData);
      return response.data;
    } catch (error) {
      console.error('Error updating profile:', error);
      throw error;
    }
  }

  async changePassword(passwordData) {
    try {
      const response = await apiClient.put('/users/me/password', passwordData);
      return response.data;
    } catch (error) {
      console.error('Error changing password:', error);
      throw error;
    }
  }

  // Notification Preferences
  async updateNotificationPreferences(preferences) {
    try {
      const response = await apiClient.put('/users/me/notifications', preferences);
      return response.data;
    } catch (error) {
      console.error('Error updating notification preferences:', error);
      throw error;
    }
  }

  // Privacy Settings
  async updatePrivacySettings(privacy) {
    try {
      const response = await apiClient.put('/users/me/privacy', privacy);
      return response.data;
    } catch (error) {
      console.error('Error updating privacy settings:', error);
      throw error;
    }
  }

  // Complaint History
  async getComplaintHistory(params = {}) {
    try {
      const response = await apiClient.get('/users/me/complaints', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching complaint history:', error);
      throw error;
    }
  }

  async getComplaintStats() {
    try {
      const response = await apiClient.get('/users/me/complaints/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching complaint stats:', error);
      throw error;
    }
  }

  // Sessions Management
  async getActiveSessions() {
    try {
      const response = await apiClient.get('/users/me/sessions');
      return response.data;
    } catch (error) {
      console.error('Error fetching active sessions:', error);
      throw error;
    }
  }

  async logoutAllSessions() {
    try {
      const response = await apiClient.post('/users/me/logout-all');
      return response.data;
    } catch (error) {
      console.error('Error logging out all sessions:', error);
      throw error;
    }
  }

  // Data Export
  async exportUserData() {
    try {
      const response = await apiClient.get('/users/me/export', {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting user data:', error);
      throw error;
    }
  }

  // Account Management
  async deleteAccount() {
    try {
      const response = await apiClient.delete('/users/me');
      return response.data;
    } catch (error) {
      console.error('Error deleting account:', error);
      throw error;
    }
  }

  // Activity History
  async getActivityHistory(days = 30) {
    try {
      const response = await apiClient.get('/users/me/activity', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching activity history:', error);
      throw error;
    }
  }

  // Avatar Upload
  async uploadAvatar(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/users/me/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading avatar:', error);
      throw error;
    }
  }

  // Ticket Timeline
  async getTicketTimeline(ticketId) {
    try {
      const response = await apiClient.get(`/tickets/${ticketId}/timeline`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket timeline:', error);
      throw error;
    }
  }

  // Advanced Ticket Filtering
  async filterTickets(filters = {}) {
    try {
      const response = await apiClient.get('/tickets/filter/advanced', {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('Error filtering tickets:', error);
      throw error;
    }
  }

  // Ticket Statistics
  async getTicketStats() {
    try {
      const response = await apiClient.get('/tickets/stats/summary');
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket stats:', error);
      throw error;
    }
  }

  // Public Complaints
  async getPublicComplaints(filters = {}) {
    try {
      const response = await apiClient.get('/tickets/public', {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching public complaints:', error);
      throw error;
    }
  }

  // Mock data for development
  getMockComplaintHistory() {
    return [
      {
        id: 1,
        title: 'Defective smartphone received',
        brand: 'TechCorp',
        status: 'resolved',
        created_at: '2024-01-15T10:30:00Z',
        resolved_at: '2024-01-18T14:20:00Z'
      },
      {
        id: 2,
        title: 'Wrong order delivered',
        brand: 'FoodExpress',
        status: 'in-progress',
        created_at: '2024-01-16T09:15:00Z'
      },
      {
        id: 3,
        title: 'Poor customer service',
        brand: 'FashionHub',
        status: 'new',
        created_at: '2024-01-17T16:45:00Z'
      }
    ];
  }

  getMockActivityHistory() {
    return [
      {
        type: 'complaint_created',
        timestamp: '2024-01-17T16:45:00Z',
        title: 'Created complaint: Poor customer service',
        details: {
          complaint_id: 3,
          brand: 'FashionHub',
          status: 'new'
        }
      },
      {
        type: 'complaint_created',
        timestamp: '2024-01-16T09:15:00Z',
        title: 'Created complaint: Wrong order delivered',
        details: {
          complaint_id: 2,
          brand: 'FoodExpress',
          status: 'in-progress'
        }
      },
      {
        type: 'conversation_started',
        timestamp: '2024-01-15T14:20:00Z',
        title: 'Started conversation session',
        details: {
          session_id: 1,
          status: 'active'
        }
      }
    ];
  }
}

export default new UserService(); 