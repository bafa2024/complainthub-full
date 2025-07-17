import apiClient from './apiClient';

// Mock data for admin dashboard
const MOCK_USERS = [
  { id: 1, full_name: 'John Doe', email: 'john@example.com', role: 'user' },
  { id: 2, full_name: 'Jane Smith', email: 'jane@example.com', role: 'user' },
  { id: 3, full_name: 'Alice Brown', email: 'alice@example.com', role: 'user' },
  { id: 4, full_name: 'Bob Wilson', email: 'bob@example.com', role: 'user' },
  { id: 5, full_name: 'Carol Davis', email: 'carol@example.com', role: 'user' },
];

const MOCK_BRANDS = [
  { id: 1, name: 'Acme Corp', email: 'contact@acme.com', status: 'active' },
  { id: 2, name: 'ShopEasy', email: 'support@shopeasy.com', status: 'active' },
  { id: 3, name: 'GadgetPro', email: 'help@gadgetpro.com', status: 'active' },
];

const getAllUsers = async () => {
  try {
    const response = await apiClient.get('/admin/users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error.message || error);
    // Return mock data as fallback
    return MOCK_USERS;
  }
};

const createUser = async (userData) => {
  try {
    const response = await apiClient.post('/admin/users', userData);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error.message || error);
    throw error;
  }
};

const getUserById = async (userId) => {
  try {
    const response = await apiClient.get(`/admin/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user:', error.message || error);
    throw error;
  }
};

const updateUser = async (userId, userData) => {
  try {
    const response = await apiClient.put(`/admin/users/${userId}`, userData);
    return response.data;
  } catch (error) {
    console.error('Error updating user:', error.message || error);
    throw error;
  }
};

const deleteUser = async (userId) => {
  try {
    const response = await apiClient.delete(`/admin/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting user:', error.message || error);
    throw error;
  }
};

const getAllBrands = async () => {
  try {
    const response = await apiClient.get('/brands');
    return response.data;
  } catch (error) {
    console.error('Error fetching brands:', error.message || error);
    // Return mock data as fallback
    return MOCK_BRANDS;
  }
};

const getSystemStats = async () => {
  try {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching system stats:', error.message || error);
    // Return mock stats as fallback
    return {
      total_users: MOCK_USERS.length,
      total_brands: MOCK_BRANDS.length,
      total_tickets: 15,
      resolved_tickets: 8,
      resolution_rate: 53.3
    };
  }
};

const updateSystemSettings = async (settings) => {
  try {
    const response = await apiClient.put('/admin/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating system settings:', error.message || error);
    throw error;
  }
};

const getAnalyticsOverview = async (dateRange = '30d') => {
  try {
    const response = await apiClient.get(`/analytics/overview?date_range=${dateRange}`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching analytics overview:', error.message || error);
    // Return mock data as fallback
    return {
      overview: {
        total_users: 2847,
        total_brands: 156,
        total_tickets: 1247,
        active_tickets: 58,
        resolved_tickets: 1189,
        resolution_rate: 95.3,
        avg_resolution_time: 2.3,
        avg_satisfaction: 4.2,
        total_revenue: 45600
      },
      status_breakdown: {
        new: 13,
        'in-progress': 45,
        resolved: 1189,
        closed: 0
      },
      channel_distribution: {
        whatsapp: 456,
        telegram: 234,
        webchat: 345,
        voice: 156,
        email: 56
      },
      category_distribution: {
        'Technical Issues': 456,
        'Billing': 234,
        'Service Quality': 198,
        'Product Issues': 156,
        'Other': 203
      },
      sentiment_metrics: {
        avg_sentiment: 3.8,
        sentiment_distribution: {
          positive: 789,
          neutral: 234,
          negative: 224
        },
        avg_satisfaction: 4.2
      },
      revenue_metrics: {
        total_revenue: 45600,
        monthly_revenue: 45600,
        revenue_growth: 15,
        top_revenue_brands: []
      },
      trends: {
        daily_tickets: [
          { date: '2024-01-01', count: 45 },
          { date: '2024-01-02', count: 52 },
          { date: '2024-01-03', count: 38 },
          { date: '2024-01-04', count: 67 },
          { date: '2024-01-05', count: 41 },
          { date: '2024-01-06', count: 29 },
          { date: '2024-01-07', count: 58 }
        ],
        growth_rate: 12.5
      }
    };
  }
};

const getRealTimeMetrics = async () => {
  try {
    const response = await apiClient.get('/analytics/realtime');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching real-time metrics:', error.message || error);
    // Return mock data as fallback
    return {
      today_tickets: 67,
      last_hour_tickets: 8,
      active_conversations: 23,
      pending_tickets: 45,
      recent_activity: [
        {
          ticket_id: 1247,
          title: "Payment processing issue",
          status: "new",
          brand_id: 1,
          created_at: new Date().toISOString(),
          channel: "whatsapp"
        },
        {
          ticket_id: 1246,
          title: "App login problem",
          status: "in-progress",
          brand_id: 2,
          created_at: new Date(Date.now() - 300000).toISOString(),
          channel: "webchat"
        },
        {
          ticket_id: 1245,
          title: "Order delivery delay",
          status: "resolved",
          brand_id: 3,
          created_at: new Date(Date.now() - 600000).toISOString(),
          channel: "telegram"
        }
      ],
      system_health: {
        status: "healthy",
        recent_activity: 67,
        error_rate: 0.02,
        avg_response_time: 245
      }
    };
  }
};

const generateReport = async (reportType, filters = {}) => {
  try {
    const response = await apiClient.post(`/analytics/reports/${reportType}`, filters);
    return response.data.data;
  } catch (error) {
    console.error('Error generating report:', error.message || error);
    // Return mock report data
    return {
      report_type: reportType,
      generated_at: new Date().toISOString(),
      data: {
        summary: "Report generated successfully",
        metrics: "Mock metrics data"
      }
    };
  }
};

const getPredictiveAnalytics = async (metric, days = 30) => {
  try {
    const response = await apiClient.get(`/analytics/predictive/${metric}?days=${days}`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching predictive analytics:', error.message || error);
    // Return mock prediction data
    return {
      predictions: Array.from({ length: days }, (_, i) => ({
        date: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        predicted_volume: Math.floor(Math.random() * 20) + 30
      })),
      confidence: 0.75,
      method: "linear_regression"
    };
  }
};

const getTrends = async (dateRange = '30d', metric = 'tickets') => {
  try {
    const response = await apiClient.get(`/analytics/trends?date_range=${dateRange}&metric=${metric}`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching trends:', error.message || error);
    // Return mock trends data
    return {
      daily_tickets: [
        { date: '2024-01-01', count: 45 },
        { date: '2024-01-02', count: 52 },
        { date: '2024-01-03', count: 38 },
        { date: '2024-01-04', count: 67 },
        { date: '2024-01-05', count: 41 },
        { date: '2024-01-06', count: 29 },
        { date: '2024-01-07', count: 58 }
      ],
      growth_rate: 12.5
    };
  }
};

const compareMetrics = async (metric, period1, period2, brandId = null) => {
  try {
    const params = new URLSearchParams({
      metric,
      period1,
      period2
    });
    if (brandId) params.append('brand_id', brandId);
    
    const response = await apiClient.get(`/analytics/comparison?${params}`);
    return response.data.data;
  } catch (error) {
    console.error('Error comparing metrics:', error.message || error);
    // Return mock comparison data
    return {
      metric,
      period1,
      period2,
      comparison: {
        period1_value: 100,
        period2_value: 115,
        change: 15,
        change_percent: 15,
        trend: "increasing"
      }
    };
  }
};

const exportReport = async (reportType, format = 'json', filters = {}) => {
  try {
    const params = new URLSearchParams({
      format,
      ...filters
    });
    
    const response = await apiClient.get(`/analytics/export/${reportType}?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error exporting report:', error.message || error);
    throw new Error('Failed to export report');
  }
};

const getDashboardData = async (dateRange = '30d') => {
  try {
    const response = await apiClient.get(`/analytics/dashboard?date_range=${dateRange}`);
    return response.data.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error.message || error);
    // Return mock dashboard data
    return {
      overview: await getAnalyticsOverview(dateRange),
      real_time: await getRealTimeMetrics(),
      brand_data: null,
      user_role: "admin",
      date_range: dateRange
    };
  }
};

const getAnalyticsHealth = async () => {
  try {
    const response = await apiClient.get('/analytics/health');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching analytics health:', error.message || error);
    // Return mock health data
    return {
      status: "healthy",
      recent_activity: 67,
      error_rate: 0.02,
      avg_response_time: 245
    };
  }
};

// Security Management Methods
const getSecurityOverview = async () => {
  try {
    const response = await apiClient.get('/security/overview');
    return response.data;
  } catch (error) {
    console.error('Error fetching security overview:', error.message || error);
    // Return mock data as fallback
    return {
      recent_events: 45,
      threats_last_7_days: 3,
      failed_login_attempts: 12,
      rate_limit_violations: 8,
      whitelisted_ips: 5,
      blacklisted_ips: 2,
      security_score: 85,
      event_distribution: {
        'USER_LOGIN': 25,
        'RATE_LIMIT_EXCEEDED': 8,
        'SUSPICIOUS_ACTIVITY': 3,
        'ADMIN_ACTION': 9
      }
    };
  }
};

const getSecurityEvents = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/security/events?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching security events:', error.message || error);
    // Return mock data as fallback
    return {
      events: [
        {
          id: 1,
          event_type: 'USER_LOGIN',
          message: 'User login successful',
          severity: 'low',
          timestamp: new Date().toISOString(),
          context: { user_id: 1, ip: '192.168.1.1' }
        },
        {
          id: 2,
          event_type: 'RATE_LIMIT_EXCEEDED',
          message: 'Rate limit exceeded for IP 192.168.1.100',
          severity: 'medium',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          context: { ip: '192.168.1.100' }
        }
      ],
      total: 2
    };
  }
};

const getThreatAnalysis = async (days = 7) => {
  try {
    const response = await apiClient.get(`/security/threats?days=${days}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching threat analysis:', error.message || error);
    // Return mock data as fallback
    return {
      total_threats: 3,
      threats_by_type: {
        'THREAT_DETECTED': 1,
        'SUSPICIOUS_ACTIVITY': 2
      },
      threats_by_hour: {
        10: 1,
        14: 1,
        22: 1
      },
      top_threatening_ips: [
        { ip: '192.168.1.100', count: 2 },
        { ip: '10.0.0.50', count: 1 }
      ],
      period_days: days
    };
  }
};

const getAuditTrail = async (filters = {}) => {
  try {
    const params = new URLSearchParams(filters);
    const response = await apiClient.get(`/security/audit-trail?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching audit trail:', error.message || error);
    // Return mock data as fallback
    return {
      audit_trail: [
        {
          id: 1,
          event_type: 'USER_LOGIN',
          message: 'User login successful',
          timestamp: new Date().toISOString(),
          user_id: 1,
          ip: '192.168.1.1',
          details: { user_agent: 'Mozilla/5.0...' }
        }
      ],
      total: 1
    };
  }
};

const getRateLimitStatus = async () => {
  try {
    const response = await apiClient.get('/security/rate-limits');
    return response.data;
  } catch (error) {
    console.error('Error fetching rate limit status:', error.message || error);
    // Return mock data as fallback
    return {
      statistics: {
        total_requests: 1250,
        violations: 8,
        blocked_ips: 2
      },
      configuration: {
        default_window: 60,
        default_max_requests: 100,
        admin_window: 60,
        admin_max_requests: 1000
      },
      current_limits: {
        default_window: 60,
        default_max_requests: 100,
        admin_window: 60,
        admin_max_requests: 1000
      }
    };
  }
};

const manageIpWhitelist = async (action, ip, reason = '') => {
  try {
    const response = await apiClient.post('/security/ip-whitelist', {
      action,
      ip_address: ip,
      reason
    });
    return response.data;
  } catch (error) {
    console.error('Error managing IP whitelist:', error.message || error);
    throw error;
  }
};

const manageIpBlacklist = async (action, ip, reason = '') => {
  try {
    const response = await apiClient.post('/security/ip-blacklist', {
      action,
      ip_address: ip,
      reason
    });
    return response.data;
  } catch (error) {
    console.error('Error managing IP blacklist:', error.message || error);
    throw error;
  }
};

const enable2fa = async (userId) => {
  try {
    const response = await apiClient.post(`/security/2fa/enable/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error enabling 2FA:', error.message || error);
    throw error;
  }
};

const disable2fa = async (userId) => {
  try {
    const response = await apiClient.post(`/security/2fa/disable/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error disabling 2FA:', error.message || error);
    throw error;
  }
};

// GDPR Compliance Methods
const getDataInventory = async () => {
  try {
    const response = await apiClient.get('/compliance/gdpr/data-inventory');
    return response.data;
  } catch (error) {
    console.error('Error fetching data inventory:', error.message || error);
    // Return mock data as fallback
    return {
      summary: {
        total_users: 2847,
        total_brands: 156,
        total_tickets: 1247,
        total_messages: 5678,
        total_admins: 5
      },
      data_by_age: {
        users: {
          total: 2847,
          active: 2456,
          inactive: 391,
          created_last_30_days: 234,
          created_last_90_days: 567
        },
        tickets: {
          total: 1247,
          open: 58,
          closed: 1189,
          created_last_30_days: 234
        },
        messages: {
          total: 5678,
          created_last_30_days: 1234
        }
      },
      retention_status: {
        data_eligible_for_deletion: 45,
        data_requiring_review: 12,
        data_compliant: 9765
      }
    };
  }
};

const getRetentionPolicy = async () => {
  try {
    const response = await apiClient.get('/compliance/gdpr/retention-policy');
    return response.data;
  } catch (error) {
    console.error('Error fetching retention policy:', error.message || error);
    // Return mock data as fallback
    return {
      user_data: {
        retention_period: "7 years",
        reason: "Legal compliance and audit requirements",
        auto_deletion: true,
        deletion_trigger: "Account inactivity for 7 years"
      },
      ticket_data: {
        retention_period: "5 years",
        reason: "Customer service history and legal requirements",
        auto_deletion: true,
        deletion_trigger: "Ticket resolution + 5 years"
      },
      message_data: {
        retention_period: "3 years",
        reason: "Communication history and service quality",
        auto_deletion: true,
        deletion_trigger: "Message creation + 3 years"
      },
      audit_logs: {
        retention_period: "10 years",
        reason: "Security and compliance requirements",
        auto_deletion: false,
        deletion_trigger: "Manual review only"
      },
      billing_data: {
        retention_period: "7 years",
        reason: "Tax and financial compliance",
        auto_deletion: false,
        deletion_trigger: "Manual review only"
      }
    };
  }
};

const exportUserData = async (userId) => {
  try {
    const response = await apiClient.get(`/compliance/gdpr/export/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error exporting user data:', error.message || error);
    throw error;
  }
};

const deleteUserData = async (userId) => {
  try {
    const response = await apiClient.delete(`/compliance/gdpr/delete/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting user data:', error.message || error);
    throw error;
  }
};

const reportDataBreach = async (breachData) => {
  try {
    const response = await apiClient.post('/compliance/gdpr/breach-notification', breachData);
    return response.data;
  } catch (error) {
    console.error('Error reporting data breach:', error.message || error);
    throw error;
  }
};

const getBreachHistory = async () => {
  try {
    const response = await apiClient.get('/compliance/gdpr/breach-history');
    return response.data;
  } catch (error) {
    console.error('Error fetching breach history:', error.message || error);
    // Return mock data as fallback
    return {
      breaches: [
        {
          id: 1,
          breach_id: 'breach_20240101_120000',
          timestamp: new Date().toISOString(),
          description: 'Test data breach for security testing',
          affected_users: 5,
          breach_date: new Date(Date.now() - 86400000).toISOString(),
          discovery_date: new Date().toISOString(),
          reported_by: 1
        }
      ],
      total_count: 1
    };
  }
};

// System Settings
const getSystemSettings = async () => {
  try {
    const response = await apiClient.get('/admin/settings');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching system settings:', error.message || error);
    // Return default settings as fallback
    return {
      openAiKey: '',
      twilioSid: '',
      twilioToken: '',
      deepgramKey: '',
      stripeSecretKey: '',
      stripePublishableKey: '',
      feeAmount: '50',
      resolutionWindow: '24',
      maxTicketsPerUser: '10',
      autoCloseDays: '7',
      satisfactionThreshold: '3.5',
      systemName: 'ComplaintHub Bot',
      systemEmail: 'admin@complainthub.com',
      timezone: 'Asia/Kolkata',
      maintenanceMode: false,
      debugMode: false,
      sessionTimeout: '8',
      maxLoginAttempts: '5',
      passwordMinLength: '8',
      requireTwoFactor: false,
      allowedDomains: '',
      emailNotifications: true,
      smsNotifications: true,
      pushNotifications: true,
      notificationFrequency: 'immediate',
      enableWhatsApp: true,
      enableTelegram: true,
      enableVoice: true,
      enableEmail: true,
      enableAnalytics: true,
      dataRetentionDays: '365',
      enableTracking: true,
      autoBackup: true,
      backupFrequency: 'daily',
      backupRetention: '30'
    };
  }
};

const testConnection = async (service) => {
  try {
    const response = await apiClient.post(`/admin/test-connection/${service}`);
    return response.data;
  } catch (error) {
    console.error(`Error testing ${service} connection:`, error.message || error);
    throw error;
  }
};

const restartSystem = async () => {
  try {
    const response = await apiClient.post('/admin/restart-system');
    return response.data;
  } catch (error) {
    console.error('Error restarting system:', error.message || error);
    throw error;
  }
};

// Reports
const getComplaintsReport = async (filters) => {
  try {
    const response = await apiClient.get('/admin/reports/complaints', { params: filters });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching complaints report:', error.message || error);
    // Return mock data as fallback
    return {
      byStatus: [
        { status: 'Resolved', count: 1189, percentage: 95.3 },
        { status: 'In Progress', count: 45, percentage: 3.6 },
        { status: 'Pending', count: 13, percentage: 1.1 }
      ],
      byCategory: [
        { category: 'Technical Issues', count: 456, percentage: 36.6 },
        { category: 'Billing', count: 234, percentage: 18.8 },
        { category: 'Service Quality', count: 198, percentage: 15.9 },
        { category: 'Product Issues', count: 156, percentage: 12.5 },
        { category: 'Other', count: 203, percentage: 16.2 }
      ],
      byBrand: [
        { brand: 'TechCorp Solutions', count: 89, avgResolution: '1.8h', resolutionRate: 98.5, satisfactionScore: 4.5 },
        { brand: 'Global Retail', count: 67, avgResolution: '2.1h', resolutionRate: 96.2, satisfactionScore: 4.3 },
        { brand: 'Digital Services', count: 54, avgResolution: '2.5h', resolutionRate: 94.8, satisfactionScore: 4.2 },
        { brand: 'Mobile Telecom', count: 43, avgResolution: '3.2h', resolutionRate: 92.1, satisfactionScore: 4.0 },
        { brand: 'Cloud Computing', count: 38, avgResolution: '1.9h', resolutionRate: 97.3, satisfactionScore: 4.4 }
      ]
    };
  }
};

const getBrandsReport = async (filters) => {
  try {
    const response = await apiClient.get('/admin/reports/brands', { params: filters });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching brands report:', error.message || error);
    // Return mock data as fallback
    return [
      {
        name: 'TechCorp Solutions',
        industry: 'Technology',
        totalComplaints: 89,
        resolved: 87,
        resolutionRate: 98.5,
        avgResponseTime: 1.8,
        satisfactionScore: 4.5,
        revenue: 8500
      },
      {
        name: 'Global Retail',
        industry: 'Retail',
        totalComplaints: 67,
        resolved: 64,
        resolutionRate: 96.2,
        avgResponseTime: 2.1,
        satisfactionScore: 4.3,
        revenue: 7200
      },
      {
        name: 'Digital Services',
        industry: 'Services',
        totalComplaints: 54,
        resolved: 51,
        resolutionRate: 94.8,
        avgResponseTime: 2.5,
        satisfactionScore: 4.2,
        revenue: 6800
      }
    ];
  }
};

const getUsersReport = async (filters) => {
  try {
    const response = await apiClient.get('/admin/reports/users', { params: filters });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching users report:', error.message || error);
    // Return mock data as fallback
    return {
      totalUsers: 2847,
      newUsers: 156,
      activeUsers: 892,
      avgComplaintsPerUser: 2.3,
      mostActiveUsers: 150,
      userSatisfaction: 4.2
    };
  }
};

const getRevenueReport = async (filters) => {
  try {
    const response = await apiClient.get('/admin/reports/revenue', { params: filters });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching revenue report:', error.message || error);
    // Return mock data as fallback
    return {
      totalRevenue: 45600,
      monthlyRevenue: 45600,
      growthRate: 15,
      topBrands: [
        { name: 'TechCorp Solutions', revenue: 8500 },
        { name: 'Global Retail', revenue: 7200 },
        { name: 'Digital Services', revenue: 6800 },
        { name: 'Mobile Telecom', revenue: 5500 },
        { name: 'Cloud Computing', revenue: 4800 }
      ]
    };
  }
};

<<<<<<< HEAD
const generateReport = async (reportType, format, filters) => {
  try {
    const response = await apiClient.post(`/admin/reports/generate/${reportType}`, filters, {
      params: { format },
      responseType: 'blob'
    });
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('Error generating report:', error.message || error);
    throw error;
  }
};

=======
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
// System Health and Activity
const getSystemHealth = async () => {
  try {
    const response = await apiClient.get('/admin/health');
    return response.data.data;
  } catch (error) {
    console.error('Error fetching system health:', error.message || error);
    // Return mock data as fallback
    return {
      status: 'healthy',
      uptime: '99.9%',
      error_rate: 0.001,
      avg_response_time: 150,
      database_status: 'connected',
      api_status: 'operational',
      last_check: new Date().toISOString()
    };
  }
};

const getRecentActivity = async (limit = 10) => {
  try {
    const response = await apiClient.get('/admin/activity', { params: { limit } });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching recent activity:', error.message || error);
    // Return mock data as fallback
    return [
      {
        type: 'ticket_created',
        title: 'New complaint submitted',
        time: '2 minutes ago',
        icon: 'fa-ticket-alt'
      },
      {
        type: 'user_registered',
        title: 'New user registered',
        time: '5 minutes ago',
        icon: 'fa-user-plus'
      },
      {
        type: 'ticket_resolved',
        title: 'Complaint resolved',
        time: '10 minutes ago',
        icon: 'fa-check-circle'
      },
      {
        type: 'brand_created',
        title: 'New brand added',
        time: '1 hour ago',
        icon: 'fa-building'
      },
      {
        type: 'system_backup',
        title: 'System backup completed',
        time: '2 hours ago',
        icon: 'fa-database'
      }
    ];
  }
};

const getTopBrands = async (limit = 10) => {
  try {
    const response = await apiClient.get('/admin/top-brands', { params: { limit } });
    return response.data.data;
  } catch (error) {
    console.error('Error fetching top brands:', error.message || error);
    // Return mock data as fallback
    return [
      {
        name: 'TechCorp Solutions',
        resolution_rate: 98.5,
        avg_response_time: 1.8,
        total_tickets: 89
      },
      {
        name: 'Global Retail',
        resolution_rate: 96.2,
        avg_response_time: 2.1,
        total_tickets: 67
      },
      {
        name: 'Digital Services',
        resolution_rate: 94.8,
        avg_response_time: 2.5,
        total_tickets: 54
      }
    ];
  }
};

// Backup Management
const createBackup = async () => {
  try {
    const response = await apiClient.post('/admin/backup');
    return response.data;
  } catch (error) {
    console.error('Error creating backup:', error.message || error);
    throw error;
  }
};

const listBackups = async () => {
  try {
    const response = await apiClient.get('/admin/backups');
    return response.data.data;
  } catch (error) {
    console.error('Error listing backups:', error.message || error);
    throw error;
  }
};

const restoreBackup = async (backupId) => {
  try {
    const response = await apiClient.post(`/admin/backup/${backupId}/restore`);
    return response.data;
  } catch (error) {
    console.error('Error restoring backup:', error.message || error);
    throw error;
  }
};

const deleteBackup = async (backupId) => {
  try {
    const response = await apiClient.delete(`/admin/backup/${backupId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting backup:', error.message || error);
    throw error;
  }
};

export default {
  getAllUsers,
  createUser,
  getUserById,
  updateUser,
  deleteUser,
  getAllBrands,
  getSystemStats,
  updateSystemSettings,
  getAnalyticsOverview,
  getRealTimeMetrics,
  generateReport,
  getPredictiveAnalytics,
  getTrends,
  compareMetrics,
  exportReport,
  getDashboardData,
  getAnalyticsHealth,
  // Security Management
  getSecurityOverview,
  getSecurityEvents,
  getThreatAnalysis,
  getAuditTrail,
  getRateLimitStatus,
  manageIpWhitelist,
  manageIpBlacklist,
  enable2fa,
  disable2fa,
  // GDPR Compliance
  getDataInventory,
  getRetentionPolicy,
  exportUserData,
  deleteUserData,
  reportDataBreach,
  getBreachHistory,
  // System Settings
  getSystemSettings,
  updateSystemSettings,
  testConnection,
  restartSystem,
  // Reports
  getComplaintsReport,
  getBrandsReport,
  getUsersReport,
  getRevenueReport,
<<<<<<< HEAD
  generateReport,
=======
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
  // System Health and Activity
  getSystemHealth,
  getRecentActivity,
  getTopBrands,
  // Backup Management
  createBackup,
  listBackups,
  restoreBackup,
  deleteBackup
};