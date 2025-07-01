#!/usr/bin/env python3
"""
Test frontend authentication flow
"""

import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_frontend_auth_flow():
    print("🧪 Testing Frontend Authentication Flow")
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
            print(login_response.text)
            return False
            
        login_result = login_response.json()
        token = login_result.get("access_token")
        print(f"✅ Login successful, token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get current user info
    print("\n2. Getting current user info...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        user_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if user_response.status_code != 200:
            print(f"❌ Get user failed: {user_response.status_code}")
            print(user_response.text)
            return False
            
        user_data = user_response.json()
        print(f"✅ User info: {user_data.get('email')} (Role: {user_data.get('role')})")
        print(f"   Brand ID: {user_data.get('brand_id')}")
        
    except Exception as e:
        print(f"❌ Get user error: {e}")
        return False
    
    # Step 3: Get tickets for this brand
    print("\n3. Getting tickets...")
    try:
        tickets_response = requests.get(f"{API_BASE}/tickets/", headers=headers)
        if tickets_response.status_code != 200:
            print(f"❌ Get tickets failed: {tickets_response.status_code}")
            print(tickets_response.text)
            return False
            
        tickets = tickets_response.json()
        print(f"✅ Found {len(tickets)} tickets")
        
        if not tickets:
            print("❌ No tickets found for this brand")
            return False
            
        test_ticket = tickets[0]
        ticket_id = test_ticket.get("id")
        print(f"   Test ticket ID: {ticket_id}")
        print(f"   Title: {test_ticket.get('title')}")
        print(f"   Status: {test_ticket.get('status')}")
        
    except Exception as e:
        print(f"❌ Get tickets error: {e}")
        return False
    
    # Step 4: Update ticket status (simulating frontend request)
    print("\n4. Updating ticket status...")
    update_data = {"status": "in-progress"}
    
    try:
        update_response = requests.patch(
            f"{API_BASE}/tickets/{ticket_id}",
            json=update_data,
            headers=headers
        )
        
        print(f"Response status: {update_response.status_code}")
        print(f"Response headers: {dict(update_response.headers)}")
        
        if update_response.status_code == 200:
            result = update_response.json()
            print(f"✅ Ticket updated successfully!")
            print(f"   New status: {result.get('status')}")
            return True
        else:
            print(f"❌ Update failed: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_auth_flow()
    if success:
        print("\n🎉 Frontend auth flow test completed successfully!")
    else:
        print("\n❌ Frontend auth flow test failed!") 