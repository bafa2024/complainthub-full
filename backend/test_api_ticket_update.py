#!/usr/bin/env python3
"""
Test API ticket update functionality
"""

import requests
import json

def test_api_ticket_update():
    """Test the API endpoint for ticket updates"""
    
    print("🧪 Testing API Ticket Update")
    print("=" * 50)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    API_BASE = f"{BASE_URL}/api/v1"
    
    # Step 1: Login as brand user
    print("\n1. Logging in as brand user...")
    login_data = {
        "username": "testbrand@example.com",
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
    
    # Step 2: Get tickets for the brand user
    print("\n2. Getting tickets...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        tickets_response = requests.get(f"{API_BASE}/tickets/", headers=headers)
        if tickets_response.status_code != 200:
            print(f"❌ Getting tickets failed: {tickets_response.status_code}")
            print(tickets_response.text)
            return False
        
        tickets = tickets_response.json()
        if not tickets:
            print("❌ No tickets found")
            return False
        
        test_ticket = tickets[0]
        ticket_id = test_ticket.get("id")
        print(f"✅ Found ticket ID: {ticket_id}")
        print(f"   Title: {test_ticket.get('title')}")
        print(f"   Current status: {test_ticket.get('status')}")
        
    except Exception as e:
        print(f"❌ Getting tickets error: {e}")
        return False
    
    # Step 3: Update ticket status
    print("\n3. Updating ticket status...")
    update_data = {
        "status": "in-progress"
    }
    
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
    success = test_api_ticket_update()
    if success:
        print("\n🎉 API test completed successfully!")
    else:
        print("\n❌ API test failed!") 