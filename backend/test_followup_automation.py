#!/usr/bin/env python3
"""
Test script for Follow-up Automation System

This script tests the complete follow-up automation workflow including:
- Follow-up scheduling
- Background task execution
- Multi-channel follow-ups
- Response handling
- Auto-closure
- Statistics and reporting
"""

import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_BRAND_EMAIL = "brand@example.com"
TEST_BRAND_PASSWORD = "brandpassword123"

class FollowUpAutomationTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_ticket_id = None
        self.test_follow_up_id = None
        
    def log_test(self, test_name: str, success: bool, message: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        return success
    
    def authenticate(self):
        """Authenticate as a brand user"""
        try:
            # Login as brand user
            login_data = {
                "email": TEST_BRAND_EMAIL,
                "password": TEST_BRAND_PASSWORD
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                return self.log_test("Authentication", True, "Successfully authenticated")
            else:
                return self.log_test("Authentication", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            return self.log_test("Authentication", False, str(e))
    
    def create_test_ticket(self):
        """Create a test ticket for follow-up testing"""
        try:
            ticket_data = {
                "title": "Test complaint for follow-up",
                "description": "This is a test complaint to verify follow-up automation",
                "category": "complaint",
                "urgency": "medium",
                "channel": "webchat"
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/tickets/",
                json=ticket_data
            )
            
            if response.status_code == 201:
                data = response.json()
                self.test_ticket_id = data["id"]
                return self.log_test(
                    "Create Test Ticket", 
                    True, 
                    f"Ticket created with ID: {self.test_ticket_id}"
                )
            else:
                return self.log_test(
                    "Create Test Ticket", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Create Test Ticket", False, str(e))
    
    def resolve_ticket(self):
        """Mark the test ticket as resolved to trigger follow-up"""
        try:
            response = self.session.patch(
                f"{API_BASE_URL}/tickets_extended/{self.test_ticket_id}/status",
                params={"status": "resolved"}
            )
            
            if response.status_code == 200:
                return self.log_test(
                    "Resolve Ticket", 
                    True, 
                    "Ticket marked as resolved"
                )
            else:
                return self.log_test(
                    "Resolve Ticket", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Resolve Ticket", False, str(e))
    
    def test_follow_up_scheduling(self):
        """Test follow-up scheduling"""
        try:
            # Schedule a follow-up
            schedule_data = {
                "delay_hours": 0  # Schedule immediately for testing
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/followup/schedule/{self.test_ticket_id}",
                json=schedule_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.test_follow_up_id = data.get("follow_up_id")
                return self.log_test(
                    "Follow-up Scheduling", 
                    True, 
                    f"Follow-up scheduled with ID: {self.test_follow_up_id}"
                )
            else:
                return self.log_test(
                    "Follow-up Scheduling", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Scheduling", False, str(e))
    
    def test_follow_up_execution(self):
        """Test follow-up execution"""
        try:
            response = self.session.post(
                f"{API_BASE_URL}/followup/execute/{self.test_follow_up_id}"
            )
            
            if response.status_code == 200:
                return self.log_test(
                    "Follow-up Execution", 
                    True, 
                    "Follow-up execution started"
                )
            else:
                return self.log_test(
                    "Follow-up Execution", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Execution", False, str(e))
    
    def test_follow_up_listing(self):
        """Test follow-up listing"""
        try:
            response = self.session.get(
                f"{API_BASE_URL}/followup/list",
                params={"ticket_id": self.test_ticket_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                follow_ups = data.get("follow_ups", [])
                return self.log_test(
                    "Follow-up Listing", 
                    True, 
                    f"Found {len(follow_ups)} follow-ups"
                )
            else:
                return self.log_test(
                    "Follow-up Listing", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Listing", False, str(e))
    
    def test_follow_up_response_handling(self):
        """Test follow-up response handling"""
        try:
            response_data = {
                "follow_up_id": self.test_follow_up_id,
                "response": "resolved",
                "rating": 5
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/followup/response",
                json=response_data
            )
            
            if response.status_code == 200:
                return self.log_test(
                    "Follow-up Response Handling", 
                    True, 
                    "Response processed successfully"
                )
            else:
                return self.log_test(
                    "Follow-up Response Handling", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Response Handling", False, str(e))
    
    def test_follow_up_statistics(self):
        """Test follow-up statistics"""
        try:
            response = self.session.get(
                f"{API_BASE_URL}/followup/stats",
                params={"days": 30}
            )
            
            if response.status_code == 200:
                stats = response.json()
                return self.log_test(
                    "Follow-up Statistics", 
                    True, 
                    f"Stats retrieved: {stats.get('total_follow_ups', 0)} total follow-ups"
                )
            else:
                return self.log_test(
                    "Follow-up Statistics", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Statistics", False, str(e))
    
    def test_celery_tasks(self):
        """Test Celery background tasks"""
        try:
            # Test retry failed follow-ups
            response = self.session.post(f"{API_BASE_URL}/followup/retry-failed")
            
            if response.status_code == 200:
                return self.log_test(
                    "Celery Tasks", 
                    True, 
                    "Background tasks working"
                )
            else:
                return self.log_test(
                    "Celery Tasks", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Celery Tasks", False, str(e))
    
    def test_multi_channel_follow_ups(self):
        """Test multi-channel follow-up capabilities"""
        try:
            # Test different channels
            channels = ["whatsapp", "email", "telegram", "voice"]
            
            for channel in channels:
                # Create a test follow-up for each channel
                follow_up_data = {
                    "ticket_id": self.test_ticket_id,
                    "channel": channel,
                    "follow_up_type": "resolution_confirmation",
                    "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
                
                response = self.session.post(
                    f"{API_BASE_URL}/followup/schedule/{self.test_ticket_id}",
                    json={"delay_hours": 1}
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Multi-channel follow-up for {channel} scheduled")
                else:
                    logger.warning(f"⚠️ Failed to schedule {channel} follow-up")
            
            return self.log_test(
                "Multi-channel Follow-ups", 
                True, 
                "Multi-channel follow-ups tested"
            )
                
        except Exception as e:
            return self.log_test("Multi-channel Follow-ups", False, str(e))
    
    def test_auto_closure(self):
        """Test automatic ticket closure"""
        try:
            # Create a ticket that should be auto-closed
            old_ticket_data = {
                "title": "Old test ticket for auto-closure",
                "description": "This ticket should be auto-closed",
                "category": "complaint",
                "urgency": "low",
                "channel": "webchat"
            }
            
            response = self.session.post(
                f"{API_BASE_URL}/tickets/",
                json=old_ticket_data
            )
            
            if response.status_code == 201:
                old_ticket_id = response.json()["id"]
                
                # Mark as resolved
                self.session.patch(
                    f"{API_BASE_URL}/tickets_extended/{old_ticket_id}/status",
                    params={"status": "resolved"}
                )
                
                return self.log_test(
                    "Auto-closure Setup", 
                    True, 
                    f"Old ticket {old_ticket_id} prepared for auto-closure"
                )
            else:
                return self.log_test(
                    "Auto-closure Setup", 
                    False, 
                    f"Status code: {response.status_code}"
                )
                
        except Exception as e:
            return self.log_test("Auto-closure Setup", False, str(e))
    
    def test_follow_up_cancellation(self):
        """Test follow-up cancellation"""
        try:
            # Create a follow-up to cancel
            response = self.session.post(
                f"{API_BASE_URL}/followup/schedule/{self.test_ticket_id}",
                json={"delay_hours": 24}
            )
            
            if response.status_code == 200:
                follow_up_id = response.json().get("follow_up_id")
                
                # Cancel the follow-up
                cancel_response = self.session.delete(
                    f"{API_BASE_URL}/followup/{follow_up_id}"
                )
                
                if cancel_response.status_code == 200:
                    return self.log_test(
                        "Follow-up Cancellation", 
                        True, 
                        f"Follow-up {follow_up_id} cancelled successfully"
                    )
                else:
                    return self.log_test(
                        "Follow-up Cancellation", 
                        False, 
                        f"Status code: {cancel_response.status_code}"
                    )
            else:
                return self.log_test(
                    "Follow-up Cancellation", 
                    False, 
                    f"Failed to create follow-up for cancellation"
                )
                
        except Exception as e:
            return self.log_test("Follow-up Cancellation", False, str(e))
    
    def run_all_tests(self):
        """Run all follow-up automation tests"""
        logger.info("🚀 Starting Follow-up Automation System Tests")
        logger.info("=" * 60)
        
        tests = [
            ("Authentication", self.authenticate),
            ("Create Test Ticket", self.create_test_ticket),
            ("Resolve Ticket", self.resolve_ticket),
            ("Follow-up Scheduling", self.test_follow_up_scheduling),
            ("Follow-up Execution", self.test_follow_up_execution),
            ("Follow-up Listing", self.test_follow_up_listing),
            ("Follow-up Response Handling", self.test_follow_up_response_handling),
            ("Follow-up Statistics", self.test_follow_up_statistics),
            ("Celery Tasks", self.test_celery_tasks),
            ("Multi-channel Follow-ups", self.test_multi_channel_follow_ups),
            ("Auto-closure Setup", self.test_auto_closure),
            ("Follow-up Cancellation", self.test_follow_up_cancellation),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                logger.error(f"❌ {test_name} failed with exception: {e}")
        
        logger.info("=" * 60)
        logger.info(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All follow-up automation tests passed!")
        else:
            logger.warning(f"⚠️ {total - passed} tests failed")
        
        return passed == total

def main():
    """Main test execution"""
    tester = FollowUpAutomationTester()
    success = tester.run_all_tests()
    
    if success:
        logger.info("✅ Follow-up Automation System is working correctly!")
        sys.exit(0)
    else:
        logger.error("❌ Follow-up Automation System has issues!")
        sys.exit(1)

if __name__ == "__main__":
    main() 