// frontend/src/services/securityService.js

import apiClient from './apiClient';

class SecurityService {
  // Get security events
  async getSecurityEvents(params = {}) {
    try {
      const response = await apiClient.get('/security/events', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching security events:', error);
      throw error;
    }
  }

  // Get security report
  async getSecurityReport() {
    try {
      const response = await apiClient.get('/security/report');
      return response.data;
    } catch (error) {
      console.error('Error fetching security report:', error);
      throw error;
    }
  }

  // Get compliance status
  async getComplianceStatus() {
    try {
      const response = await apiClient.get('/security/compliance');
      return response.data;
    } catch (error) {
      console.error('Error fetching compliance status:', error);
      throw error;
    }
  }

  // Add IP to blacklist
  async addIPToBlacklist(ipAddress, reason) {
    try {
      const response = await apiClient.post('/security/blacklist/ip', {
        ip_address: ipAddress,
        reason: reason
      });
      return response.data;
    } catch (error) {
      console.error('Error adding IP to blacklist:', error);
      throw error;
    }
  }

  // Remove IP from blacklist
  async removeIPFromBlacklist(ipAddress) {
    try {
      const response = await apiClient.delete(`/security/blacklist/ip/${ipAddress}`);
      return response.data;
    } catch (error) {
      console.error('Error removing IP from blacklist:', error);
      throw error;
    }
  }

  // Get blacklisted IPs
  async getBlacklistedIPs() {
    try {
      const response = await apiClient.get('/security/blacklist');
      return response.data;
    } catch (error) {
      console.error('Error fetching blacklisted IPs:', error);
      throw error;
    }
  }

  // Reset rate limit
  async resetRateLimit(identifier) {
    try {
      const response = await apiClient.post('/security/rate-limit/reset', {
        identifier: identifier
      });
      return response.data;
    } catch (error) {
      console.error('Error resetting rate limit:', error);
      throw error;
    }
  }

  // Check SSL certificate
  async checkSSLCertificate(hostname, port = 443) {
    try {
      const response = await apiClient.post('/security/ssl/check', {
        hostname: hostname,
        port: port
      });
      return response.data;
    } catch (error) {
      console.error('Error checking SSL certificate:', error);
      throw error;
    }
  }

  // Update threat intelligence
  async updateThreatIntelligence() {
    try {
      const response = await apiClient.post('/security/threat-intelligence/update');
      return response.data;
    } catch (error) {
      console.error('Error updating threat intelligence:', error);
      throw error;
    }
  }

  // Get DDoS status
  async getDDoSStatus() {
    try {
      const response = await apiClient.get('/security/ddos/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching DDoS status:', error);
      throw error;
    }
  }

  // Update WAF rules
  async updateWAFRules(rules) {
    try {
      const response = await apiClient.post('/security/waf/rules', rules);
      return response.data;
    } catch (error) {
      console.error('Error updating WAF rules:', error);
      throw error;
    }
  }

  // Get WAF rules
  async getWAFRules() {
    try {
      const response = await apiClient.get('/security/waf/rules');
      return response.data;
    } catch (error) {
      console.error('Error fetching WAF rules:', error);
      throw error;
    }
  }

  // Record GDPR consent
  async recordGDPRConsent(userId, consentType, granted) {
    try {
      const response = await apiClient.post('/security/compliance/gdpr-consent', {
        user_id: userId,
        consent_type: consentType,
        granted: granted
      });
      return response.data;
    } catch (error) {
      console.error('Error recording GDPR consent:', error);
      throw error;
    }
  }

  // Get GDPR consent
  async getGDPRConsent(userId) {
    try {
      const response = await apiClient.get(`/security/compliance/gdpr-consent/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching GDPR consent:', error);
      throw error;
    }
  }

  // Log data access
  async logDataAccess(userId, dataType, action) {
    try {
      const response = await apiClient.post('/security/audit/data-access', {
        user_id: userId,
        data_type: dataType,
        action: action
      });
      return response.data;
    } catch (error) {
      console.error('Error logging data access:', error);
      throw error;
    }
  }

  // Get audit trail
  async getAuditTrail(params = {}) {
    try {
      const response = await apiClient.get('/security/audit/trail', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching audit trail:', error);
      throw error;
    }
  }

  // Password strength validation
  validatePasswordStrength(password) {
    const score = {
      length: password.length >= 12 ? 2 : password.length >= 8 ? 1 : 0,
      lowercase: /[a-z]/.test(password) ? 1 : 0,
      uppercase: /[A-Z]/.test(password) ? 1 : 0,
      numbers: /\d/.test(password) ? 1 : 0,
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password) ? 1 : 0,
      common: /(123|abc|qwe|password|admin)/.test(password.toLowerCase()) ? -2 : 0,
      repeated: /(.)\1{2,}/.test(password) ? -1 : 0
    };

    const totalScore = Math.max(0, Object.values(score).reduce((a, b) => a + b, 0));
    const strength = totalScore < 3 ? 'weak' : totalScore < 5 ? 'medium' : 'strong';

    const feedback = [];
    if (score.length === 0) feedback.push('Password must be at least 8 characters long (12+ recommended)');
    if (score.lowercase === 0) feedback.push('Password must contain lowercase letters');
    if (score.uppercase === 0) feedback.push('Password must contain uppercase letters');
    if (score.numbers === 0) feedback.push('Password must contain numbers');
    if (score.special === 0) feedback.push('Password must contain special characters');
    if (score.common < 0) feedback.push('Password contains common patterns');
    if (score.repeated < 0) feedback.push('Password contains repeated characters');

    return {
      score: totalScore,
      strength: strength,
      feedback: feedback,
      isValid: totalScore >= 4
    };
  }

  // Sanitize input
  sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    
    // Remove potentially dangerous characters
    return input
      .replace(/[<>]/g, '') // Remove < and >
      .replace(/javascript:/gi, '') // Remove javascript: protocol
      .replace(/on\w+\s*=/gi, '') // Remove event handlers
      .trim();
  }

  // Generate secure token
  generateSecureToken(length = 32) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }

  // Mask PII data
  maskPIIData(data, dataType = 'email') {
    if (!data) return data;

    switch (dataType) {
      case 'email':
        if (data.includes('@')) {
          const [username, domain] = data.split('@');
          return `${username.substring(0, 2)}***@${domain}`;
        }
        break;
      case 'phone':
        if (data.length >= 10) {
          return `${data.substring(0, 3)}***${data.substring(data.length - 4)}`;
        }
        break;
      case 'name':
        if (data.length > 2) {
          return `${data[0]}${'*'.repeat(data.length - 2)}${data[data.length - 1]}`;
        }
        break;
      case 'credit_card':
        if (data.length >= 13) {
          return `${data.substring(0, 4)}****${data.substring(data.length - 4)}`;
        }
        break;
      case 'ssn':
        if (data.length >= 9) {
          return `***-**-${data.substring(data.length - 4)}`;
        }
        break;
    }
    return data;
  }
}

export default new SecurityService(); 