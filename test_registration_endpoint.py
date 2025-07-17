import requests
import json
import time

# Test the registration endpoint with a unique email
timestamp = int(time.time())
url = "http://localhost:8000/api/v1/auth/signup"
data = {
    "full_name": "Test User",
    "email": f"testuser{timestamp}@example.com",
    "phone_number": "1234567890",
    "password": "testpassword123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
    else:
        print("❌ Registration failed!")
        
except Exception as e:
    print(f"Error: {e}") 