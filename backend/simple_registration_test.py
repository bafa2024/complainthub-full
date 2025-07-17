#!/usr/bin/env python3
"""
Simple registration test that directly tests the signup endpoint
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_registration():
    """Test user registration directly"""
    print("🧪 Simple Registration Test")
    print("=" * 40)
    
    # Generate unique email
    timestamp = int(time.time())
    email = f"test_user_{timestamp}@example.com"
    
    # Test data
    signup_data = {
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Test User",
        "phone_number": "1234567890",
        "role": "user"
    }
    
    print(f"Testing registration with email: {email}")
    
    try:
        # Test registration
        response = requests.post(
            f"{API_BASE}/auth/signup",
            json=signup_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            
            # Test login
            print("\nTesting login...")
            login_data = {
                "username": email,
                "password": "TestPassword123!"
            }
            
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            print(f"Login Status Code: {login_response.status_code}")
            print(f"Login Response: {login_response.text}")
            
            if login_response.status_code == 200:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed!")
                return False
        else:
            print("❌ Registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_registration()
    if success:
        print("\n🎉 Registration test completed successfully!")
    else:
        print("\n❌ Registration test failed!") 