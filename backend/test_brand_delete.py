#!/usr/bin/env python3
"""
Test script to verify brand delete functionality
"""

import requests
import json

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

def get_brands(token):
    """Get all brands"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/brands", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get brands: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error getting brands: {e}")
        return []

def create_test_brand(token):
    """Create a test brand for deletion"""
    headers = {"Authorization": f"Bearer {token}"}
    brand_data = {
        "name": "Test Brand for Deletion",
        "support_email": "testdelete@example.com",
        "industry": "Technology",
        "logo_url": "https://example.com/logo.png",
        "contact_info": "Test Contact"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/brands", json=brand_data, headers=headers)
        if response.status_code == 200:
            brand = response.json()
            print(f"Created test brand: {brand['name']} (ID: {brand['id']})")
            return brand
        else:
            print(f"Failed to create test brand: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating test brand: {e}")
        return None

def delete_brand(token, brand_id):
    """Delete a brand"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/brands/{brand_id}", headers=headers)
        print(f"Delete response: {response.status_code}")
        if response.status_code == 200:
            print(f"Successfully deleted brand {brand_id}")
            return True
        else:
            print(f"Failed to delete brand: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error deleting brand: {e}")
        return False

def main():
    print("Testing Brand Delete Functionality")
    print("=" * 40)
    
    # Login as admin
    print("1. Logging in as admin...")
    token = login_admin()
    if not token:
        print("Failed to login. Exiting.")
        return
    
    print("✓ Login successful")
    
    # Get current brands
    print("\n2. Getting current brands...")
    brands = get_brands(token)
    print(f"✓ Found {len(brands)} brands")
    
    # Create a test brand
    print("\n3. Creating test brand for deletion...")
    test_brand = create_test_brand(token)
    if not test_brand:
        print("Failed to create test brand. Exiting.")
        return
    
    # Verify brand was created
    print("\n4. Verifying brand was created...")
    updated_brands = get_brands(token)
    print(f"✓ Now have {len(updated_brands)} brands")
    
    # Delete the test brand
    print(f"\n5. Deleting test brand (ID: {test_brand['id']})...")
    success = delete_brand(token, test_brand['id'])
    
    if success:
        # Verify brand was deleted
        print("\n6. Verifying brand was deleted...")
        final_brands = get_brands(token)
        print(f"✓ Now have {len(final_brands)} brands")
        
        # Check if the brand is actually gone
        brand_exists = any(b['id'] == test_brand['id'] for b in final_brands)
        if not brand_exists:
            print("✓ Test brand successfully deleted!")
        else:
            print("✗ Test brand still exists in the list")
    else:
        print("✗ Failed to delete test brand")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 