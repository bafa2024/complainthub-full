import requests
import json
import time

# Test signup
unique_email = f"test_{int(time.time())}@example.com"
signup_data = {
    "name": "Test User",
    "email": unique_email,
    "phone": "1234567890",
    "password": "password123"
}

# First, try to signup
print("Testing signup...")
response = requests.post(
    "http://localhost:8000/api/v1/auth/signup",
    json=signup_data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\nSignup successful! Now testing login...")
    
    # Test login
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"]
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        data=login_data  # Note: using data, not json for form data
    )
    
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "full_name": "Updated User Name",
            "phone_number": "9876543210"
        }
        print("\nTesting user profile update...")
        update_response = requests.put(
            "http://localhost:8000/api/v1/users/me",
            json=update_data,
            headers=headers
        )
        print(f"Update Status Code: {update_response.status_code}")
        print(f"Update Response: {update_response.text}")

        # Test account deletion
        print("\nTesting user account deletion...")
        delete_response = requests.delete(
            "http://localhost:8000/api/v1/users/me",
            headers=headers
        )
        print(f"Delete Status Code: {delete_response.status_code}")
        print(f"Delete Response: {delete_response.text}")