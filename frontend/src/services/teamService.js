import apiClient from './apiClient';

// Team Invitation Service
const teamService = {
  // Send team invitation
  sendInvitation: async (brandId, invitationData) => {
    try {
      const response = await apiClient.post(`/brands/${brandId}/invitations`, invitationData);
      return response.data;
    } catch (error) {
      console.error('Error sending team invitation:', error.message || error);
      throw error;
    }
  },

  // Get team invitations for a brand
  getInvitations: async (brandId) => {
    try {
      const response = await apiClient.get(`/brands/${brandId}/invitations`);
      return response.data;
    } catch (error) {
      console.error('Error fetching team invitations:', error.message || error);
      throw error;
    }
  },

  // Delete team invitation
  deleteInvitation: async (brandId, invitationId) => {
    try {
      const response = await apiClient.delete(`/brands/${brandId}/invitations/${invitationId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting team invitation:', error.message || error);
      throw error;
    }
  },

  // Get invitation details by token (public)
  getInvitationByToken: async (token) => {
    try {
      const response = await apiClient.get(`/brands/invitations/${token}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching invitation details:', error.message || error);
      throw error;
    }
  },

  // Accept team invitation (public)
  acceptInvitation: async (token, userData) => {
    try {
      const response = await apiClient.post(`/brands/invitations/${token}/accept`, userData);
      return response.data;
    } catch (error) {
      console.error('Error accepting team invitation:', error.message || error);
      throw error;
    }
  },

  // Get team members for a brand
  getTeamMembers: async (brandId) => {
    try {
      const response = await apiClient.get(`/brands/${brandId}/team-members`);
      return response.data;
    } catch (error) {
      console.error('Error fetching team members:', error.message || error);
      throw error;
    }
  }
};

export default teamService; 