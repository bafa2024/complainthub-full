import apiClient from './apiClient';

const ticketService = {
  // Get all tickets for the current user
  async getTickets() {
    try {
      const response = await apiClient.get('/api/v1/tickets/');
      return response.data;
    } catch (error) {
      console.error('Error fetching tickets:', error);
      throw error;
    }
  },

  // Get a specific ticket by ID
  async getTicketById(ticketId) {
    try {
      const response = await apiClient.get(`/api/v1/tickets/${ticketId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket:', error);
      throw error;
    }
  },

  // Create a new ticket
  async createTicket(ticketData) {
    try {
      const response = await apiClient.post('/api/v1/tickets/', ticketData);
      return response.data;
    } catch (error) {
      console.error('Error creating ticket:', error);
      throw error;
    }
  },

  // Update a ticket
  async updateTicket(ticketId, updateData) {
    try {
      const response = await apiClient.patch(`/api/v1/tickets/${ticketId}`, updateData);
      return response.data;
    } catch (error) {
      console.error('Error updating ticket:', error);
      throw error;
    }
  },

  // Auto-tag a ticket using AI
  async autoTagTicket(ticketId) {
    try {
      const response = await apiClient.post(`/api/v1/tickets/${ticketId}/auto-tag`);
      return response.data;
    } catch (error) {
      console.error('Error auto-tagging ticket:', error);
      throw error;
    }
  },

  // Get public tickets
  async getPublicTickets() {
    try {
      const response = await apiClient.get('/api/v1/tickets/public');
      return response.data;
    } catch (error) {
      console.error('Error fetching public tickets:', error);
      throw error;
    }
  },

  // Upload voice complaint
  async uploadVoiceComplaint(audioFile, metadata) {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('metadata', JSON.stringify(metadata));

      const response = await apiClient.post('/api/v1/tickets_extended/voice', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading voice complaint:', error);
      throw error;
    }
  },

  // Transcribe audio only
  async transcribeAudio(audioFile, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);

      const response = await apiClient.post('/api/v1/tickets_extended/voice/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error transcribing audio:', error);
      throw error;
    }
  },

  // Analyze voice sentiment
  async analyzeVoiceSentiment(audioFile, language = 'en') {
    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', language);

      const response = await apiClient.post('/api/v1/tickets_extended/voice/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing voice sentiment:', error);
      throw error;
    }
  },

  // Get ticket statistics
  async getTicketStats(brandId = null, dateRange = '30d') {
    try {
      const params = { date_range: dateRange };
      if (brandId) params.brand_id = brandId;
      
      const response = await apiClient.get('/api/v1/tickets/stats', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket stats:', error);
      throw error;
    }
  },

  // Get ticket analytics
  async getTicketAnalytics(brandId = null, filters = {}) {
    try {
      const params = { ...filters };
      if (brandId) params.brand_id = brandId;
      
      const response = await apiClient.get('/api/v1/tickets/analytics', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching ticket analytics:', error);
      throw error;
    }
  },

  // Export tickets
  async exportTickets(format = 'csv', filters = {}) {
    try {
      const params = { format, ...filters };
      const response = await apiClient.get('/api/v1/tickets/export', { 
        params,
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error('Error exporting tickets:', error);
      throw error;
    }
  },

  // Mock data for development/testing
  getMockTickets() {
    return [
      {
        id: 1,
        title: "Poor customer service experience",
        description: "I called customer service and was on hold for 45 minutes. When someone finally answered, they were rude and unhelpful.",
        status: "new",
        category: "complaint",
        urgency: "medium",
        severity_level: 2,
        abuse_level_flag: false,
        channel: "voice",
        satisfaction_rating: null,
        created_at: "2024-01-15T10:30:00Z",
        owner: {
          id: 1,
          full_name: "John Doe",
          email: "john@example.com"
        },
        brand: {
          id: 1,
          name: "TechCorp"
        },
        ai_analysis: {
          sentiment_score: -0.7,
          toxicity_score: 0.1,
          confidence: 0.85,
          language: "en"
        }
      },
      {
        id: 2,
        title: "Product quality issue",
        description: "The product I received is defective and doesn't work as advertised. Very disappointed with the quality.",
        status: "in-progress",
        category: "complaint",
        urgency: "high",
        severity_level: 3,
        abuse_level_flag: false,
        channel: "webchat",
        satisfaction_rating: null,
        created_at: "2024-01-14T15:45:00Z",
        owner: {
          id: 2,
          full_name: "Jane Smith",
          email: "jane@example.com"
        },
        brand: {
          id: 1,
          name: "TechCorp"
        },
        ai_analysis: {
          sentiment_score: -0.8,
          toxicity_score: 0.05,
          confidence: 0.92,
          language: "en"
        }
      },
      {
        id: 3,
        title: "Abusive language in complaint",
        description: "This is the worst service ever! You people are incompetent idiots! I want my money back NOW!",
        status: "new",
        category: "complaint",
        urgency: "high",
        severity_level: 5,
        abuse_level_flag: true,
        channel: "email",
        satisfaction_rating: null,
        created_at: "2024-01-13T09:15:00Z",
        owner: {
          id: 3,
          full_name: "Bob Johnson",
          email: "bob@example.com"
        },
        brand: {
          id: 2,
          name: "FoodExpress"
        },
        ai_analysis: {
          sentiment_score: -0.9,
          toxicity_score: 0.8,
          confidence: 0.95,
          language: "en"
        }
      }
    ];
  }
};

export default ticketService;