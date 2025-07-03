#!/usr/bin/env python3
"""
Test script to verify user management CRUD functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "testbrand@example.com"  # Use the test user that was reset
ADMIN_PASSWORD = "testpass123"  # Password from the reset script

def login_admin():
    """Login as admin and return the access token"""
    login_data = {
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def get_users(token):
    """Get all users"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get users: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error getting users: {e}")
        return []

def create_test_user(token):
    """Create a test user"""
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": f"testuser_{int(time.time())}@example.com",
        "full_name": "Test User",
        "phone_number": "1234567890",
        "role": "user",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/admin/users", json=user_data, headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"Created test user: {user['email']} (ID: {user['id']})")
            return user
        else:
            print(f"Failed to create test user: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None

def update_user(token, user_id):
    """Update a user"""
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "full_name": "Updated Test User",
        "phone_number": "0987654321",
        "role": "brand_user"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/v1/admin/users/{user_id}", json=user_data, headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"Updated test user: {user['full_name']} (ID: {user['id']})")
            return user
        else:
            print(f"Failed to update test user: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error updating test user: {e}")
        return None

def delete_user(token, user_id):
    """Delete a user"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/admin/users/{user_id}", headers=headers)
        print(f"Delete response: {response.status_code}")
        if response.status_code == 200:
            print(f"Successfully deleted user {user_id}")
            return True
        else:
            print(f"Failed to delete user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False

def main():
    print("Testing User Management CRUD Functionality")
    print("=" * 50)
    
    # Login as admin
    print("1. Logging in as admin...")
    token = login_admin()
    if not token:
        print("Failed to login. Exiting.")
        return
    
    print("✓ Login successful")
    
    # Get current users
    print("\n2. Getting current users...")
    users = get_users(token)
    print(f"✓ Found {len(users)} users")
    
    # Create a test user
    print("\n3. Creating test user...")
    test_user = create_test_user(token)
    if not test_user:
        print("Failed to create test user. Exiting.")
        return
    
    # Verify user was created
    print("\n4. Verifying user was created...")
    updated_users = get_users(token)
    print(f"✓ Now have {len(updated_users)} users")
    
    # Update the test user
    print(f"\n5. Updating test user (ID: {test_user['id']})...")
    updated_user = update_user(token, test_user['id'])
    if not updated_user:
        print("Failed to update test user.")
    
    # Delete the test user
    print(f"\n6. Deleting test user (ID: {test_user['id']})...")
    success = delete_user(token, test_user['id'])
    
    if success:
        # Verify user was deleted
        print("\n7. Verifying user was deleted...")
        final_users = get_users(token)
        print(f"✓ Now have {len(final_users)} users")
        
        # Check if the user is actually gone
        user_exists = any(u['id'] == test_user['id'] for u in final_users)
        if not user_exists:
            print("✓ Test user successfully deleted!")
        else:
            print("✗ Test user still exists in the list")
    else:
        print("✗ Failed to delete test user")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 