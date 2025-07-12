#!/usr/bin/env python3
"""
Comprehensive Security & Compliance Test Script
Tests all security and compliance features of the Brand Complaint Management System
"""

import requests
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityComplianceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.brand_token = None
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if details:
            logger.info(f"   Details: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_authentication(self):
        """Test authentication and authorization"""
        logger.info("\n🔐 Testing Authentication & Authorization")
        
        # Test admin login
        try:
            response = self.session.post(f"{self.base_url}/api/v1/login/admin", json={
                "email": "admin@example.com",
                "password": "admin123"
            })
            if response.status_code == 200:
                self.admin_token = response.json().get("access_token")
                self.log_test("Admin Login", True, f"Token: {self.admin_token[:20]}...")
            else:
                self.log_test("Admin Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Login", False, str(e))
        
        # Test user login
        try:
            response = self.session.post(f"{self.base_url}/api/v1/login/user", json={
                "email": "user@example.com",
                "password": "user123"
            })
            if response.status_code == 200:
                self.user_token = response.json().get("access_token")
                self.log_test("User Login", True, f"Token: {self.user_token[:20]}...")
            else:
                self.log_test("User Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("User Login", False, str(e))
        
        # Test brand login
        try:
            response = self.session.post(f"{self.base_url}/api/v1/login/brand", json={
                "email": "brand@example.com",
                "password": "brand123"
            })
            if response.status_code == 200:
                self.brand_token = response.json().get("access_token")
                self.log_test("Brand Login", True, f"Token: {self.brand_token[:20]}...")
            else:
                self.log_test("Brand Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Brand Login", False, str(e))
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        logger.info("\n🚦 Testing Rate Limiting")
        
        if not self.user_token:
            self.log_test("Rate Limiting", False, "No user token available")
            return
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Test normal requests
        try:
            for i in range(5):
                response = self.session.get(f"{self.base_url}/api/v1/users/me", headers=headers)
                if response.status_code == 200:
                    self.log_test(f"Rate Limit - Request {i+1}", True)
                else:
                    self.log_test(f"Rate Limit - Request {i+1}", False, f"Status: {response.status_code}")
                time.sleep(0.1)
        except Exception as e:
            self.log_test("Rate Limiting", False, str(e))
        
        # Test rate limit exceeded
        try:
            for i in range(150):  # Exceed rate limit
                response = self.session.get(f"{self.base_url}/api/v1/users/me", headers=headers)
                if response.status_code == 429:
                    self.log_test("Rate Limit Exceeded", True, f"Blocked after {i+1} requests")
                    break
                time.sleep(0.01)
            else:
                self.log_test("Rate Limit Exceeded", False, "Rate limit not enforced")
        except Exception as e:
            self.log_test("Rate Limit Exceeded", False, str(e))
    
    def test_ip_whitelisting(self):
        """Test IP whitelisting for admin routes"""
        logger.info("\n🛡️ Testing IP Whitelisting")
        
        if not self.admin_token:
            self.log_test("IP Whitelisting", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test admin route access
        try:
            response = self.session.get(f"{self.base_url}/api/v1/admin/users", headers=headers)
            if response.status_code == 200:
                self.log_test("Admin Route Access", True)
            elif response.status_code == 403:
                self.log_test("Admin Route Access", True, "IP not whitelisted (expected)")
            else:
                self.log_test("Admin Route Access", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Admin Route Access", False, str(e))
    
    def test_threat_detection(self):
        """Test threat detection mechanisms"""
        logger.info("\n🚨 Testing Threat Detection")
        
        # Test suspicious user agent
        try:
            headers = {"User-Agent": "sqlmap/1.0"}
            response = self.session.get(f"{self.base_url}/api/v1/users/me", headers=headers)
            if response.status_code == 403:
                self.log_test("Suspicious User Agent Detection", True)
            else:
                self.log_test("Suspicious User Agent Detection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Suspicious User Agent Detection", False, str(e))
        
        # Test suspicious path
        try:
            response = self.session.get(f"{self.base_url}/wp-admin")
            if response.status_code == 403:
                self.log_test("Suspicious Path Detection", True)
            else:
                self.log_test("Suspicious Path Detection", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Suspicious Path Detection", False, str(e))
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance features"""
        logger.info("\n📋 Testing GDPR Compliance")
        
        if not self.admin_token:
            self.log_test("GDPR Compliance", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test data export
        try:
            response = self.session.get(f"{self.base_url}/api/v1/compliance/gdpr/export/1", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "user_info" in data and "tickets" in data:
                    self.log_test("GDPR Data Export", True, f"Exported {len(data.get('tickets', []))} tickets")
                else:
                    self.log_test("GDPR Data Export", False, "Invalid export format")
            else:
                self.log_test("GDPR Data Export", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("GDPR Data Export", False, str(e))
        
        # Test retention policy
        try:
            response = self.session.get(f"{self.base_url}/api/v1/compliance/gdpr/retention-policy", headers=headers)
            if response.status_code == 200:
                policy = response.json()
                if "user_data" in policy and "ticket_data" in policy:
                    self.log_test("Retention Policy", True, f"Policy covers {len(policy)} data types")
                else:
                    self.log_test("Retention Policy", False, "Invalid policy format")
            else:
                self.log_test("Retention Policy", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Retention Policy", False, str(e))
        
        # Test data inventory
        try:
            response = self.session.get(f"{self.base_url}/api/v1/compliance/gdpr/data-inventory", headers=headers)
            if response.status_code == 200:
                inventory = response.json()
                if "summary" in inventory and "data_by_age" in inventory:
                    self.log_test("Data Inventory", True, f"Total users: {inventory['summary'].get('total_users', 0)}")
                else:
                    self.log_test("Data Inventory", False, "Invalid inventory format")
            else:
                self.log_test("Data Inventory", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Data Inventory", False, str(e))
    
    def test_security_management(self):
        """Test security management features"""
        logger.info("\n🔒 Testing Security Management")
        
        if not self.admin_token:
            self.log_test("Security Management", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test security overview
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/overview", headers=headers)
            if response.status_code == 200:
                overview = response.json()
                if "recent_events" in overview and "security_score" in overview:
                    self.log_test("Security Overview", True, f"Score: {overview.get('security_score', 0)}")
                else:
                    self.log_test("Security Overview", False, "Invalid overview format")
            else:
                self.log_test("Security Overview", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Security Overview", False, str(e))
        
        # Test security events
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/events", headers=headers)
            if response.status_code == 200:
                events = response.json()
                if "events" in events:
                    self.log_test("Security Events", True, f"Found {len(events['events'])} events")
                else:
                    self.log_test("Security Events", False, "Invalid events format")
            else:
                self.log_test("Security Events", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Security Events", False, str(e))
        
        # Test threat analysis
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/threats", headers=headers)
            if response.status_code == 200:
                threats = response.json()
                if "total_threats" in threats and "threats_by_type" in threats:
                    self.log_test("Threat Analysis", True, f"Total threats: {threats.get('total_threats', 0)}")
                else:
                    self.log_test("Threat Analysis", False, "Invalid threat analysis format")
            else:
                self.log_test("Threat Analysis", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Threat Analysis", False, str(e))
        
        # Test rate limit status
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/rate-limits", headers=headers)
            if response.status_code == 200:
                rate_limits = response.json()
                if "statistics" in rate_limits and "configuration" in rate_limits:
                    self.log_test("Rate Limit Status", True, "Configuration retrieved")
                else:
                    self.log_test("Rate Limit Status", False, "Invalid rate limit format")
            else:
                self.log_test("Rate Limit Status", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Rate Limit Status", False, str(e))
    
    def test_audit_trail(self):
        """Test audit trail functionality"""
        logger.info("\n📝 Testing Audit Trail")
        
        if not self.admin_token:
            self.log_test("Audit Trail", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test audit trail retrieval
        try:
            response = self.session.get(f"{self.base_url}/api/v1/security/audit-trail", headers=headers)
            if response.status_code == 200:
                audit = response.json()
                if "audit_trail" in audit:
                    self.log_test("Audit Trail", True, f"Found {len(audit['audit_trail'])} entries")
                else:
                    self.log_test("Audit Trail", False, "Invalid audit trail format")
            else:
                self.log_test("Audit Trail", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Audit Trail", False, str(e))
    
    def test_2fa_functionality(self):
        """Test two-factor authentication"""
        logger.info("\n🔐 Testing Two-Factor Authentication")
        
        if not self.admin_token:
            self.log_test("2FA", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 2FA enable
        try:
            response = self.session.post(f"{self.base_url}/api/v1/security/2fa/enable/1", headers=headers)
            if response.status_code == 200:
                result = response.json()
                if "secret" in result:
                    self.log_test("2FA Enable", True, f"Secret generated: {result['secret'][:10]}...")
                else:
                    self.log_test("2FA Enable", False, "No secret in response")
            else:
                self.log_test("2FA Enable", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("2FA Enable", False, str(e))
        
        # Test 2FA disable
        try:
            response = self.session.post(f"{self.base_url}/api/v1/security/2fa/disable/1", headers=headers)
            if response.status_code == 200:
                self.log_test("2FA Disable", True)
            else:
                self.log_test("2FA Disable", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("2FA Disable", False, str(e))
    
    def test_breach_notification(self):
        """Test data breach notification"""
        logger.info("\n🚨 Testing Data Breach Notification")
        
        if not self.admin_token:
            self.log_test("Breach Notification", False, "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test breach report
        try:
            breach_data = {
                "description": "Test data breach for security testing",
                "affected_users": 5,
                "breach_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "discovery_date": datetime.now().isoformat(),
                "severity": "medium"
            }
            response = self.session.post(f"{self.base_url}/api/v1/compliance/gdpr/breach-notification", 
                                       json=breach_data, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if "breach_id" in result:
                    self.log_test("Breach Notification", True, f"Breach ID: {result['breach_id']}")
                else:
                    self.log_test("Breach Notification", False, "No breach ID in response")
            else:
                self.log_test("Breach Notification", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Breach Notification", False, str(e))
        
        # Test breach history
        try:
            response = self.session.get(f"{self.base_url}/api/v1/compliance/gdpr/breach-history", headers=headers)
            if response.status_code == 200:
                history = response.json()
                if "breaches" in history:
                    self.log_test("Breach History", True, f"Found {len(history['breaches'])} breaches")
                else:
                    self.log_test("Breach History", False, "Invalid history format")
            else:
                self.log_test("Breach History", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Breach History", False, str(e))
    
    def test_encryption_and_masking(self):
        """Test data encryption and masking"""
        logger.info("\n🔐 Testing Encryption & Data Masking")
        
        # Test sensitive data masking
        try:
            from backend.app.core.security import mask_sensitive_data
            
            # Test email masking
            masked_email = mask_sensitive_data("user@example.com", "email")
            if "***" in masked_email and "@" in masked_email:
                self.log_test("Email Masking", True, f"Masked: {masked_email}")
            else:
                self.log_test("Email Masking", False, "Email not properly masked")
            
            # Test phone masking
            masked_phone = mask_sensitive_data("+1234567890", "phone")
            if "***" in masked_phone:
                self.log_test("Phone Masking", True, f"Masked: {masked_phone}")
            else:
                self.log_test("Phone Masking", False, "Phone not properly masked")
                
        except Exception as e:
            self.log_test("Data Masking", False, str(e))
    
    def test_password_policies(self):
        """Test password strength validation"""
        logger.info("\n🔑 Testing Password Policies")
        
        try:
            from backend.app.core.security import validate_password_strength
            
            # Test weak password
            weak_result = validate_password_strength("123")
            if not weak_result["is_valid"]:
                self.log_test("Weak Password Rejection", True, weak_result["message"])
            else:
                self.log_test("Weak Password Rejection", False, "Weak password accepted")
            
            # Test strong password
            strong_result = validate_password_strength("StrongPass123!")
            if strong_result["is_valid"]:
                self.log_test("Strong Password Acceptance", True, "Strong password accepted")
            else:
                self.log_test("Strong Password Acceptance", False, strong_result["message"])
                
        except Exception as e:
            self.log_test("Password Policies", False, str(e))
    
    def run_all_tests(self):
        """Run all security and compliance tests"""
        logger.info("🚀 Starting Security & Compliance Test Suite")
        logger.info("=" * 60)
        
        self.test_authentication()
        self.test_rate_limiting()
        self.test_ip_whitelisting()
        self.test_threat_detection()
        self.test_gdpr_compliance()
        self.test_security_management()
        self.test_audit_trail()
        self.test_2fa_functionality()
        self.test_breach_notification()
        self.test_encryption_and_masking()
        self.test_password_policies()
        
        # Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 SECURITY & COMPLIANCE TEST REPORT")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['details']}")
        
        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open("security_compliance_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"\n📄 Detailed report saved to: security_compliance_test_report.json")
        
        if failed_tests == 0:
            logger.info("🎉 All security and compliance tests passed!")
        else:
            logger.warning(f"⚠️  {failed_tests} tests failed. Please review the implementation.")

if __name__ == "__main__":
    # Create test instance
    tester = SecurityComplianceTester()
    
    # Run all tests
    tester.run_all_tests() 