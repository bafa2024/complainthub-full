#!/usr/bin/env python3
"""
Test script to verify user deletion with related data handling
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "testbrand@example.com"
ADMIN_PASSWORD = "testpass123"

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
        "full_name": "Test User for Deletion",
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

def create_test_ticket(token, user_id):
    """Create a test ticket for the user"""
    headers = {"Authorization": f"Bearer {token}"}
    ticket_data = {
        "title": "Test Ticket",
        "description": "This is a test ticket",
        "brand_id": 1,  # Assuming brand ID 1 exists
        "channel": "web"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tickets", json=ticket_data, headers=headers)
        if response.status_code == 200:
            ticket = response.json()
            print(f"Created test ticket: {ticket['title']} (ID: {ticket['id']})")
            return ticket
        else:
            print(f"Failed to create test ticket: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating test ticket: {e}")
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
    print("Testing User Deletion with Related Data")
    print("=" * 45)
    
    # Login as admin
    print("1. Logging in as admin...")
    token = login_admin()
    if not token:
        print("Failed to login. Exiting.")
        return
    
    print("✓ Login successful")
    
    # Create a test user
    print("\n2. Creating test user...")
    test_user = create_test_user(token)
    if not test_user:
        print("Failed to create test user. Exiting.")
        return
    
    # Create a test ticket for this user (this would normally be done by the user themselves)
    print(f"\n3. Creating test ticket for user {test_user['id']}...")
    test_ticket = create_test_ticket(token, test_user['id'])
    
    # Try to delete the user (should fail if they have tickets)
    print(f"\n4. Attempting to delete user {test_user['id']}...")
    success = delete_user(token, test_user['id'])
    
    if success:
        print("✓ User was deleted successfully (no related data found)")
    else:
        print("✗ User deletion was blocked (related data found)")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 