import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration endpoint"""
    print("\n🚀 Testing User Registration")
    print("=" * 50)
    
    # Generate unique test user data
    timestamp = str(int(time.time()))
    test_user = {
        "email": f"test_user_{timestamp}@example.com",
        "password": "SecurePassword123!",
        "full_name": f"Test User {timestamp}",
        "phone_number": f"+1234567{timestamp[-4:]}"
    }
    
    print(f"\n📝 Registering user: {test_user['email']}")
    
    try:
        # Send registration request
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Registration successful!")
            print(f"   User ID: {data.get('id', 'N/A')}")
            print(f"   Email: {data.get('email', 'N/A')}")
            print(f"   Role: {data.get('role', 'N/A')}")
            return True
        else:
            print(f"❌ Registration failed!")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_duplicate_registration():
    """Test duplicate email registration"""
    print("\n\n🔄 Testing Duplicate Registration Prevention")
    print("=" * 50)
    
    # Use a fixed email for duplicate test
    test_user = {
        "email": "duplicate_test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Duplicate Test User",
        "phone_number": "+1234567890"
    }
    
    print(f"\n📝 First registration attempt: {test_user['email']}")
    
    try:
        # First registration
        response1 = requests.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 First attempt status: {response1.status_code}")
        
        # Second registration (should fail)
        print(f"\n📝 Second registration attempt (should fail)")
        response2 = requests.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Second attempt status: {response2.status_code}")
        
        if response2.status_code == 400:
            print("✅ Duplicate registration correctly prevented!")
            print(f"   Error message: {response2.json().get('detail', 'N/A')}")
            return True
        else:
            print("❌ Duplicate registration was not prevented!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_invalid_registration():
    """Test registration with invalid data"""
    print("\n\n🚫 Testing Invalid Registration Data")
    print("=" * 50)
    
    invalid_cases = [
        {
            "name": "Missing email",
            "data": {
                "password": "SecurePassword123!",
                "full_name": "Test User"
            }
        },
        {
            "name": "Invalid email format",
            "data": {
                "email": "not-an-email",
                "password": "SecurePassword123!",
                "full_name": "Test User"
            }
        },
        {
            "name": "Weak password",
            "data": {
                "email": "test@example.com",
                "password": "123",
                "full_name": "Test User"
            }
        }
    ]
    
    all_passed = True
    
    for case in invalid_cases:
        print(f"\n📝 Testing: {case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/signup",
                json=case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [400, 422]:
                print(f"   ✅ Correctly rejected (status: {response.status_code})")
            else:
                print(f"   ❌ Should have been rejected (status: {response.status_code})")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("\n🧪 USER REGISTRATION TEST SUITE")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing server: {BASE_URL}")
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️ Server returned unexpected status")
    except:
        print("❌ Could not connect to server. Please ensure it's running on port 8000")
        return
    
    # Run tests
    results = []
    results.append(("Basic Registration", test_user_registration()))
    results.append(("Duplicate Prevention", test_duplicate_registration()))
    results.append(("Invalid Data Handling", test_invalid_registration()))
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main() 