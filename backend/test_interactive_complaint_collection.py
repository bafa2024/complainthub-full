#!/usr/bin/env python3
"""
Test script for Interactive Complaint Collection with multiple connectors
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
BRAND_EMAIL = "brand@example.com"
BRAND_PASSWORD = "brand123"

def test_twilio_interactive_complaint_collection():
    """Test Twilio Interactive Complaint Collection"""
    print("=== Testing Twilio Interactive Complaint Collection ===")
    
    # Test voice call webhook
    voice_call_data = {
        "From": "+1234567890",
        "To": "+0987654321",
        "CallSid": "test_call_sid_123",
        "CallStatus": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/twilio",
            data=voice_call_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio voice call webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio voice call webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio voice call webhook - Error: {e}")
    
    # Test SMS webhook
    sms_data = {
        "From": "+1234567890",
        "To": "+0987654321",
        "Body": "I have a complaint about your service",
        "MessageSid": "test_message_sid_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/twilio",
            data=sms_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio SMS webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio SMS webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio SMS webhook - Error: {e}")
    
    # Test WhatsApp webhook
    whatsapp_data = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321",
        "Body": "I have a complaint about your service",
        "MessageSid": "test_whatsapp_sid_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/twilio",
            data=whatsapp_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio WhatsApp webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio WhatsApp webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio WhatsApp webhook - Error: {e}")

def test_knowlarity_interactive_complaint_collection():
    """Test Knowlarity Interactive Complaint Collection"""
    print("\n=== Testing Knowlarity Interactive Complaint Collection ===")
    
    # Test voice call webhook
    voice_call_data = {
        "from": "+919876543210",
        "to": "+911800123456",
        "call_id": "knowlarity_call_123",
        "status": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/knowlarity",
            json=voice_call_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity voice call webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity voice call webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity voice call webhook - Error: {e}")
    
    # Test SMS webhook
    sms_data = {
        "from": "+919876543210",
        "to": "+911800123456",
        "message": "I have a complaint about your service",
        "message_id": "knowlarity_msg_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/knowlarity",
            json=sms_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity SMS webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity SMS webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity SMS webhook - Error: {e}")
    
    # Test connection
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/knowlarity/test",
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Knowlarity connection test - Success")
            else:
                print(f"❌ Knowlarity connection test - Failed: {result.get('error')}")
        else:
            print(f"❌ Knowlarity connection test - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity connection test - Error: {e}")

def test_exotel_interactive_complaint_collection():
    """Test Exotel Interactive Complaint Collection"""
    print("\n=== Testing Exotel Interactive Complaint Collection ===")
    
    # Test voice call webhook
    voice_call_data = {
        "From": "+919876543210",
        "To": "+911800123456",
        "CallSid": "exotel_call_123",
        "CallStatus": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/exotel",
            data=voice_call_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel voice call webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel voice call webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel voice call webhook - Error: {e}")
    
    # Test SMS webhook
    sms_data = {
        "From": "+919876543210",
        "To": "+911800123456",
        "Body": "I have a complaint about your service",
        "MessageSid": "exotel_msg_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/exotel",
            data=sms_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel SMS webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel SMS webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel SMS webhook - Error: {e}")
    
    # Test connection
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/exotel/test",
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Exotel connection test - Success")
            else:
                print(f"❌ Exotel connection test - Failed: {result.get('error')}")
        else:
            print(f"❌ Exotel connection test - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel connection test - Error: {e}")

def test_whatsapp_interactive_complaint_collection():
    """Test WhatsApp Interactive Complaint Collection"""
    print("\n=== Testing WhatsApp Interactive Complaint Collection ===")
    
    # Test WhatsApp webhook (Twilio format)
    whatsapp_data = {
        "From": "whatsapp:+919876543210",
        "To": "whatsapp:+911800123456",
        "Body": "I have a complaint about your service",
        "MessageSid": "whatsapp_msg_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/whatsapp",
            data=whatsapp_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp webhook - Error: {e}")
    
    # Test WhatsApp Business API format
    whatsapp_business_data = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "911800123456",
                                "phone_number_id": "987654321"
                            },
                            "messages": [
                                {
                                    "from": "919876543210",
                                    "id": "msg_123",
                                    "timestamp": "1234567890",
                                    "text": {
                                        "body": "I have a complaint about your service"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/whatsapp",
            json=whatsapp_business_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp Business API webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp Business API webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp Business API webhook - Error: {e}")

def test_telegram_interactive_complaint_collection():
    """Test Telegram Interactive Complaint Collection"""
    print("\n=== Testing Telegram Interactive Complaint Collection ===")
    
    # Test Telegram webhook
    telegram_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {
                "id": 987654321,
                "first_name": "John",
                "username": "john_doe"
            },
            "chat": {
                "id": 987654321,
                "type": "private"
            },
            "text": "I have a complaint about your service"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/telegram",
            json=telegram_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Telegram webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Telegram webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram webhook - Error: {e}")

def test_outbound_communications():
    """Test outbound communications via different channels"""
    print("\n=== Testing Outbound Communications ===")
    
    # Test Knowlarity SMS
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/knowlarity/send-sms",
            json={
                "to_number": "+919876543210",
                "message": "Thank you for your complaint. We are working on it."
            },
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Knowlarity SMS sending - Success")
            else:
                print(f"❌ Knowlarity SMS sending - Failed: {result.get('error')}")
        else:
            print(f"❌ Knowlarity SMS sending - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity SMS sending - Error: {e}")
    
    # Test Exotel SMS
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/exotel/send-sms",
            json={
                "to_number": "+919876543210",
                "message": "Thank you for your complaint. We are working on it."
            },
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Exotel SMS sending - Success")
            else:
                print(f"❌ Exotel SMS sending - Failed: {result.get('error')}")
        else:
            print(f"❌ Exotel SMS sending - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel SMS sending - Error: {e}")
    
    # Test Knowlarity outbound call
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/knowlarity/make-call",
            json={
                "to_number": "+919876543210",
                "message": "Hello, we are calling to follow up on your complaint."
            },
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Knowlarity outbound call - Success")
            else:
                print(f"❌ Knowlarity outbound call - Failed: {result.get('error')}")
        else:
            print(f"❌ Knowlarity outbound call - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity outbound call - Error: {e}")
    
    # Test Exotel outbound call
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/channels/exotel/make-call",
            json={
                "to_number": "+919876543210",
                "message": "Hello, we are calling to follow up on your complaint."
            },
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Exotel outbound call - Success")
            else:
                print(f"❌ Exotel outbound call - Failed: {result.get('error')}")
        else:
            print(f"❌ Exotel outbound call - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel outbound call - Error: {e}")

def test_interactive_voice_response():
    """Test Interactive Voice Response (IVR) functionality"""
    print("\n=== Testing Interactive Voice Response ===")
    
    # Test Knowlarity IVR
    try:
        knowlarity_adapter = KnowlarityAdapter()
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        ivr_response = knowlarity_adapter.create_interactive_voice_response(options)
        print("✅ Knowlarity IVR creation - Success")
        print(f"   IVR Response: {ivr_response[:100]}...")
        
        # Test menu selection
        menu_response = knowlarity_adapter.handle_menu_selection("1", options)
        print("✅ Knowlarity IVR menu selection - Success")
        print(f"   Menu Response: {menu_response[:100]}...")
        
    except Exception as e:
        print(f"❌ Knowlarity IVR - Error: {e}")
    
    # Test Exotel IVR
    try:
        exotel_adapter = ExotelAdapter()
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        ivr_response = exotel_adapter.create_interactive_voice_response(options)
        print("✅ Exotel IVR creation - Success")
        print(f"   IVR Response: {ivr_response[:100]}...")
        
        # Test menu selection
        menu_response = exotel_adapter.handle_menu_selection("2", options)
        print("✅ Exotel IVR menu selection - Success")
        print(f"   Menu Response: {menu_response[:100]}...")
        
    except Exception as e:
        print(f"❌ Exotel IVR - Error: {e}")

def get_admin_token():
    """Get admin authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Failed to get admin token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting admin token: {e}")
        return None

def main():
    """Run all Interactive Complaint Collection tests"""
    print("Starting Interactive Complaint Collection Tests")
    print("=" * 60)
    
    # Test Twilio Interactive Complaint Collection
    test_twilio_interactive_complaint_collection()
    
    # Test Knowlarity Interactive Complaint Collection
    test_knowlarity_interactive_complaint_collection()
    
    # Test Exotel Interactive Complaint Collection
    test_exotel_interactive_complaint_collection()
    
    # Test WhatsApp Interactive Complaint Collection
    test_whatsapp_interactive_complaint_collection()
    
    # Test Telegram Interactive Complaint Collection
    test_telegram_interactive_complaint_collection()
    
    # Test outbound communications
    test_outbound_communications()
    
    # Test Interactive Voice Response
    test_interactive_voice_response()
    
    print("\n" + "=" * 60)
    print("Interactive Complaint Collection Tests Completed")

if __name__ == "__main__":
    main() 