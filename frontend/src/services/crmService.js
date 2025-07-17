// frontend/src/services/crmService.js

import apiClient from './apiClient';

class CRMService {
  // Get supported CRM systems
  async getSupportedCRMs() {
    try {
      const response = await apiClient.get('/crm/supported-crms');
      return response.data;
    } catch (error) {
      console.error('Error fetching supported CRMs:', error);
      throw error;
    }
  }

  // Get CRM integrations for a brand
  async getCRMIntegrations(brandId = null) {
    try {
      const params = brandId ? { brand_id: brandId } : {};
      const response = await apiClient.get('/crm/integrations', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching CRM integrations:', error);
      throw error;
    }
  }

  // Get specific CRM integration
  async getCRMIntegration(integrationId) {
    try {
      const response = await apiClient.get(`/crm/integrations/${integrationId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching CRM integration:', error);
      throw error;
    }
  }

  // Create new CRM integration
  async createCRMIntegration(integrationData) {
    try {
      const response = await apiClient.post('/crm/integrations', integrationData);
      return response.data;
    } catch (error) {
      console.error('Error creating CRM integration:', error);
      throw error;
    }
  }

  // Update CRM integration
  async updateCRMIntegration(integrationId, updateData) {
    try {
      const response = await apiClient.put(`/crm/integrations/${integrationId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Error updating CRM integration:', error);
      throw error;
    }
  }

  // Delete CRM integration
  async deleteCRMIntegration(integrationId) {
    try {
      const response = await apiClient.delete(`/crm/integrations/${integrationId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting CRM integration:', error);
      throw error;
    }
  }

  // Sync CRM integration
  async syncCRMIntegration(integrationId, syncDirection = 'bidirectional') {
    try {
      const response = await apiClient.post(`/crm/integrations/${integrationId}/sync`, {
        sync_direction: syncDirection
      });
      return response.data;
    } catch (error) {
      console.error('Error syncing CRM integration:', error);
      throw error;
    }
  }

  // Test CRM connection
  async testCRMConnection(crmType, apiKey, baseUrl) {
    try {
      const response = await apiClient.post('/crm/test-connection', {
        crm_type: crmType,
        api_key: apiKey,
        base_url: baseUrl
      });
      return response.data;
    } catch (error) {
      console.error('Error testing CRM connection:', error);
      throw error;
    }
  }

  // Get CRM sync status
  async getCRMSyncStatus(integrationId) {
    try {
      const response = await apiClient.get(`/crm/integrations/${integrationId}/sync-status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching CRM sync status:', error);
      throw error;
    }
  }

  // Get CRM webhook URL
  getCRMWebhookURL(crmType, integrationId) {
    const baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    return `${baseUrl}/api/v1/crm/webhook/${crmType}?integration_id=${integrationId}`;
  }

  // Get CRM field mappings
  async getCRMFieldMappings(crmType) {
    try {
      const response = await apiClient.get(`/crm/field-mappings/${crmType}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching CRM field mappings:', error);
      throw error;
    }
  }

  // Update CRM field mappings
  async updateCRMFieldMappings(crmType, mappings) {
    try {
      const response = await apiClient.put(`/crm/field-mappings/${crmType}`, mappings);
      return response.data;
    } catch (error) {
      console.error('Error updating CRM field mappings:', error);
      throw error;
    }
  }
}

export default new CRMService(); 