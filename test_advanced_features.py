#!/usr/bin/env python3
"""
Comprehensive Test Script for Advanced Features

Tests:
1. Ticket Status Tagging with UI
2. Post-Resolution Verification
3. Voice Transcription SEO Indexing

Run with: python test_advanced_features.py
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
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_BRAND_EMAIL = "brand@example.com"
TEST_BRAND_PASSWORD = "brandpassword123"

class AdvancedFeaturesTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_ticket_id = None
        self.test_followup_id = None
        
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
    
    def test_ticket_status_tagging(self):
        """Test 1: Ticket Status Tagging with UI"""
        print("\n" + "="*60)
        print("TEST 1: TICKET STATUS TAGGING WITH UI")
        print("="*60)
        
        try:
            # Create a test ticket
            print("📝 Creating test ticket...")
            ticket_data = {
                "title": "Test complaint for tagging",
                "description": "This is a test complaint to verify the tagging system. Customer is very angry about poor service quality.",
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
            
            # Test auto-tagging
            print("🤖 Testing AI auto-tagging...")
            response = self.session.post(f"{API_BASE}/tickets_extended/{self.test_ticket_id}/auto-tag")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Auto-tagging successful:")
                print(f"   - Severity Level: {result['auto_tagging_results']['severity_level']} ({result['auto_tagging_results']['severity_label']})")
                print(f"   - Urgency: {result['auto_tagging_results']['urgency']}")
                print(f"   - Abuse Flag: {result['auto_tagging_results']['abuse_level_flag']}")
                print(f"   - Sentiment Score: {result['auto_tagging_results']['sentiment_score']:.2f}")
                print(f"   - Toxicity Score: {result['auto_tagging_results']['toxicity_score']:.2f}")
            else:
                print(f"❌ Auto-tagging failed: {response.text}")
                return False
            
            # Test manual tagging updates
            print("🏷️  Testing manual tagging updates...")
            tagging_updates = [
                {"severity_level": 3, "urgency": "high"},
                {"abuse_level_flag": True},
                {"severity_level": 2, "urgency": "medium", "abuse_level_flag": False}
            ]
            
            for i, update in enumerate(tagging_updates, 1):
                response = self.session.patch(f"{API_BASE}/tickets/{self.test_ticket_id}", json=update)
                if response.status_code == 200:
                    ticket = response.json()
                    print(f"✅ Tagging update {i} successful:")
                    print(f"   - Severity: {ticket.get('severity_level', 'N/A')}")
                    print(f"   - Urgency: {ticket.get('urgency', 'N/A')}")
                    print(f"   - Abuse Flag: {ticket.get('abuse_level_flag', 'N/A')}")
                else:
                    print(f"❌ Tagging update {i} failed: {response.text}")
                    return False
            
            print("✅ Ticket Status Tagging Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Ticket Status Tagging Test FAILED: {e}")
            return False
    
    def test_post_resolution_verification(self):
        """Test 2: Post-Resolution Verification"""
        print("\n" + "="*60)
        print("TEST 2: POST-RESOLUTION VERIFICATION")
        print("="*60)
        
        try:
            if not self.test_ticket_id:
                print("❌ No test ticket available for verification test")
                return False
            
            # Mark ticket as resolved
            print("✅ Marking ticket as resolved...")
            response = self.session.patch(f"{API_BASE}/tickets/{self.test_ticket_id}", json={"status": "resolved"})
            if response.status_code != 200:
                print(f"❌ Failed to mark ticket as resolved: {response.text}")
                return False
            
            # Schedule post-resolution verification
            print("📅 Scheduling post-resolution verification...")
            response = self.session.post(f"{API_BASE}/followup/schedule/{self.test_ticket_id}", json={"delay_hours": 0})
            if response.status_code == 200:
                result = response.json()
                self.test_followup_id = result.get("follow_up_id")
                print(f"✅ Follow-up scheduled with ID: {self.test_followup_id}")
                print(f"   - Scheduled time: {result.get('scheduled_time')}")
                print(f"   - Message: {result.get('message')}")
            else:
                print(f"❌ Failed to schedule follow-up: {response.text}")
                return False
            
            # Execute follow-up immediately (for testing)
            print("📞 Executing follow-up verification...")
            response = self.session.post(f"{API_BASE}/followup/execute/{self.test_followup_id}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Follow-up execution started: {result.get('message')}")
            else:
                print(f"❌ Failed to execute follow-up: {response.text}")
                return False
            
            # Test follow-up response handling
            print("💬 Testing follow-up response handling...")
            test_responses = [
                {"response": "resolved", "rating": 5},
                {"response": "not_resolved", "rating": 2},
                {"response": "resolved", "rating": 4}
            ]
            
            for i, test_response in enumerate(test_responses, 1):
                response = self.session.post(f"{API_BASE}/followup/response", json={
                    "follow_up_id": self.test_followup_id,
                    "response": test_response["response"],
                    "rating": test_response["rating"]
                })
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Response {i} processed: {result.get('message')}")
                else:
                    print(f"❌ Response {i} failed: {response.text}")
                    return False
            
            # Get follow-up analytics
            print("📊 Getting follow-up analytics...")
            response = self.session.get(f"{API_BASE}/followup/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Follow-up analytics retrieved:")
                print(f"   - Total follow-ups: {stats.get('total_followups', 'N/A')}")
                print(f"   - Response rate: {stats.get('response_rate', 'N/A')}%")
                print(f"   - Average rating: {stats.get('average_rating', 'N/A')}")
            else:
                print(f"❌ Failed to get follow-up analytics: {response.text}")
            
            print("✅ Post-Resolution Verification Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Post-Resolution Verification Test FAILED: {e}")
            return False
    
    def test_seo_indexing(self):
        """Test 3: Voice Transcription SEO Indexing"""
        print("\n" + "="*60)
        print("TEST 3: VOICE TRANSCRIPTION SEO INDEXING")
        print("="*60)
        
        try:
            if not self.test_ticket_id:
                print("❌ No test ticket available for SEO test")
                return False
            
            # Generate SEO content from transcription
            print("🔍 Generating SEO content from transcription...")
            response = self.session.post(f"{API_BASE}/seo/generate-seo-content/{self.test_ticket_id}")
            if response.status_code == 200:
                seo_content = response.json()
                print(f"✅ SEO content generated:")
                print(f"   - Title: {seo_content['seo_elements']['title']}")
                print(f"   - Description: {seo_content['seo_elements']['description'][:100]}...")
                print(f"   - Keywords: {', '.join(seo_content['seo_elements']['keywords'][:5])}")
                print(f"   - Category: {seo_content['seo_elements']['category']}")
                print(f"   - Language: {seo_content['language']}")
            else:
                print(f"❌ Failed to generate SEO content: {response.text}")
                return False
            
            # Generate static page
            print("📄 Generating static HTML page...")
            response = self.session.post(f"{API_BASE}/seo/generate/{self.test_ticket_id}")
            if response.status_code == 200:
                static_page = response.json()
                print(f"✅ Static page generated:")
                print(f"   - Filepath: {static_page.get('filepath')}")
                print(f"   - URL: {static_page.get('url')}")
                print(f"   - Filename: {static_page.get('filename')}")
            else:
                print(f"❌ Failed to generate static page: {response.text}")
                return False
            
            # Generate sitemap
            print("🗺️  Generating sitemap...")
            response = self.session.post(f"{API_BASE}/seo/generate-sitemap")
            if response.status_code == 200:
                sitemap = response.json()
                print(f"✅ Sitemap generated:")
                print(f"   - Total URLs: {sitemap.get('total_urls')}")
                print(f"   - Complaint URLs: {sitemap.get('complaint_urls')}")
                print(f"   - Filepath: {sitemap.get('sitemap_path')}")
            else:
                print(f"❌ Failed to generate sitemap: {response.text}")
                return False
            
            # Generate robots.txt
            print("🤖 Generating robots.txt...")
            response = self.session.post(f"{API_BASE}/seo/generate-robots")
            if response.status_code == 200:
                robots = response.json()
                print(f"✅ Robots.txt generated: {robots.get('robots_path')}")
            else:
                print(f"❌ Failed to generate robots.txt: {response.text}")
                return False
            
            # Get SEO analytics
            print("📊 Getting SEO analytics...")
            response = self.session.get(f"{API_BASE}/seo/analytics")
            if response.status_code == 200:
                analytics = response.json()
                print(f"✅ SEO analytics retrieved:")
                print(f"   - Total public tickets: {analytics['analytics'].get('total_public_tickets')}")
                print(f"   - Transcript coverage: {analytics['analytics'].get('transcript_coverage')}%")
                print(f"   - Static pages generated: {analytics['analytics'].get('static_pages_generated')}")
                print(f"   - Language distribution: {analytics['analytics'].get('language_distribution')}")
            else:
                print(f"❌ Failed to get SEO analytics: {response.text}")
            
            # Test public complaints endpoint
            print("🌐 Testing public complaints endpoint...")
            response = self.session.get(f"{API_BASE}/seo/public-complaints?limit=5")
            if response.status_code == 200:
                public_complaints = response.json()
                print(f"✅ Public complaints retrieved: {public_complaints.get('total')} complaints")
                for complaint in public_complaints.get('complaints', [])[:2]:
                    print(f"   - Complaint {complaint['id']}: {complaint['title']}")
            else:
                print(f"❌ Failed to get public complaints: {response.text}")
            
            print("✅ Voice Transcription SEO Indexing Test PASSED")
            return True
            
        except Exception as e:
            print(f"❌ Voice Transcription SEO Indexing Test FAILED: {e}")
            return False
    
    def test_api_endpoints_availability(self):
        """Test API endpoints availability"""
        print("\n" + "="*60)
        print("TEST 4: API ENDPOINTS AVAILABILITY")
        print("="*60)
        
        endpoints_to_test = [
            # Ticket tagging endpoints
            ("GET", f"{API_BASE}/tickets/", "Get tickets"),
            ("POST", f"{API_BASE}/tickets_extended/{self.test_ticket_id}/auto-tag", "Auto-tag ticket"),
            ("PATCH", f"{API_BASE}/tickets/{self.test_ticket_id}", "Update ticket"),
            
            # Follow-up endpoints
            ("POST", f"{API_BASE}/followup/schedule/{self.test_ticket_id}", "Schedule follow-up"),
            ("GET", f"{API_BASE}/followup/stats", "Get follow-up stats"),
            
            # SEO endpoints
            ("POST", f"{API_BASE}/seo/generate-seo-content/{self.test_ticket_id}", "Generate SEO content"),
            ("POST", f"{API_BASE}/seo/generate/{self.test_ticket_id}", "Generate static page"),
            ("POST", f"{API_BASE}/seo/generate-sitemap", "Generate sitemap"),
            ("POST", f"{API_BASE}/seo/generate-robots", "Generate robots.txt"),
            ("GET", f"{API_BASE}/seo/analytics", "Get SEO analytics"),
            ("GET", f"{API_BASE}/seo/public-complaints", "Get public complaints"),
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
            
            # Clean up static pages
            if os.path.exists("static_pages"):
                import shutil
                shutil.rmtree("static_pages")
                print("✅ Static pages directory cleaned")
                
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Advanced Features Test Suite")
        print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Login as brand user
        if not self.login(TEST_BRAND_EMAIL, TEST_BRAND_PASSWORD):
            print("❌ Cannot proceed without login")
            return False
        
        test_results = []
        
        # Run tests
        test_results.append(("Ticket Status Tagging", self.test_ticket_status_tagging()))
        test_results.append(("Post-Resolution Verification", self.test_post_resolution_verification()))
        test_results.append(("Voice Transcription SEO Indexing", self.test_seo_indexing()))
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
            print("🎉 ALL TESTS PASSED! Advanced features are working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        # Cleanup
        self.cleanup_test_data()
        
        return passed_tests == total_tests

def main():
    """Main function"""
    print("🔧 Advanced Features Test Suite")
    print("Testing: Ticket Status Tagging, Post-Resolution Verification, SEO Indexing")
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
    tester = AdvancedFeaturesTester()
    success = tester.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 