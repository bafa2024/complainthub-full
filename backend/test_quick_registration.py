import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Test data
timestamp = str(int(time.time()))
test_user = {
    "email": f"test_user_{timestamp}@example.com",
    "password": "SecurePassword123!",
    "full_name": f"Test User {timestamp}",
    "phone_number": f"+1234567{timestamp[-4:]}"
}

print(f"\n📝 Testing registration for: {test_user['email']}")

try:
    # Send registration request
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/signup",
        json=test_user,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        data = response.json()
        print(f"   User ID: {data.get('id')}")
        print(f"   Email: {data.get('email')}")
        print(f"   Role: {data.get('role')}")
    else:
        print("❌ Registration failed!")
        
except requests.exceptions.Timeout:
    print("⏱️ Request timed out after 10 seconds")
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server")
except Exception as e:
    print(f"❌ Error: {str(e)}") 