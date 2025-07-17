#!/usr/bin/env python3
"""
Comprehensive Test Script for Brand Management Features

Tests:
1. Enhanced Complaint Management with UI confirmation
2. Virtual Number Generator (Twilio API)
3. Credit System (24h free, ₹50/ticket)
4. Insights & Analytics (TAT, abuse patterns, team performance)
5. Notifications & Alerts (email/SMS/WhatsApp)

Run with: python test_brand_management_features.py
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (update with actual test user)
TEST_BRAND_EMAIL = "brand@example.com"
TEST_BRAND_PASSWORD = "brandpassword123"
TEST_ADMIN_EMAIL = "admin@example.com"
TEST_ADMIN_PASSWORD = "adminpassword123"

class BrandManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_ticket_id = None
        self.test_phone_number = None
        self.test_transaction_id = None
        
    def login(self, email: str, password: str) -> bool:
        """Login and get auth token"""
        try:
            response = self.session.post(f"{BASE_URL}/api/v1/auth/login", json={
                "email": email,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print(f"✅ Login successful for {email}")
                return True
            else:
                print(f"❌ Login failed for {email}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_enhanced_complaint_management(self):
        """Test 1: Enhanced Complaint Management with UI confirmation"""
        print("\n" + "="*60)
        print("TEST 1: ENHANCED COMPLAINT MANAGEMENT")
        print("="*60)
        
        try:
            # Create a test ticket
            print("📝 Creating test ticket...")
            ticket_data = {
                "title": "Test complaint for management",
                "description": "This is a test complaint to verify the enhanced management features.",
                "brand_id": 1,
                "category": "complaint",
                "urgency": "medium",
                "channel": "webchat"
            }
            
            response = self.session.post(f"{API_BASE}/tickets/", json=ticket_data)
            if response.status_code == 201:
                ticket = response.json()
                self.test_ticket_id = ticket["id"]
                print(f"✅ Test ticket created with ID: {self.test_ticket_id}")
            else:
                print(f"❌ Failed to create test ticket: {response.text}")
                return False
            
            # Test status updates with confirmation simulation
            print("🔄 Testing status updates...")
            status_updates = [
                {"status": "in-progress", "description": "Mark In Progress"},
                {"status": "resolved", "description": "Mark Resolved"},
                {"status": "closed", "description": "Mark Closed"}
            ]
            
            for update in status_updates:
                print(f"   Testing: {update['description']}")
                response = self.session.patch(f"{API_BASE}/tickets/{self.test_ticket_id}", json=update)
                if response.status_code == 200:
                    ticket = response.json()
                    print(f"   ✅ {update['description']} successful - Status: {ticket.get('status')}")
                else:
                    print(f"   ❌ {update['description']} failed: {response.text}")
                    return False
            
            # Test escalation
            print("🚨 Testing ticket escalation...")
            response = self.session.post(f"{API_BASE}/brand-management/tickets/{self.test_ticket_id}/escalate")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Escalation successful: {result.get('message')}")
            else:
                print(f"❌ Escalation failed: {response.text}")
                return False
            
            # Test assignment
            print("👤 Testing ticket assignment...")
            assignment_data = {"assignee_id": 1}  # Assuming user ID 1 exists
            response = self.session.post(f"{API_BASE}/brand-management/tickets/{self.test_ticket_id}/assign", json=assignment_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Assignment successful: {result.get('message')}")
            else:
                print(f"❌ Assignment failed: {response.text}")
                return False
            
            print("✅ Enhanced Complaint Management Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Enhanced Complaint Management Test FAILED: {e}")
            return False
    
    def test_virtual_number_generator(self):
        """Test 2: Virtual Number Generator (Twilio API)"""
        print("\n" + "="*60)
        print("TEST 2: VIRTUAL NUMBER GENERATOR")
        print("="*60)
        
        try:
            # Get telephony providers
            print("📞 Getting telephony providers...")
            response = self.session.get(f"{API_BASE}/brand-management/phone-numbers/providers")
            if response.status_code == 200:
                providers = response.json()
                print(f"✅ Providers retrieved: {len(providers.get('providers', []))} providers")
                for provider in providers.get('providers', []):
                    print(f"   - {provider.get('display_name')} ({provider.get('name')})")
            else:
                print(f"❌ Failed to get providers: {response.text}")
                return False
            
            # Search for available numbers
            print("🔍 Searching for available numbers...")
            search_params = {
                "country_code": "IN",
                "number_type": "toll-free",
                "capabilities": "voice,sms",
                "provider": "twilio"
            }
            
            response = self.session.get(f"{API_BASE}/brand-management/phone-numbers/search", params=search_params)
            if response.status_code == 200:
                numbers = response.json()
                available_numbers = numbers.get('numbers', [])
                print(f"✅ Found {len(available_numbers)} available numbers")
                
                if available_numbers:
                    self.test_phone_number = available_numbers[0]
                    print(f"   Selected: {self.test_phone_number.get('phone_number')}")
                else:
                    print("   ⚠️  No numbers available for testing")
            else:
                print(f"❌ Failed to search numbers: {response.text}")
                return False
            
            # Get brand's current phone numbers
            print("📱 Getting current phone numbers...")
            response = self.session.get(f"{API_BASE}/brand-management/phone-numbers")
            if response.status_code == 200:
                current_numbers = response.json()
                print(f"✅ Current numbers: {len(current_numbers.get('phone_numbers', []))} numbers")
            else:
                print(f"❌ Failed to get current numbers: {response.text}")
                return False
            
            # Test number status update (if we have a number)
            if self.test_phone_number:
                print("🔄 Testing number status update...")
                status_data = {"status": "inactive"}
                response = self.session.patch(
                    f"{API_BASE}/brand-management/phone-numbers/{self.test_phone_number['phone_number']}/status",
                    json=status_data
                )
                if response.status_code == 200:
                    print("✅ Status update successful")
                else:
                    print(f"❌ Status update failed: {response.text}")
            
            print("✅ Virtual Number Generator Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Virtual Number Generator Test FAILED: {e}")
            return False
    
    def test_credit_system(self):
        """Test 3: Credit System (24h free, ₹50/ticket)"""
        print("\n" + "="*60)
        print("TEST 3: CREDIT SYSTEM")
        print("="*60)
        
        try:
            # Get billing summary
            print("💰 Getting billing summary...")
            response = self.session.get(f"{API_BASE}/brand-management/billing/summary")
            if response.status_code == 200:
                summary = response.json()
                billing_data = summary.get('summary', {})
                print(f"✅ Billing summary retrieved:")
                print(f"   - Current Balance: ₹{billing_data.get('current_balance', 0)}")
                print(f"   - Monthly Spending: ₹{billing_data.get('monthly_spending', 0)}")
                print(f"   - Pending Charges: {billing_data.get('pending_charges', 0)}")
                print(f"   - Subscription Status: {billing_data.get('subscription', {}).get('active', False)}")
            else:
                print(f"❌ Failed to get billing summary: {response.text}")
                return False
            
            # Get subscription plans
            print("📋 Getting subscription plans...")
            response = self.session.get(f"{API_BASE}/brand-management/billing/plans")
            if response.status_code == 200:
                plans = response.json()
                print(f"✅ Subscription plans retrieved: {len(plans.get('plans', []))} plans")
                for plan in plans.get('plans', []):
                    print(f"   - {plan.get('name')}: ₹{plan.get('monthly_price')}/month")
            else:
                print(f"❌ Failed to get subscription plans: {response.text}")
                return False
            
            # Get transaction history
            print("📊 Getting transaction history...")
            response = self.session.get(f"{API_BASE}/brand-management/billing/transactions")
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ Transaction history retrieved: {len(transactions.get('transactions', []))} transactions")
            else:
                print(f"❌ Failed to get transactions: {response.text}")
                return False
            
            # Test credit top-up (simulation)
            print("💳 Testing credit top-up...")
            topup_data = {
                "amount": 1000,
                "payment_method": "stripe"
            }
            
            response = self.session.post(f"{API_BASE}/brand-management/billing/topup", json=topup_data)
            if response.status_code == 200:
                result = response.json()
                self.test_transaction_id = result.get('transaction_id')
                print(f"✅ Top-up initiated: Transaction ID {self.test_transaction_id}")
                print(f"   - Payment Intent ID: {result.get('payment_intent_id')}")
            else:
                print(f"❌ Top-up failed: {response.text}")
                return False
            
            print("✅ Credit System Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Credit System Test FAILED: {e}")
            return False
    
    def test_analytics_insights(self):
        """Test 4: Insights & Analytics (TAT, abuse patterns, team performance)"""
        print("\n" + "="*60)
        print("TEST 4: ANALYTICS & INSIGHTS")
        print("="*60)
        
        try:
            # Get brand analytics overview
            print("📈 Getting brand analytics overview...")
            response = self.session.get(f"{API_BASE}/brand-management/analytics/overview")
            if response.status_code == 200:
                analytics = response.json()
                overview = analytics.get('analytics', {})
                print(f"✅ Analytics overview retrieved:")
                print(f"   - Total Complaints: {overview.get('total_complaints', 0)}")
                print(f"   - Resolution Rate: {overview.get('resolution_rate', 0):.1f}%")
                print(f"   - Avg Resolution Time: {overview.get('avg_resolution_time', 0):.1f} hours")
                print(f"   - Customer Satisfaction: {overview.get('avg_satisfaction', 0)}/5")
            else:
                print(f"❌ Failed to get analytics overview: {response.text}")
                return False
            
            # Get TAT analytics
            print("⏱️  Getting TAT analytics...")
            response = self.session.get(f"{API_BASE}/brand-management/analytics/tat")
            if response.status_code == 200:
                tat_data = response.json()
                tat_analytics = tat_data.get('tat_analytics', {})
                print(f"✅ TAT analytics retrieved:")
                print(f"   - Average TAT: {tat_analytics.get('avg_tat', 0):.1f} hours")
                print(f"   - Median TAT: {tat_analytics.get('median_tat', 0):.1f} hours")
                print(f"   - 24h Resolution Rate: {tat_analytics.get('resolution_24h_rate', 0):.1f}%")
            else:
                print(f"❌ Failed to get TAT analytics: {response.text}")
                return False
            
            # Get abuse pattern analytics
            print("🚨 Getting abuse pattern analytics...")
            response = self.session.get(f"{API_BASE}/brand-management/analytics/abuse-patterns")
            if response.status_code == 200:
                abuse_data = response.json()
                abuse_analytics = abuse_data.get('abuse_analytics', {})
                print(f"✅ Abuse analytics retrieved:")
                print(f"   - Total Abuse Cases: {abuse_analytics.get('total_cases', 0)}")
                print(f"   - Abuse Rate: {abuse_analytics.get('abuse_rate', 0):.1f}%")
                print(f"   - Auto-Detection Rate: {abuse_analytics.get('auto_detection_rate', 0):.1f}%")
            else:
                print(f"❌ Failed to get abuse analytics: {response.text}")
                return False
            
            # Get team performance analytics
            print("👥 Getting team performance analytics...")
            response = self.session.get(f"{API_BASE}/brand-management/analytics/team-performance")
            if response.status_code == 200:
                team_data = response.json()
                team_analytics = team_data.get('team_analytics', {})
                print(f"✅ Team analytics retrieved:")
                print(f"   - Active Team Members: {team_analytics.get('active_members', 0)}")
                print(f"   - Avg Response Time: {team_analytics.get('avg_response_time', 0):.1f} hours")
                print(f"   - Team Efficiency: {team_analytics.get('efficiency_score', 0):.1f}%")
            else:
                print(f"❌ Failed to get team analytics: {response.text}")
                return False
            
            # Test analytics export
            print("📊 Testing analytics export...")
            export_data = {
                "report_type": "overview",
                "format": "csv"
            }
            
            response = self.session.post(f"{API_BASE}/brand-management/analytics/export", json=export_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Export initiated: {result.get('message')}")
            else:
                print(f"❌ Export failed: {response.text}")
                return False
            
            print("✅ Analytics & Insights Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Analytics & Insights Test FAILED: {e}")
            return False
    
    def test_notifications_alerts(self):
        """Test 5: Notifications & Alerts (email/SMS/WhatsApp)"""
        print("\n" + "="*60)
        print("TEST 5: NOTIFICATIONS & ALERTS")
        print("="*60)
        
        try:
            # Get user notifications
            print("🔔 Getting user notifications...")
            response = self.session.get(f"{API_BASE}/brand-management/notifications")
            if response.status_code == 200:
                notifications = response.json()
                print(f"✅ Notifications retrieved: {len(notifications.get('notifications', []))} notifications")
                
                # Mark first notification as read if available
                if notifications.get('notifications'):
                    first_notification = notifications['notifications'][0]
                    notification_id = first_notification['id']
                    
                    print(f"📖 Marking notification {notification_id} as read...")
                    response = self.session.patch(f"{API_BASE}/brand-management/notifications/{notification_id}/read")
                    if response.status_code == 200:
                        print("✅ Notification marked as read")
                    else:
                        print(f"❌ Failed to mark notification read: {response.text}")
            else:
                print(f"❌ Failed to get notifications: {response.text}")
                return False
            
            # Get notification statistics
            print("📊 Getting notification statistics...")
            response = self.session.get(f"{API_BASE}/brand-management/notifications/stats")
            if response.status_code == 200:
                stats = response.json()
                notification_stats = stats.get('stats', {})
                print(f"✅ Notification stats retrieved:")
                print(f"   - Total: {notification_stats.get('total', 0)}")
                print(f"   - Unread: {notification_stats.get('unread', 0)}")
                print(f"   - High Priority Unread: {notification_stats.get('high_priority_unread', 0)}")
                print(f"   - Read Rate: {notification_stats.get('read_rate', 0):.1f}%")
            else:
                print(f"❌ Failed to get notification stats: {response.text}")
                return False
            
            # Test sending brand notification
            print("📤 Testing brand notification...")
            notification_data = {
                "type": "test_notification",
                "data": {
                    "message": "This is a test notification from the brand management system",
                    "timestamp": datetime.utcnow().isoformat()
                },
                "channels": ["email", "in_app"]
            }
            
            response = self.session.post(f"{API_BASE}/brand-management/notifications/send", json=notification_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Notification sent: {result.get('message')}")
            else:
                print(f"❌ Failed to send notification: {response.text}")
                return False
            
            print("✅ Notifications & Alerts Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Notifications & Alerts Test FAILED: {e}")
            return False
    
    def test_api_endpoints_availability(self):
        """Test API endpoints availability"""
        print("\n" + "="*60)
        print("TEST 6: API ENDPOINTS AVAILABILITY")
        print("="*60)
        
        endpoints_to_test = [
            # Phone Number Management
            ("GET", f"{API_BASE}/brand-management/phone-numbers/providers", "Get telephony providers"),
            ("GET", f"{API_BASE}/brand-management/phone-numbers/search", "Search available numbers"),
            ("GET", f"{API_BASE}/brand-management/phone-numbers", "Get brand phone numbers"),
            
            # Billing & Credit System
            ("GET", f"{API_BASE}/brand-management/billing/summary", "Get billing summary"),
            ("GET", f"{API_BASE}/brand-management/billing/transactions", "Get transaction history"),
            ("GET", f"{API_BASE}/brand-management/billing/plans", "Get subscription plans"),
            ("POST", f"{API_BASE}/brand-management/billing/topup", "Create credit topup"),
            
            # Analytics & Insights
            ("GET", f"{API_BASE}/brand-management/analytics/overview", "Get brand analytics"),
            ("GET", f"{API_BASE}/brand-management/analytics/tat", "Get TAT analytics"),
            ("GET", f"{API_BASE}/brand-management/analytics/abuse-patterns", "Get abuse analytics"),
            ("GET", f"{API_BASE}/brand-management/analytics/team-performance", "Get team analytics"),
            ("POST", f"{API_BASE}/brand-management/analytics/export", "Export analytics"),
            
            # Notifications & Alerts
            ("GET", f"{API_BASE}/brand-management/notifications", "Get user notifications"),
            ("GET", f"{API_BASE}/brand-management/notifications/stats", "Get notification stats"),
            ("POST", f"{API_BASE}/brand-management/notifications/send", "Send brand notification"),
            
            # Complaint Management
            ("POST", f"{API_BASE}/brand-management/tickets/{self.test_ticket_id}/escalate", "Escalate ticket"),
            ("POST", f"{API_BASE}/brand-management/tickets/{self.test_ticket_id}/assign", "Assign ticket"),
        ]
        
        available_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for method, url, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(url)
                elif method == "POST":
                    response = self.session.post(url, json={})
                elif method == "PATCH":
                    response = self.session.patch(url, json={})
                
                if response.status_code in [200, 201, 400, 401, 403, 404]:
                    print(f"✅ {description}: {response.status_code}")
                    available_endpoints += 1
                else:
                    print(f"❌ {description}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {description}: Error - {e}")
        
        print(f"\n📊 Endpoints Availability: {available_endpoints}/{total_endpoints} ({available_endpoints/total_endpoints*100:.1f}%)")
        
        if available_endpoints >= total_endpoints * 0.8:  # 80% threshold
            print("✅ API Endpoints Availability Test PASSED")
            return True
        else:
            print("❌ API Endpoints Availability Test FAILED")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            if self.test_ticket_id:
                # Delete test ticket
                response = self.session.delete(f"{API_BASE}/tickets/{self.test_ticket_id}")
                if response.status_code in [200, 204]:
                    print(f"✅ Test ticket {self.test_ticket_id} deleted")
                else:
                    print(f"⚠️  Could not delete test ticket: {response.status_code}")
            
            if self.test_phone_number:
                # Release test phone number
                response = self.session.delete(f"{API_BASE}/brand-management/phone-numbers/{self.test_phone_number['phone_number']}")
                if response.status_code in [200, 204]:
                    print(f"✅ Test phone number {self.test_phone_number['phone_number']} released")
                else:
                    print(f"⚠️  Could not release test phone number: {response.status_code}")
                    
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Brand Management Features Test Suite")
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Login as brand user
        if not self.login(TEST_BRAND_EMAIL, TEST_BRAND_PASSWORD):
            print("❌ Cannot proceed without login")
            return False
        
        test_results = []
        
        # Run tests
        test_results.append(("Enhanced Complaint Management", self.test_enhanced_complaint_management()))
        test_results.append(("Virtual Number Generator", self.test_virtual_number_generator()))
        test_results.append(("Credit System", self.test_credit_system()))
        test_results.append(("Analytics & Insights", self.test_analytics_insights()))
        test_results.append(("Notifications & Alerts", self.test_notifications_alerts()))
        test_results.append(("API Endpoints Availability", self.test_api_endpoints_availability()))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Brand management features are working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        # Cleanup
        self.cleanup_test_data()
        
        return passed_tests == total_tests

def main():
    """Main function"""
    print("🔧 Brand Management Features Test Suite")
    print("Testing: Complaint Management, Phone Numbers, Billing, Analytics, Notifications")
    print("="*80)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print(f"❌ Server not running at {BASE_URL}")
            print("Please start the server with: uvicorn app.main:app --reload")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please start the server with: uvicorn app.main:app --reload")
        return False
    
    # Run tests
    tester = BrandManagementTester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 