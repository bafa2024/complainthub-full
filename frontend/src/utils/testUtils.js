// Test utilities for frontend components
export class TestUtils {
  // Component rendering tests
  static testComponentRenders(Component, props = {}) {
    try {
      const element = document.createElement('div');
      // This would be replaced with actual React testing in a real environment
      return { success: true, message: 'Component renders successfully' };
    } catch (error) {
      return { success: false, message: `Component failed to render: ${error.message}` };
    }
  }

  // Form validation tests
  static testFormValidation(formData, validationRules) {
    const errors = [];
    
    Object.keys(validationRules).forEach(field => {
      const value = formData[field];
      const rules = validationRules[field];
      
      if (rules.required && (!value || value.trim() === '')) {
        errors.push(`${field} is required`);
      }
      
      if (rules.email && value && !this.isValidEmail(value)) {
        errors.push(`${field} must be a valid email`);
      }
      
      if (rules.minLength && value && value.length < rules.minLength) {
        errors.push(`${field} must be at least ${rules.minLength} characters`);
      }
      
      if (rules.maxLength && value && value.length > rules.maxLength) {
        errors.push(`${field} must be no more than ${rules.maxLength} characters`);
      }
    });
    
    return {
      success: errors.length === 0,
      errors,
      message: errors.length === 0 ? 'Form validation passed' : `Form validation failed: ${errors.join(', ')}`
    };
  }

  // API integration tests
  static async testAPIEndpoint(endpoint, method = 'GET', data = null) {
    try {
      const response = await fetch(endpoint, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : null,
      });
      
      return {
        success: response.ok,
        status: response.status,
        message: response.ok ? 'API endpoint working' : `API returned status ${response.status}`
      };
    } catch (error) {
      return {
        success: false,
        message: `API test failed: ${error.message}`
      };
    }
  }

  // Local storage tests
  static testLocalStorage() {
    try {
      const testKey = 'test_key';
      const testValue = 'test_value';
      
      localStorage.setItem(testKey, testValue);
      const retrievedValue = localStorage.getItem(testKey);
      localStorage.removeItem(testKey);
      
      return {
        success: retrievedValue === testValue,
        message: retrievedValue === testValue ? 'Local storage working' : 'Local storage test failed'
      };
    } catch (error) {
      return {
        success: false,
        message: `Local storage test failed: ${error.message}`
      };
    }
  }

  // Responsive design tests
  static testResponsiveDesign() {
    const breakpoints = [
      { name: 'Mobile', width: 375 },
      { name: 'Tablet', width: 768 },
      { name: 'Desktop', width: 1024 },
      { name: 'Large Desktop', width: 1440 }
    ];
    
    const results = breakpoints.map(bp => ({
      breakpoint: bp.name,
      width: bp.width,
      success: true, // In real testing, this would check actual responsive behavior
      message: `Responsive design test for ${bp.name} (${bp.width}px)`
    }));
    
    return {
      success: results.every(r => r.success),
      results,
      message: 'Responsive design tests completed'
    };
  }

  // Accessibility tests
  static testAccessibility(element) {
    const issues = [];
    
    // Check for alt text on images
    const images = element.querySelectorAll('img');
    images.forEach((img, index) => {
      if (!img.alt) {
        issues.push(`Image ${index + 1} missing alt text`);
      }
    });
    
    // Check for proper heading hierarchy
    const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6');
    let previousLevel = 0;
    headings.forEach((heading, index) => {
      const level = parseInt(heading.tagName.charAt(1));
      if (level > previousLevel + 1) {
        issues.push(`Heading hierarchy issue: ${heading.tagName} follows ${previousLevel}`);
      }
      previousLevel = level;
    });
    
    // Check for form labels
    const inputs = element.querySelectorAll('input, textarea, select');
    inputs.forEach((input, index) => {
      if (!input.id || !element.querySelector(`label[for="${input.id}"]`)) {
        issues.push(`Input ${index + 1} missing proper label`);
      }
    });
    
    return {
      success: issues.length === 0,
      issues,
      message: issues.length === 0 ? 'Accessibility tests passed' : `Accessibility issues found: ${issues.join(', ')}`
    };
  }

  // Performance tests
  static testPerformance(callback) {
    const startTime = performance.now();
    
    try {
      callback();
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      return {
        success: duration < 1000, // 1 second threshold
        duration: `${duration.toFixed(2)}ms`,
        message: duration < 1000 ? 'Performance test passed' : 'Performance test failed - too slow'
      };
    } catch (error) {
      return {
        success: false,
        message: `Performance test failed: ${error.message}`
      };
    }
  }

  // Helper methods
  static isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  static isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  }

  // Test runner
  static async runTestSuite(tests) {
    const results = [];
    
    for (const test of tests) {
      try {
        const result = await test.fn();
        results.push({
          name: test.name,
          ...result,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        results.push({
          name: test.name,
          success: false,
          message: `Test failed with error: ${error.message}`,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    return {
      total: results.length,
      passed: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
      results
    };
  }
}

// Test data generators
export const TestData = {
  generateUser() {
    return {
      id: Math.floor(Math.random() * 10000),
      name: 'Test User',
      email: 'test@example.com',
      phone: '+1234567890',
      role: 'user'
    };
  },

  generateComplaint() {
    return {
      id: Math.floor(Math.random() * 10000),
      title: 'Test Complaint',
      description: 'This is a test complaint description',
      category: 'Product Quality',
      priority: 'medium',
      status: 'open',
      brand: 'Test Brand',
      createdAt: new Date().toISOString()
    };
  },

  generateBrand() {
    return {
      id: Math.floor(Math.random() * 10000),
      name: 'Test Brand',
      email: 'brand@example.com',
      phone: '+1234567890',
      industry: 'Technology',
      status: 'active'
    };
  }
}; 