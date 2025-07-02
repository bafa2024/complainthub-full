#!/usr/bin/env python3
"""
Test brand profile update functionality
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_brand_profile_update():
    print("🧪 Testing Brand Profile Update")
    print("=" * 50)
    
    # Step 1: Login as brand user
    print("1. Logging in as brand user...")
    login_data = {
        "username": "testbrand@example.com",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(
            f"{API_BASE}/login/access-token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Get current user info
    print("\n2. Getting current user info...")
    try:
        user_response = requests.get(
            f"{API_BASE}/login/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if user_response.status_code != 200:
            print(f"❌ Failed to get user info: {user_response.status_code}")
            print(f"Response: {user_response.text}")
            return
        
        user_data = user_response.json()
        print(f"✅ User info retrieved: {user_data['email']} (Brand ID: {user_data.get('brand_id')})")
        
        if not user_data.get('brand_id'):
            print("❌ User is not associated with any brand")
            return
            
        brand_id = user_data['brand_id']
        
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return
    
    # Step 3: Get current brand info
    print(f"\n3. Getting current brand info (Brand ID: {brand_id})...")
    try:
        brand_response = requests.get(
            f"{API_BASE}/brands/{brand_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if brand_response.status_code != 200:
            print(f"❌ Failed to get brand info: {brand_response.status_code}")
            print(f"Response: {brand_response.text}")
            return
        
        brand_data = brand_response.json()
        print(f"✅ Current brand: {brand_data['name']}")
        print(f"   Support Email: {brand_data['support_email']}")
        print(f"   Industry: {brand_data.get('industry', 'Not set')}")
        
    except Exception as e:
        print(f"❌ Error getting brand info: {e}")
        return
    
    # Step 4: Update brand profile
    print(f"\n4. Updating brand profile...")
    update_data = {
        "name": f"{brand_data['name']} (Updated)",
        "support_email": "updated-support@example.com",
        "industry": "Technology",
        "logo_url": "https://example.com/updated-logo.png"
    }
    
    try:
        update_response = requests.put(
            f"{API_BASE}/brands/{brand_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if update_response.status_code != 200:
            print(f"❌ Failed to update brand: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return
        
        updated_brand = update_response.json()
        print("✅ Brand profile updated successfully!")
        print(f"   New name: {updated_brand['name']}")
        print(f"   New support email: {updated_brand['support_email']}")
        print(f"   New industry: {updated_brand.get('industry')}")
        print(f"   New logo URL: {updated_brand.get('logo_url')}")
        
    except Exception as e:
        print(f"❌ Error updating brand: {e}")
        return
    
    # Step 5: Verify the update
    print(f"\n5. Verifying the update...")
    try:
        verify_response = requests.get(
            f"{API_BASE}/brands/{brand_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Failed to verify update: {verify_response.status_code}")
            return
        
        verified_brand = verify_response.json()
        if (verified_brand['name'] == update_data['name'] and 
            verified_brand['support_email'] == update_data['support_email']):
            print("✅ Update verified successfully!")
        else:
            print("❌ Update verification failed - data doesn't match")
            
    except Exception as e:
        print(f"❌ Error verifying update: {e}")
        return
    
    print("\n🎉 Brand profile update test completed successfully!")

if __name__ == "__main__":
    test_brand_profile_update() 