#!/usr/bin/env python3
"""
Test script for team invitation functionality
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_team_invitation():
    """Test the complete team invitation flow"""
    
    print("🧪 Testing Team Invitation Functionality")
    print("=" * 50)
    
    # Step 1: Login as a brand user to get access token
    print("\n1. Logging in as brand user...")
    login_data = {
        "username": "brand@example.com",  # Use existing brand user
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return False
        
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Create a team invitation
    print("\n2. Creating team invitation...")
    headers = {"Authorization": f"Bearer {access_token}"}
    invitation_data = {
        "email": "newteam@example.com",
        "role": "brand_user"
    }
    
    try:
        # Get brand ID from user info or use default
        brand_id = 1  # Assuming brand ID 1 exists
        
        invite_response = requests.post(
            f"{API_BASE}/brands/{brand_id}/invitations",
            json=invitation_data,
            headers=headers
        )
        
        if invite_response.status_code != 200:
            print(f"❌ Invitation creation failed: {invite_response.status_code}")
            print(invite_response.text)
            return False
        
        invitation_result = invite_response.json()
        invitation_id = invitation_result.get("id")
        invitation_token = invitation_result.get("invitation_token")
        
        print(f"✅ Invitation created successfully (ID: {invitation_id})")
        print(f"   Token: {invitation_token}")
        
    except Exception as e:
        print(f"❌ Invitation creation error: {e}")
        return False
    
    # Step 3: Get invitation details by token (public endpoint)
    print("\n3. Getting invitation details...")
    try:
        details_response = requests.get(f"{API_BASE}/brands/invitations/{invitation_token}")
        
        if details_response.status_code != 200:
            print(f"❌ Getting invitation details failed: {details_response.status_code}")
            print(details_response.text)
            return False
        
        details = details_response.json()
        print(f"✅ Invitation details retrieved:")
        print(f"   Email: {details.get('email')}")
        print(f"   Role: {details.get('role')}")
        print(f"   Brand: {details.get('brand_name')}")
        
    except Exception as e:
        print(f"❌ Getting invitation details error: {e}")
        return False
    
    # Step 4: Accept invitation (public endpoint)
    print("\n4. Accepting invitation...")
    accept_data = {
        "full_name": "New Team Member",
        "password": "newpassword123",
        "phone_number": "+1234567890"
    }
    
    try:
        accept_response = requests.post(
            f"{API_BASE}/brands/invitations/{invitation_token}/accept",
            json=accept_data
        )
        
        if accept_response.status_code != 200:
            print(f"❌ Accepting invitation failed: {accept_response.status_code}")
            print(accept_response.text)
            return False
        
        accept_result = accept_response.json()
        user_id = accept_result.get("user_id")
        
        print(f"✅ Invitation accepted successfully (User ID: {user_id})")
        
    except Exception as e:
        print(f"❌ Accepting invitation error: {e}")
        return False
    
    # Step 5: List invitations (should show accepted invitation)
    print("\n5. Listing invitations...")
    try:
        list_response = requests.get(
            f"{API_BASE}/brands/{brand_id}/invitations",
            headers=headers
        )
        
        if list_response.status_code != 200:
            print(f"❌ Listing invitations failed: {list_response.status_code}")
            print(list_response.text)
            return False
        
        invitations = list_response.json()
        print(f"✅ Found {len(invitations)} invitations")
        
        for inv in invitations:
            status = "Accepted" if inv.get("is_accepted") else "Pending"
            print(f"   - {inv.get('email')} ({status})")
        
    except Exception as e:
        print(f"❌ Listing invitations error: {e}")
        return False
    
    print("\n🎉 All tests passed! Team invitation functionality is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_team_invitation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 