#!/usr/bin/env python3
"""
Test script for voice complaint feature
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_BRAND_ID = 1

def create_test_user():
    """Create a test user if it doesn't exist"""
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    # Try to login first
    response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
    if response.status_code == 200:
        print("✓ Test user already exists and can login")
        return response.json()["access_token"]
    
    # Create new user
    user_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 200:
        print("✓ Test user created successfully")
        # Login to get token
        response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
    
    print("✗ Failed to create/login test user")
    return None

def test_voice_complaint_submission(token):
    """Test voice complaint submission"""
    print("\n=== Testing Voice Complaint Submission ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "multipart/form-data"
    }
    
    # Create test metadata
    metadata = {
        "title": "Test Voice Complaint",
        "description": "This is a test voice complaint description",
        "category": "technical",
        "priority": "medium",
        "type": "complaint",
        "brand_id": TEST_BRAND_ID,
        "contact_preference": "email",
        "allow_contact": True
    }
    
    # Create a dummy audio file
    audio_content = b"dummy audio content for testing"
    
    # Prepare form data
    files = {
        'audio': ('test-audio.wav', audio_content, 'audio/wav'),
        'metadata': (None, json.dumps(metadata), 'application/json')
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/tickets_extended/voice",
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Voice complaint submitted successfully")
            print(f"  Ticket ID: {data.get('ticket_id')}")
            print(f"  Transcript: {data.get('transcript')}")
            print(f"  Category: {data.get('category')}")
            return data.get('ticket_id')
        else:
            print("✗ Voice complaint submission failed")
            return None
            
    except Exception as e:
        print(f"✗ Error during voice complaint submission: {e}")
        return None

def test_ticket_retrieval(token, ticket_id):
    """Test that the ticket can be retrieved"""
    print("\n=== Testing Ticket Retrieval ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test user tickets endpoint
        response = requests.get(f"{BASE_URL}/tickets/", headers=headers)
        print(f"User tickets response status: {response.status_code}")
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"✓ Found {len(tickets)} tickets for user")
            
            # Check if our ticket is in the list
            our_ticket = next((t for t in tickets if t.get('id') == ticket_id), None)
            if our_ticket:
                print("✓ Our voice complaint ticket found in user tickets")
                print(f"  Title: {our_ticket.get('title')}")
                print(f"  Status: {our_ticket.get('status')}")
                print(f"  Channel: {our_ticket.get('channel')}")
            else:
                print("✗ Our voice complaint ticket not found in user tickets")
        
        # Test specific ticket endpoint
        response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
        print(f"Specific ticket response status: {response.status_code}")
        
        if response.status_code == 200:
            ticket = response.json()
            print("✓ Specific ticket retrieved successfully")
            print(f"  Title: {ticket.get('title')}")
            print(f"  Description: {ticket.get('description')}")
            print(f"  Voice recording URL: {ticket.get('voice_recording_url')}")
            print(f"  Transcript: {ticket.get('transcript')}")
        else:
            print("✗ Failed to retrieve specific ticket")
            
    except Exception as e:
        print(f"✗ Error during ticket retrieval: {e}")

def test_brand_ticket_access(token, ticket_id):
    """Test that brand users can access the ticket"""
    print("\n=== Testing Brand Ticket Access ===")
    
    # First, create a brand user
    brand_user_data = {
        "email": "branduser@example.com",
        "password": "brandpass123",
        "full_name": "Brand User",
        "role": "brand_user",
        "brand_id": TEST_BRAND_ID
    }
    
    try:
        # Create brand user
        response = requests.post(f"{BASE_URL}/users/", json=brand_user_data)
        if response.status_code != 200:
            print("✗ Failed to create brand user")
            return
        
        # Login as brand user
        login_data = {
            "username": "branduser@example.com",
            "password": "brandpass123"
        }
        response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
        if response.status_code != 200:
            print("✗ Failed to login as brand user")
            return
        
        brand_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {brand_token}"}
        
        # Test brand tickets endpoint
        response = requests.get(f"{BASE_URL}/tickets/", headers=headers)
        print(f"Brand tickets response status: {response.status_code}")
        
        if response.status_code == 200:
            tickets = response.json()
            print(f"✓ Found {len(tickets)} tickets for brand")
            
            # Check if our ticket is in the brand's list
            our_ticket = next((t for t in tickets if t.get('id') == ticket_id), None)
            if our_ticket:
                print("✓ Our voice complaint ticket found in brand tickets")
            else:
                print("✗ Our voice complaint ticket not found in brand tickets")
        
        # Test specific ticket access
        response = requests.get(f"{BASE_URL}/tickets/{ticket_id}", headers=headers)
        print(f"Brand specific ticket response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Brand user can access the specific ticket")
        else:
            print("✗ Brand user cannot access the specific ticket")
            
    except Exception as e:
        print(f"✗ Error during brand ticket access test: {e}")

def main():
    """Main test function"""
    print("=== Voice Complaint Feature Test ===")
    print(f"Testing against: {BASE_URL}")
    
    # Test 1: Create/Login user
    token = create_test_user()
    if not token:
        print("✗ Cannot proceed without valid user token")
        return
    
    # Test 2: Submit voice complaint
    ticket_id = test_voice_complaint_submission(token)
    if not ticket_id:
        print("✗ Cannot proceed without successful ticket creation")
        return
    
    # Test 3: Verify ticket retrieval
    test_ticket_retrieval(token, ticket_id)
    
    # Test 4: Verify brand access
    test_brand_ticket_access(token, ticket_id)
    
    print("\n=== Test Summary ===")
    print("Voice complaint feature test completed!")

if __name__ == "__main__":
    main() 