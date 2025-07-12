#!/usr/bin/env python3
"""
Test script for Phone Number Generation API
Tests the complete phone number management functionality including:
- Telephony provider listing
- Number search and purchase
- Brand phone number management
- Request management
- Analytics
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (update with actual test user credentials)
TEST_USER_EMAIL = "brand@test.com"
TEST_USER_PASSWORD = "testpassword123"

class PhoneNumberTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.brand_id = None
        self.user_id = None
        
    def login(self):
        """Login as a brand user"""
        print("🔐 Logging in as brand user...")
        
        login_data = {
            "username": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE}/login", data=login_data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                
                # Get user info
                user_response = self.session.get(f"{API_BASE}/auth/me")
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    self.brand_id = user_data.get("brand_id")
                    self.user_id = user_data.get("id")
                    print(f"✅ Logged in successfully. Brand ID: {self.brand_id}")
                    return True
                else:
                    print(f"❌ Failed to get user info: {user_response.status_code}")
                    return False
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_get_providers(self):
        """Test getting telephony providers"""
        print("\n📞 Testing telephony providers...")
        
        try:
            response = self.session.get(f"{API_BASE}/phone-numbers/providers")
            if response.status_code == 200:
                providers = response.json()
                print(f"✅ Found {len(providers)} providers:")
                for provider in providers:
                    print(f"   - {provider['display_name']} ({provider['name']})")
                    print(f"     Countries: {provider['supported_countries']}")
                    print(f"     Capabilities: {provider['supported_capabilities']}")
                return providers
            else:
                print(f"❌ Failed to get providers: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error getting providers: {e}")
            return []
    
    def test_search_numbers(self):
        """Test searching for available numbers"""
        print("\n🔍 Testing number search...")
        
        search_params = {
            "country_code": "IN",
            "number_type": "toll-free",
            "capabilities": "voice,sms",
            "provider": ""
        }
        
        try:
            response = self.session.get(f"{API_BASE}/phone-numbers/search", params=search_params)
            if response.status_code == 200:
                numbers = response.json()
                print(f"✅ Found {len(numbers)} available numbers:")
                for number in numbers[:3]:  # Show first 3
                    print(f"   - {number['phone_number']} ({number['provider']})")
                    print(f"     Type: {number['number_type']}, Cost: ₹{number['monthly_cost']}/month")
                return numbers
            else:
                print(f"❌ Failed to search numbers: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error searching numbers: {e}")
            return []
    
    def test_purchase_number(self, available_numbers):
        """Test purchasing a phone number"""
        if not available_numbers:
            print("\n⚠️ No available numbers to purchase")
            return None
            
        print("\n💰 Testing number purchase...")
        
        # Select first available number
        selected_number = available_numbers[0]
        
        purchase_data = {
            "country_code": "IN",
            "number_type": "toll-free",
            "capabilities": ["voice", "sms"],
            "provider_preference": selected_number["provider"],
            "auto_approve": True
        }
        
        try:
            response = self.session.post(f"{API_BASE}/phone-numbers/purchase", json=purchase_data)
            if response.status_code == 200:
                result = response.json()
                if result["success"]:
                    print(f"✅ Successfully purchased {result['phone_number']}")
                    print(f"   Provider: {result['provider']}")
                    print(f"   Cost: ₹{result['cost']}")
                    return result
                else:
                    print(f"❌ Purchase failed: {result['message']}")
                    return None
            else:
                print(f"❌ Purchase request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error purchasing number: {e}")
            return None
    
    def test_get_brand_numbers(self):
        """Test getting brand's phone numbers"""
        print("\n📱 Testing brand phone numbers...")
        
        try:
            response = self.session.get(f"{API_BASE}/phone-numbers/brand")
            if response.status_code == 200:
                numbers = response.json()
                print(f"✅ Brand has {len(numbers)} phone numbers:")
                for number in numbers:
                    print(f"   - {number['phone_number']} ({number['status']})")
                    print(f"     Provider: {number['provider']}, Cost: ₹{number['monthly_cost']}/month")
                return numbers
            else:
                print(f"❌ Failed to get brand numbers: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error getting brand numbers: {e}")
            return []
    
    def test_create_request(self):
        """Test creating a phone number request"""
        print("\n📝 Testing phone number request creation...")
        
        request_data = {
            "country_code": "IN",
            "number_type": "toll-free",
            "capabilities": ["voice", "sms"],
            "provider_preference": "twilio"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/phone-numbers/requests", json=request_data)
            if response.status_code == 200:
                request = response.json()
                print(f"✅ Created request #{request['id']}")
                print(f"   Status: {request['status']}")
                print(f"   Type: {request['number_type']}")
                return request
            else:
                print(f"❌ Failed to create request: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating request: {e}")
            return None
    
    def test_get_requests(self):
        """Test getting phone number requests"""
        print("\n📋 Testing phone number requests...")
        
        try:
            response = self.session.get(f"{API_BASE}/phone-numbers/requests")
            if response.status_code == 200:
                requests = response.json()
                print(f"✅ Found {len(requests)} requests:")
                for req in requests:
                    print(f"   - Request #{req['id']}: {req['status']}")
                    if req['assigned_number']:
                        print(f"     Assigned: {req['assigned_number']}")
                return requests
            else:
                print(f"❌ Failed to get requests: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"❌ Error getting requests: {e}")
            return []
    
    def test_update_number_status(self, phone_numbers):
        """Test updating phone number status"""
        if not phone_numbers:
            print("\n⚠️ No phone numbers to update")
            return False
            
        print("\n🔄 Testing status update...")
        
        number_to_update = phone_numbers[0]
        current_status = number_to_update["status"]
        new_status = "inactive" if current_status == "active" else "active"
        
        update_data = {"status": new_status}
        
        try:
            response = self.session.put(
                f"{API_BASE}/phone-numbers/{number_to_update['phone_number']}/status",
                json=update_data
            )
            if response.status_code == 200:
                updated_number = response.json()
                print(f"✅ Updated {updated_number['phone_number']} status to {updated_number['status']}")
                return True
            else:
                print(f"❌ Failed to update status: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            return False
    
    def test_release_number(self, phone_numbers):
        """Test releasing a phone number"""
        if not phone_numbers:
            print("\n⚠️ No phone numbers to release")
            return False
            
        print("\n🗑️ Testing number release...")
        
        number_to_release = phone_numbers[0]
        
        try:
            response = self.session.delete(f"{API_BASE}/phone-numbers/{number_to_release['phone_number']}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Released {number_to_release['phone_number']}: {result['message']}")
                return True
            else:
                print(f"❌ Failed to release number: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error releasing number: {e}")
            return False
    
    def test_analytics(self):
        """Test phone number analytics"""
        print("\n📊 Testing phone number analytics...")
        
        try:
            response = self.session.get(f"{API_BASE}/phone-numbers/analytics")
            if response.status_code == 200:
                analytics = response.json()
                print("✅ Analytics data:")
                print(f"   Total numbers: {analytics['total_numbers']}")
                print(f"   Active numbers: {analytics['active_numbers']}")
                print(f"   Inactive numbers: {analytics['inactive_numbers']}")
                print(f"   Monthly cost: ₹{analytics['monthly_cost']}")
                if analytics.get('provider_stats'):
                    print("   Provider breakdown:")
                    for stat in analytics['provider_stats']:
                        print(f"     {stat['provider']}: {stat['count']} numbers")
                return analytics
            else:
                print(f"❌ Failed to get analytics: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting analytics: {e}")
            return None
    
    def run_all_tests(self):
        """Run all phone number tests"""
        print("🚀 Starting Phone Number Generation API Tests")
        print("=" * 50)
        
        # Login
        if not self.login():
            print("❌ Cannot proceed without login")
            return
        
        # Test providers
        providers = self.test_get_providers()
        
        # Test search
        available_numbers = self.test_search_numbers()
        
        # Test purchase
        purchase_result = self.test_purchase_number(available_numbers)
        
        # Test brand numbers
        brand_numbers = self.test_get_brand_numbers()
        
        # Test request creation
        request = self.test_create_request()
        
        # Test get requests
        requests = self.test_get_requests()
        
        # Test status update
        if brand_numbers:
            self.test_update_number_status(brand_numbers)
        
        # Test analytics
        analytics = self.test_analytics()
        
        # Test release (only if we have numbers)
        if brand_numbers:
            self.test_release_number(brand_numbers)
        
        print("\n" + "=" * 50)
        print("✅ Phone Number Generation API Tests Completed!")
        
        # Summary
        print("\n📋 Test Summary:")
        print(f"   Providers tested: {len(providers)}")
        print(f"   Available numbers found: {len(available_numbers)}")
        print(f"   Purchase successful: {'Yes' if purchase_result else 'No'}")
        print(f"   Brand numbers: {len(brand_numbers)}")
        print(f"   Requests created: {len(requests)}")
        print(f"   Analytics available: {'Yes' if analytics else 'No'}")

def main():
    """Main test function"""
    print("Phone Number Generation API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Make sure the server is running on http://localhost:8000")
        return
    
    # Run tests
    tester = PhoneNumberTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 