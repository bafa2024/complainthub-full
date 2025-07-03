#!/usr/bin/env python3
"""
Test script for admin brand creation functionality
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

def test_admin_brand_creation():
    """Test admin brand creation functionality"""
    
    print("🧪 Testing Admin Brand Creation Functionality")
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
    
    # Step 2: Test admin brand creation
    print("\n2. Testing admin brand creation...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    brand_data = {
        "name": "Test Admin Brand Creation",
        "support_email": "admin@testbrand.com",
        "industry": "Technology",
        "logo_url": "https://example.com/logo.png"
    }
    
    try:
        create_response = requests.post(
            f"{API_BASE}/admin/brands", 
            json=brand_data,
            headers=headers
        )
        
        print(f"Status Code: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        
        if create_response.status_code == 200:
            brand_info = create_response.json()
            print(f"✅ Admin brand created successfully!")
            print(f"   Brand ID: {brand_info['id']}")
            print(f"   Brand Name: {brand_info['name']}")
            print(f"   Support Email: {brand_info['support_email']}")
            return True
        else:
            print(f"❌ Admin brand creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Admin brand creation error: {e}")
        return False

def test_admin_brand_creation_validation():
    """Test admin brand creation validation"""
    
    print("\n🧪 Testing Admin Brand Creation Validation")
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
    
    # Test 1: Missing required fields
    print("\n2. Testing missing required fields...")
    invalid_brand_data = {
        "name": "Test Brand",
        # Missing support_email
    }
    
    try:
        create_response = requests.post(
            f"{API_BASE}/admin/brands", 
            json=invalid_brand_data,
            headers=headers
        )
        
        if create_response.status_code == 422:
            print("✅ Validation working - missing required fields rejected")
        else:
            print(f"❌ Expected validation error, got: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Validation test error: {e}")
    
    # Test 2: Duplicate brand name
    print("\n3. Testing duplicate brand name...")
    duplicate_brand_data = {
        "name": "Test Admin Brand Creation",  # Same name as created above
        "support_email": "duplicate@testbrand.com"
    }
    
    try:
        create_response = requests.post(
            f"{API_BASE}/admin/brands", 
            json=duplicate_brand_data,
            headers=headers
        )
        
        if create_response.status_code == 400:
            print("✅ Validation working - duplicate brand name rejected")
        else:
            print(f"❌ Expected duplicate error, got: {create_response.status_code}")
            print(f"Response: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Duplicate test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Admin Brand Creation Tests")
    print("=" * 50)
    
    # Test basic admin brand creation
    success = test_admin_brand_creation()
    
    # Test validation
    test_admin_brand_creation_validation()
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 