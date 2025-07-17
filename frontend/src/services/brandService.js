import apiClient from './apiClient';

const getBrands = async () => {
  try {
    // Use the admin endpoint for getting all brands
    const response = await apiClient.get('/admin/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error.message || error);
    throw error;
  }
};

const getPublicBrands = async () => {
  const response = await apiClient.get('/brands');
  return response.data;
};

const createBrand = async (brandData) => {
  try {
    // Use the admin endpoint for brand creation
    const response = await apiClient.post('/admin/brands', brandData);
    return response.data;
  } catch (error) {
    console.error('Error creating brand:', error);
    // Re-throw the error with more context
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to create brands. Please contact an administrator.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Invalid brand data. Please check your input.');
    } else if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.');
    } else {
      throw error;
    }
  }
};

const updateBrand = async (brandId, brandData) => {
  try {
    const response = await apiClient.put(`/brands/${brandId}`, brandData);
    return response.data;
  } catch (error) {
    console.error('Error updating brand:', error.message || error);
    throw error;
  }
};

const getBrandById = async (brandId) => {
  try {
    const response = await apiClient.get(`/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching brand:', error.message || error);
    throw error;
  }
};

const getCurrentUserBrand = async () => {
  try {
    // First get the current user to get their brand_id
    const userResponse = await apiClient.get('/auth/me');
    const user = userResponse.data;
    
    if (!user.brand_id) {
      throw new Error('User is not associated with any brand');
    }
    
    // Then get the brand details
    const brandResponse = await apiClient.get(`/brands/${user.brand_id}`);
    return brandResponse.data;
  } catch (error) {
    console.error('Error fetching current user brand:', error.message || error);
    throw error;
  }
};

const updateCurrentUserBrand = async (brandData) => {
  try {
    // First get the current user to get their brand_id
    const userResponse = await apiClient.get('/auth/me');
    const user = userResponse.data;
    
    if (!user.brand_id) {
      throw new Error('User is not associated with any brand');
    }
    
    // Then update the brand
    const response = await apiClient.put(`/brands/${user.brand_id}`, brandData);
    return response.data;
  } catch (error) {
    console.error('Error updating current user brand:', error.message || error);
    throw error;
  }
};

const deleteBrand = async (brandId) => {
  try {
    // Use the admin endpoint for brand deletion
    const response = await apiClient.delete(`/admin/brands/${brandId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting brand:', error);
    // Re-throw the error with more context
    if (error.response?.status === 403) {
      throw new Error('You do not have permission to delete brands. Please contact an administrator.');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Cannot delete brand. Please check for related data.');
    } else if (error.response?.status === 401) {
      throw new Error('Authentication required. Please log in again.');
    } else if (error.response?.status === 404) {
      throw new Error('Brand not found.');
    } else {
      throw error;
    }
  }
};

// Billing Methods
const getBillingSummary = async () => {
  try {
    const response = await apiClient.get('/billing/summary');
    return response.data;
  } catch (error) {
    console.error('Error fetching billing summary:', error.message || error);
    throw error;
  }
};

const getTransactionHistory = async (limit = 50, offset = 0) => {
  try {
    const response = await apiClient.get(`/billing/transactions?limit=${limit}&offset=${offset}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching transaction history:', error.message || error);
    throw error;
  }
};

const createCreditTopup = async (amount, paymentMethod = 'stripe') => {
  try {
    const response = await apiClient.post('/billing/topup', {
      amount,
      payment_method: paymentMethod
    });
    return response.data;
  } catch (error) {
    console.error('Error creating credit topup:', error.message || error);
    throw error;
  }
};

const confirmPayment = async (paymentIntentId) => {
  try {
    const response = await apiClient.post('/billing/confirm-payment', {
      payment_intent_id: paymentIntentId
    });
    return response.data;
  } catch (error) {
    console.error('Error confirming payment:', error.message || error);
    throw error;
  }
};

const createSubscription = async (planType, paymentMethodId) => {
  try {
    const response = await apiClient.post('/billing/subscription/create', {
      plan_type: planType,
      payment_method_id: paymentMethodId
    });
    return response.data;
  } catch (error) {
    console.error('Error creating subscription:', error.message || error);
    throw error;
  }
};

const getSubscriptionPlans = async () => {
  try {
    const response = await apiClient.get('/billing/plans');
    return response.data;
  } catch (error) {
    console.error('Error fetching subscription plans:', error.message || error);
    throw error;
  }
};

const getBillingAnalytics = async (dateRange = '30d') => {
  try {
    const response = await apiClient.get(`/billing/analytics?date_range=${dateRange}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching billing analytics:', error.message || error);
    throw error;
  }
};

const generateInvoice = async (transactionId) => {
  try {
    const response = await apiClient.get(`/billing/invoice/${transactionId}`);
    return response.data;
  } catch (error) {
    console.error('Error generating invoice:', error.message || error);
    throw error;
  }
};

const createRefund = async (transactionId, reason) => {
  try {
    const response = await apiClient.post(`/billing/refund/${transactionId}`, {
      reason
    });
    return response.data;
  } catch (error) {
    console.error('Error creating refund:', error.message || error);
    throw error;
  }
};

// AI Management Methods
async getAIStatus() {
    try {
        const response = await apiClient.get('/ai/status');
        return response.data;
    } catch (error) {
        console.error('Error getting AI status:', error);
        return {
            ai_engine_status: {
                openai_available: false,
                google_nlp_available: false,
                ml_models_loaded: false
            },
            training_status: {
                total_learning_data: 0,
                recent_learning_data: 0
            },
            conversation_stats: {
                active_conversations: 0,
                completed_conversations: 0
            }
        };
    }
},

async getBrandAIInsights() {
    try {
        const response = await apiClient.get(`/ai/brand/${this.brandId}/insights`);
        return response.data;
    } catch (error) {
        console.error('Error getting brand AI insights:', error);
        return {
            learning_insights: {},
            conversation_patterns: [],
            knowledge_base: { total_entries: 0 },
            recent_learning_data: 0
        };
    }
},

async getTrainingHistory(modelType = null, limit = 10) {
    try {
        const params = { limit };
        if (modelType) params.model_type = modelType;
        const response = await apiClient.get('/ai/training-history', { params });
        return response.data;
    } catch (error) {
        console.error('Error getting training history:', error);
        return [];
    }
},

async getBrandKnowledge(knowledgeType = null, language = null) {
    try {
        const params = {};
        if (knowledgeType) params.knowledge_type = knowledgeType;
        if (language) params.language = language;
        const response = await apiClient.get(`/ai/brand/${this.brandId}/knowledge`, { params });
        return response.data;
    } catch (error) {
        console.error('Error getting brand knowledge:', error);
        return [];
    }
},

async addBrandKnowledge(knowledgeData) {
    try {
        const response = await apiClient.post(`/ai/brand/${this.brandId}/knowledge`, knowledgeData);
        return response.data;
    } catch (error) {
        console.error('Error adding brand knowledge:', error);
        throw error;
    }
},

async getResponseTemplates(category = null, urgency = null, language = null) {
    try {
        const params = {};
        if (category) params.category = category;
        if (urgency) params.urgency = urgency;
        if (language) params.language = language;
        const response = await apiClient.get(`/ai/brand/${this.brandId}/templates`, { params });
        return response.data;
    } catch (error) {
        console.error('Error getting response templates:', error);
        return [];
    }
},

async addResponseTemplate(templateData) {
    try {
        const response = await apiClient.post(`/ai/brand/${this.brandId}/templates`, templateData);
        return response.data;
    } catch (error) {
        console.error('Error adding response template:', error);
        throw error;
    }
},

async getConversationPatterns() {
    try {
        const response = await apiClient.get(`/ai/brand/${this.brandId}/insights`);
        return response.data.conversation_patterns || [];
    } catch (error) {
        console.error('Error getting conversation patterns:', error);
        return [];
    }
},

async trainModels(brandId = null, force = false) {
    try {
        const params = { force };
        if (brandId) params.brand_id = brandId;
        const response = await apiClient.post('/ai/train', null, { params });
        return response.data;
    } catch (error) {
        console.error('Error training models:', error);
        throw error;
    }
},

async analyzeText(text, brandId = null) {
    try {
        const params = { text };
        if (brandId) params.brand_id = brandId;
        const response = await apiClient.post('/ai/analyze-text', null, { params });
        return response.data;
    } catch (error) {
        console.error('Error analyzing text:', error);
        throw error;
    }
},

async generateResponse(conversationData) {
    try {
        const response = await apiClient.post('/ai/generate-response', conversationData);
        return response.data;
    } catch (error) {
        console.error('Error generating response:', error);
        throw error;
    }
},

async getLearningData(brandId = null, days = 30, limit = 100) {
    try {
        const params = { days, limit };
        if (brandId) params.brand_id = brandId;
        const response = await apiClient.get('/ai/learning-data', { params });
        return response.data;
    } catch (error) {
        console.error('Error getting learning data:', error);
        return [];
    }
},

async retrainModels(brandId = null, force = false) {
    try {
        const params = { force };
        if (brandId) params.brand_id = brandId;
        const response = await apiClient.post('/ai/retrain', null, { params });
        return response.data;
    } catch (error) {
        console.error('Error retraining models:', error);
        throw error;
    }
}

// Phone Number Management Methods
const getPhoneNumbers = async () => {
  try {
    const response = await apiClient.get('/phone-numbers/brand');
    return response.data;
  } catch (error) {
    console.error('Error fetching phone numbers:', error.message || error);
    throw error;
  }
};

const getTelephonyProviders = async () => {
  try {
    const response = await apiClient.get('/phone-numbers/providers');
    return response.data;
  } catch (error) {
    console.error('Error fetching telephony providers:', error.message || error);
    throw error;
  }
};

const searchAvailableNumbers = async (searchParams) => {
  try {
    const params = new URLSearchParams();
    if (searchParams.country_code) params.append('country_code', searchParams.country_code);
    if (searchParams.number_type) params.append('number_type', searchParams.number_type);
    if (searchParams.capabilities) params.append('capabilities', searchParams.capabilities);
    if (searchParams.provider) params.append('provider', searchParams.provider);
    
    const response = await apiClient.get(`/phone-numbers/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error searching available numbers:', error.message || error);
    throw error;
  }
};

const purchasePhoneNumber = async (purchaseData) => {
  try {
    const response = await apiClient.post('/phone-numbers/purchase', purchaseData);
    return response.data;
  } catch (error) {
    console.error('Error purchasing phone number:', error.message || error);
    throw error;
  }
};

const updatePhoneNumberStatus = async (phoneNumber, updateData) => {
  try {
    const response = await apiClient.put(`/phone-numbers/${phoneNumber}/status`, updateData);
    return response.data;
  } catch (error) {
    console.error('Error updating phone number status:', error.message || error);
    throw error;
  }
};

const releasePhoneNumber = async (phoneNumber) => {
  try {
    const response = await apiClient.delete(`/phone-numbers/${phoneNumber}`);
    return response.data;
  } catch (error) {
    console.error('Error releasing phone number:', error.message || error);
    throw error;
  }
};

const getPhoneNumberRequests = async () => {
  try {
    const response = await apiClient.get('/phone-numbers/requests');
    return response.data;
  } catch (error) {
    console.error('Error fetching phone number requests:', error.message || error);
    throw error;
  }
};

const createPhoneNumberRequest = async (requestData) => {
  try {
    const response = await apiClient.post('/phone-numbers/requests', requestData);
    return response.data;
  } catch (error) {
    console.error('Error creating phone number request:', error.message || error);
    throw error;
  }
};

const getPhoneNumberAnalytics = async () => {
  try {
    const response = await apiClient.get('/phone-numbers/analytics');
    return response.data;
  } catch (error) {
    console.error('Error fetching phone number analytics:', error.message || error);
    throw error;
  }
};

export default {
  getBrands,
  getPublicBrands,
  createBrand,
  updateBrand,
  getBrandById,
  getCurrentUserBrand,
  updateCurrentUserBrand,
  deleteBrand,
  // Billing methods
  getBillingSummary,
  getTransactionHistory,
  createCreditTopup,
  confirmPayment,
  createSubscription,
  getSubscriptionPlans,
  getBillingAnalytics,
  generateInvoice,
  createRefund,
  // AI Management methods
  getAIStatus,
  getBrandAIInsights,
  getTrainingHistory,
  getBrandKnowledge,
  addBrandKnowledge,
  getResponseTemplates,
  addResponseTemplate,
  getConversationPatterns,
  trainModels,
  analyzeText,
  generateResponse,
  getLearningData,
  retrainModels,
  // Phone Number Management methods
  getPhoneNumbers,
  getTelephonyProviders,
  searchAvailableNumbers,
  purchasePhoneNumber,
  updatePhoneNumberStatus,
  releasePhoneNumber,
  getPhoneNumberRequests,
  createPhoneNumberRequest,
  getPhoneNumberAnalytics
};