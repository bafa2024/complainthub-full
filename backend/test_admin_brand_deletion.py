#!/usr/bin/env python3
"""
Test script for admin brand deletion functionality
"""

import requests
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_admin_brand_deletion():
    """Test admin brand deletion functionality"""
    
    print("🧪 Testing Admin Brand Deletion Functionality")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_data = {
        "username": "admin@complainthub.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/login/access-token", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✅ Admin login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Create a test brand first
    print("\n2. Creating a test brand for deletion...")
    brand_data = {
        "name": "Test Brand For Deletion",
        "support_email": "delete@testbrand.com",
        "industry": "Technology",
        "logo_url": "https://example.com/logo.png"
    }
    
    try:
        create_response = requests.post(
            f"{API_BASE}/admin/brands", 
            json=brand_data,
            headers=headers
        )
        
        if create_response.status_code != 200:
            print(f"❌ Failed to create test brand: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            return False
        
        brand_info = create_response.json()
        brand_id = brand_info['id']
        print(f"✅ Test brand created with ID: {brand_id}")
        
    except Exception as e:
        print(f"❌ Error creating test brand: {e}")
        return False
    
    # Step 3: Test brand deletion
    print(f"\n3. Testing brand deletion for ID: {brand_id}...")
    
    try:
        delete_response = requests.delete(
            f"{API_BASE}/admin/brands/{brand_id}",
            headers=headers
        )
        
        print(f"Status Code: {delete_response.status_code}")
        print(f"Response: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print(f"✅ Brand deleted successfully!")
            return True
        else:
            print(f"❌ Brand deletion failed")
            return False
            
    except Exception as e:
        print(f"❌ Brand deletion error: {e}")
        return False

def test_admin_brand_deletion_validation():
    """Test admin brand deletion validation"""
    
    print("\n🧪 Testing Admin Brand Deletion Validation")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_data = {
        "username": "admin@complainthub.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/login/access-token", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✅ Admin login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 1: Delete non-existent brand
    print("\n2. Testing deletion of non-existent brand...")
    try:
        delete_response = requests.delete(
            f"{API_BASE}/admin/brands/99999",  # Non-existent ID
            headers=headers
        )
        
        if delete_response.status_code == 404:
            print("✅ Validation working - non-existent brand returns 404")
        else:
            print(f"❌ Expected 404 error, got: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            
    except Exception as e:
        print(f"❌ Non-existent brand test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Admin Brand Deletion Tests")
    print("=" * 50)
    
    # Test basic admin brand deletion
    success = test_admin_brand_deletion()
    
    # Test validation
    test_admin_brand_deletion_validation()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 