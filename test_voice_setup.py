#!/usr/bin/env python3
"""
Setup script to create test users and brands for voice complaint testing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_brand():
    """Create a test brand"""
    brand_data = {
        "name": "Test Brand",
        "support_email": "support@testbrand.com",
        "industry": "Technology"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/brands/", json=brand_data)
        if response.status_code == 200:
            brand = response.json()
            print(f"✓ Test brand created: {brand['name']} (ID: {brand['id']})")
            return brand['id']
        else:
            print(f"✗ Failed to create brand: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating brand: {e}")
        return None

def create_test_user(brand_id):
    """Create a test user"""
    user_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✓ Test user created: {user['email']} (ID: {user['id']})")
            return user['id']
        else:
            print(f"✗ Failed to create user: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return None

def create_brand_user(brand_id):
    """Create a brand user"""
    brand_user_data = {
        "email": "branduser@testbrand.com",
        "password": "brandpass123",
        "full_name": "Brand User",
        "role": "brand_user",
        "brand_id": brand_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=brand_user_data)
        if response.status_code == 200:
            user = response.json()
            print(f"✓ Brand user created: {user['email']} (ID: {user['id']})")
            return user['id']
        else:
            print(f"✗ Failed to create brand user: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating brand user: {e}")
        return None

def test_login(email, password):
    """Test login and return token"""
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Login successful for {email}")
            return token
        else:
            print(f"✗ Login failed for {email}: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error during login: {e}")
        return None

def main():
    """Main setup function"""
    print("=== Setting up test environment for voice complaint testing ===")
    
    # Create test brand
    brand_id = create_test_brand()
    if not brand_id:
        print("Cannot proceed without brand")
        return
    
    # Create test user
    user_id = create_test_user(brand_id)
    if not user_id:
        print("Cannot proceed without user")
        return
    
    # Create brand user
    brand_user_id = create_brand_user(brand_id)
    if not brand_user_id:
        print("Cannot proceed without brand user")
        return
    
    # Test logins
    print("\n=== Testing Logins ===")
    user_token = test_login("testuser@example.com", "testpassword123")
    brand_token = test_login("branduser@testbrand.com", "brandpass123")
    
    if user_token and brand_token:
        print("\n=== Setup Complete ===")
        print("Test credentials:")
        print("  Regular User: testuser@example.com / testpassword123")
        print("  Brand User: branduser@testbrand.com / brandpass123")
        print("  Brand ID: ", brand_id)
        print("\nYou can now test the voice complaint feature!")
    else:
        print("✗ Setup incomplete - login tests failed")

if __name__ == "__main__":
    main() 