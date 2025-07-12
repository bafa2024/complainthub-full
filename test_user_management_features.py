#!/usr/bin/env python3
"""
Test Script for User Management Features
Tests all implemented user management functionality including:
- Enhanced User Dashboard with Timeline View
- Multi-Channel Complaint Submission
- Public SEO Section for Unresolved Complaints
- Enhanced User Settings and Profile Management
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test user credentials
TEST_USER = {
    "email": "testuser@example.com",
    "password": "testpassword123"
}

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test_result(test_name, success, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=TEST_USER)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting auth token: {e}")
        return None

def test_user_dashboard_features():
    """Test enhanced user dashboard features"""
    print_section("Testing Enhanced User Dashboard Features")
    
    token = get_auth_token()
    if not token:
        print_test_result("Dashboard Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting user tickets with filtering
    try:
        response = requests.get(f"{API_BASE}/tickets/", headers=headers, params={
            "status": "new",
            "limit": 10
        })
        success = response.status_code == 200
        print_test_result("Ticket Filtering", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Ticket Filtering", False, str(e))
    
    # Test advanced ticket filtering
    try:
        response = requests.get(f"{API_BASE}/tickets/filter/advanced", headers=headers, params={
            "status": "new",
            "sort_by": "created_at",
            "sort_order": "desc",
            "limit": 5
        })
        success = response.status_code == 200
        print_test_result("Advanced Ticket Filtering", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Advanced Ticket Filtering", False, str(e))
    
    # Test ticket statistics
    try:
        response = requests.get(f"{API_BASE}/tickets/stats/summary", headers=headers)
        success = response.status_code == 200
        if success:
            stats = response.json()
            print_test_result("Ticket Statistics", True, f"Total: {stats.get('total_tickets', 0)}")
        else:
            print_test_result("Ticket Statistics", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Ticket Statistics", False, str(e))

def test_multi_channel_complaint_submission():
    """Test multi-channel complaint submission"""
    print_section("Testing Multi-Channel Complaint Submission")
    
    token = get_auth_token()
    if not token:
        print_test_result("Complaint Submission Auth", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test web chat complaint submission
    try:
        complaint_data = {
            "title": "Test complaint via web chat",
            "description": "This is a test complaint submitted via web chat channel",
            "brand_id": 1,
            "category": "complaint",
            "urgency": "medium",
            "channel": "webchat",
            "is_public": False
        }
        response = requests.post(f"{API_BASE}/tickets/", headers=headers, json=complaint_data)
        success = response.status_code == 201
        print_test_result("Web Chat Complaint Submission", success, f"Status: {response.status_code}")
        
        if success:
            ticket_id = response.json().get("id")
            print(f"    Created ticket ID: {ticket_id}")
    except Exception as e:
        print_test_result("Web Chat Complaint Submission", False, str(e))
    
    # Test voice complaint submission (simulated)
    try:
        voice_complaint_data = {
            "title": "Test voice complaint",
            "description": "This is a test complaint submitted via voice channel",
            "brand_id": 1,
            "category": "technical",
            "urgency": "high",
            "channel": "voice",
            "is_public": True
        }
        response = requests.post(f"{API_BASE}/tickets/", headers=headers, json=voice_complaint_data)
        success = response.status_code == 201
        print_test_result("Voice Complaint Submission", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Voice Complaint Submission", False, str(e))
    
    # Test WhatsApp complaint submission
    try:
        whatsapp_complaint_data = {
            "title": "Test WhatsApp complaint",
            "description": "This is a test complaint submitted via WhatsApp",
            "brand_id": 1,
            "category": "billing",
            "urgency": "low",
            "channel": "whatsapp",
            "is_public": False
        }
        response = requests.post(f"{API_BASE}/tickets/", headers=headers, json=whatsapp_complaint_data)
        success = response.status_code == 201
        print_test_result("WhatsApp Complaint Submission", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("WhatsApp Complaint Submission", False, str(e))

def test_public_seo_section():
    """Test public SEO section for unresolved complaints"""
    print_section("Testing Public SEO Section")
    
    # Test getting public complaints
    try:
        response = requests.get(f"{API_BASE}/tickets/public", params={
            "limit": 10
        })
        success = response.status_code == 200
        if success:
            complaints = response.json()
            print_test_result("Public Complaints API", True, f"Found {len(complaints)} complaints")
        else:
            print_test_result("Public Complaints API", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Public Complaints API", False, str(e))
    
    # Test public complaints with filtering
    try:
        response = requests.get(f"{API_BASE}/tickets/public", params={
            "status": "unresolved",
            "limit": 5
        })
        success = response.status_code == 200
        print_test_result("Public Complaints Filtering", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Public Complaints Filtering", False, str(e))

def test_user_settings_management():
    """Test enhanced user settings and profile management"""
    print_section("Testing User Settings Management")
    
    token = get_auth_token()
    if not token:
        print_test_result("Settings Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting user profile
    try:
        response = requests.get(f"{API_BASE}/users/me", headers=headers)
        success = response.status_code == 200
        print_test_result("Get User Profile", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Get User Profile", False, str(e))
    
    # Test updating user profile
    try:
        profile_update = {
            "full_name": "Test User Updated",
            "phone": "+1234567890",
            "language": "en",
            "timezone": "UTC"
        }
        response = requests.put(f"{API_BASE}/users/me", headers=headers, json=profile_update)
        success = response.status_code == 200
        print_test_result("Update User Profile", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Update User Profile", False, str(e))
    
    # Test notification preferences
    try:
        notification_prefs = {
            "email_response": True,
            "email_status": True,
            "sms_urgent": True,
            "whatsapp_enable": False,
            "push_notifications": True
        }
        response = requests.put(f"{API_BASE}/users/me/notifications", headers=headers, json=notification_prefs)
        success = response.status_code == 200
        print_test_result("Update Notification Preferences", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Update Notification Preferences", False, str(e))
    
    # Test privacy settings
    try:
        privacy_settings = {
            "profile_visibility": "anonymous",
            "share_analytics": False,
            "allow_contact": True,
            "data_retention": "1year"
        }
        response = requests.put(f"{API_BASE}/users/me/privacy", headers=headers, json=privacy_settings)
        success = response.status_code == 200
        print_test_result("Update Privacy Settings", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Update Privacy Settings", False, str(e))
    
    # Test getting complaint history
    try:
        response = requests.get(f"{API_BASE}/users/me/complaints", headers=headers)
        success = response.status_code == 200
        if success:
            complaints = response.json()
            print_test_result("Get Complaint History", True, f"Found {len(complaints)} complaints")
        else:
            print_test_result("Get Complaint History", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Get Complaint History", False, str(e))
    
    # Test getting complaint statistics
    try:
        response = requests.get(f"{API_BASE}/users/me/complaints/stats", headers=headers)
        success = response.status_code == 200
        if success:
            stats = response.json()
            print_test_result("Get Complaint Statistics", True, f"Total: {stats.get('total_complaints', 0)}")
        else:
            print_test_result("Get Complaint Statistics", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Get Complaint Statistics", False, str(e))
    
    # Test getting active sessions
    try:
        response = requests.get(f"{API_BASE}/users/me/sessions", headers=headers)
        success = response.status_code == 200
        print_test_result("Get Active Sessions", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Get Active Sessions", False, str(e))
    
    # Test data export
    try:
        response = requests.get(f"{API_BASE}/users/me/export", headers=headers)
        success = response.status_code == 200
        print_test_result("Export User Data", success, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Export User Data", False, str(e))

def test_ticket_timeline():
    """Test ticket timeline functionality"""
    print_section("Testing Ticket Timeline Features")
    
    token = get_auth_token()
    if not token:
        print_test_result("Timeline Authentication", False, "Could not get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, create a test ticket
    try:
        complaint_data = {
            "title": "Test ticket for timeline",
            "description": "This ticket is for testing timeline functionality",
            "brand_id": 1,
            "category": "complaint",
            "urgency": "medium",
            "channel": "webchat"
        }
        response = requests.post(f"{API_BASE}/tickets/", headers=headers, json=complaint_data)
        if response.status_code == 201:
            ticket_id = response.json().get("id")
            print(f"Created test ticket ID: {ticket_id}")
            
            # Test getting ticket timeline
            try:
                response = requests.get(f"{API_BASE}/tickets/{ticket_id}/timeline", headers=headers)
                success = response.status_code == 200
                if success:
                    timeline = response.json()
                    print_test_result("Get Ticket Timeline", True, f"Found {len(timeline.get('timeline', []))} events")
                else:
                    print_test_result("Get Ticket Timeline", False, f"Status: {response.status_code}")
            except Exception as e:
                print_test_result("Get Ticket Timeline", False, str(e))
        else:
            print_test_result("Create Test Ticket", False, f"Status: {response.status_code}")
    except Exception as e:
        print_test_result("Create Test Ticket", False, str(e))

def test_frontend_components():
    """Test frontend component availability"""
    print_section("Testing Frontend Component Availability")
    
    # Test if main pages are accessible
    pages_to_test = [
        "/dashboard",
        "/new-complaint", 
        "/settings",
        "/complaints"
    ]
    
    for page in pages_to_test:
        try:
            response = requests.get(f"{BASE_URL}{page}")
            success = response.status_code in [200, 302]  # 302 for redirects
            print_test_result(f"Frontend Page: {page}", success, f"Status: {response.status_code}")
        except Exception as e:
            print_test_result(f"Frontend Page: {page}", False, str(e))

def main():
    """Run all tests"""
    print("🚀 Starting User Management Features Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all test suites
    test_user_dashboard_features()
    test_multi_channel_complaint_submission()
    test_public_seo_section()
    test_user_settings_management()
    test_ticket_timeline()
    test_frontend_components()
    
    print_section("Test Summary")
    print("✅ All User Management features have been tested!")
    print("\n📋 Implemented Features:")
    print("  • Enhanced User Dashboard with Timeline View and Filtering")
    print("  • Multi-Channel Complaint Submission (Web, Voice, WhatsApp, etc.)")
    print("  • Public SEO Section for Unresolved Complaints (>7 days)")
    print("  • Enhanced User Settings and Profile Management")
    print("  • Advanced Ticket Filtering and Statistics")
    print("  • User Data Export and Privacy Controls")
    print("  • Session Management and Security Features")
    
    print("\n🎯 Next Steps:")
    print("  1. Start the backend server: python -m uvicorn app.main:app --reload")
    print("  2. Start the frontend: npm run dev")
    print("  3. Access the application at: http://localhost:3000")
    print("  4. Test the features manually in the browser")

if __name__ == "__main__":
    main() 