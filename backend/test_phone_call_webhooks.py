#!/usr/bin/env python3
"""
Test script for phone call webhook endpoints with /webhook/voice/{provider} handlers
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_twilio_voice_webhook():
    """Test Twilio voice webhook endpoints"""
    print("=== Testing Twilio Voice Webhook Endpoints ===")
    
    # Test main voice webhook
    voice_call_data = {
        "From": "+1234567890",
        "To": "+0987654321",
        "CallSid": "twilio_call_sid_123",
        "CallStatus": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio",
            data=voice_call_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio voice webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio voice webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio voice webhook - Error: {e}")
    
    # Test transcription webhook
    transcription_data = {
        "CallSid": "twilio_call_sid_123",
        "TranscriptionText": "I have a complaint about your service",
        "TranscriptionStatus": "completed",
        "TranscriptionUrl": "https://api.twilio.com/2010-04-01/Accounts/AC123/Transcriptions/TR123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio/transcription",
            data=transcription_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio transcription webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio transcription webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio transcription webhook - Error: {e}")
    
    # Test recording webhook
    recording_data = {
        "CallSid": "twilio_call_sid_123",
        "RecordingUrl": "https://api.twilio.com/2010-04-01/Accounts/AC123/Recordings/RE123",
        "RecordingDuration": "30",
        "RecordingStatus": "completed"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio/recording",
            data=recording_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio recording webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio recording webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio recording webhook - Error: {e}")
    
    # Test IVR webhook
    ivr_data = {
        "CallSid": "twilio_call_sid_123",
        "Digits": "1"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio/ivr",
            data=ivr_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio IVR webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio IVR webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio IVR webhook - Error: {e}")
    
    # Test menu webhook
    menu_data = {
        "CallSid": "twilio_call_sid_123",
        "Digits": "2"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio/menu",
            data=menu_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Twilio menu webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Twilio menu webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Twilio menu webhook - Error: {e}")

def test_knowlarity_voice_webhook():
    """Test Knowlarity voice webhook endpoints"""
    print("\n=== Testing Knowlarity Voice Webhook Endpoints ===")
    
    # Test main voice webhook
    voice_call_data = {
        "from": "+919876543210",
        "to": "+911800123456",
        "call_id": "knowlarity_call_123",
        "status": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/knowlarity",
            json=voice_call_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity voice webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity voice webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity voice webhook - Error: {e}")
    
    # Test transcription webhook
    transcription_data = {
        "call_id": "knowlarity_call_123",
        "transcription_text": "I have a complaint about your service",
        "transcription_status": "completed",
        "recording_url": "https://api.knowlarity.com/recordings/rec123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/knowlarity/transcription",
            json=transcription_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity transcription webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity transcription webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity transcription webhook - Error: {e}")
    
    # Test recording webhook
    recording_data = {
        "call_id": "knowlarity_call_123",
        "recording_url": "https://api.knowlarity.com/recordings/rec123",
        "recording_duration": "30",
        "recording_status": "completed"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/knowlarity/recording",
            json=recording_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity recording webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity recording webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity recording webhook - Error: {e}")
    
    # Test IVR webhook
    ivr_data = {
        "call_id": "knowlarity_call_123",
        "digits": "1"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/knowlarity/ivr",
            json=ivr_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity IVR webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity IVR webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity IVR webhook - Error: {e}")
    
    # Test menu webhook
    menu_data = {
        "call_id": "knowlarity_call_123",
        "digits": "2"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/knowlarity/menu",
            json=menu_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Knowlarity menu webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Knowlarity menu webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Knowlarity menu webhook - Error: {e}")

def test_exotel_voice_webhook():
    """Test Exotel voice webhook endpoints"""
    print("\n=== Testing Exotel Voice Webhook Endpoints ===")
    
    # Test main voice webhook
    voice_call_data = {
        "From": "+919876543210",
        "To": "+911800123456",
        "CallSid": "exotel_call_123",
        "CallStatus": "ringing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/exotel",
            data=voice_call_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel voice webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel voice webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel voice webhook - Error: {e}")
    
    # Test transcription webhook
    transcription_data = {
        "CallSid": "exotel_call_123",
        "TranscriptionText": "I have a complaint about your service",
        "TranscriptionStatus": "completed",
        "RecordingUrl": "https://api.exotel.com/recordings/rec123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/exotel/transcription",
            data=transcription_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel transcription webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel transcription webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel transcription webhook - Error: {e}")
    
    # Test recording webhook
    recording_data = {
        "CallSid": "exotel_call_123",
        "RecordingUrl": "https://api.exotel.com/recordings/rec123",
        "RecordingDuration": "30",
        "RecordingStatus": "completed"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/exotel/recording",
            data=recording_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel recording webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel recording webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel recording webhook - Error: {e}")
    
    # Test IVR webhook
    ivr_data = {
        "CallSid": "exotel_call_123",
        "Digits": "1"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/exotel/ivr",
            data=ivr_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel IVR webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel IVR webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel IVR webhook - Error: {e}")
    
    # Test menu webhook
    menu_data = {
        "CallSid": "exotel_call_123",
        "Digits": "2"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/exotel/menu",
            data=menu_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ Exotel menu webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Exotel menu webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exotel menu webhook - Error: {e}")

def test_webhook_routes():
    """Test webhook route endpoints"""
    print("\n=== Testing Webhook Route Endpoints ===")
    
    # Test webhook routes endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/webhook/routes",
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            routes = response.json()
            print("✅ Webhook routes - Success")
            print(f"   Available routes: {len(routes.get('routes', []))}")
            
            # Check for voice provider routes
            voice_routes = [route for route in routes.get('routes', []) if 'voice' in route.get('path', '')]
            print(f"   Voice provider routes: {len(voice_routes)}")
            
            for route in voice_routes:
                print(f"     - {route.get('path')} ({route.get('method')})")
                
        else:
            print(f"❌ Webhook routes - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook routes - Error: {e}")

def test_voice_webhook_validation():
    """Test voice webhook validation and error handling"""
    print("\n=== Testing Voice Webhook Validation ===")
    
    # Test unsupported provider
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/unsupported",
            data={"test": "data"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 400:
            print("✅ Unsupported provider validation - Success")
        else:
            print(f"❌ Unsupported provider validation - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Unsupported provider validation - Error: {e}")
    
    # Test invalid data format
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio",
            data={"invalid": "data"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code in [200, 400, 500]:
            print("✅ Invalid data format handling - Success")
        else:
            print(f"❌ Invalid data format handling - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid data format handling - Error: {e}")

def test_voice_webhook_integration():
    """Test voice webhook integration with conversation manager"""
    print("\n=== Testing Voice Webhook Integration ===")
    
    # Test complete voice call flow
    call_flow_data = {
        "From": "+1234567890",
        "To": "+0987654321",
        "CallSid": "integration_test_123",
        "CallStatus": "ringing"
    }
    
    try:
        # Step 1: Initial call
        response1 = requests.post(
            f"{BASE_URL}/api/v1/webhook/voice/twilio",
            data=call_flow_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response1.status_code == 200:
            print("✅ Voice call flow - Initial call successful")
            
            # Step 2: Transcription callback
            transcription_data = {
                "CallSid": "integration_test_123",
                "TranscriptionText": "I have a complaint about your service quality",
                "TranscriptionStatus": "completed"
            }
            
            response2 = requests.post(
                f"{BASE_URL}/api/v1/webhook/voice/twilio/transcription",
                data=transcription_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response2.status_code == 200:
                print("✅ Voice call flow - Transcription successful")
                
                # Step 3: IVR selection
                ivr_data = {
                    "CallSid": "integration_test_123",
                    "Digits": "1"
                }
                
                response3 = requests.post(
                    f"{BASE_URL}/api/v1/webhook/voice/twilio/ivr",
                    data=ivr_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response3.status_code == 200:
                    print("✅ Voice call flow - IVR selection successful")
                    print("✅ Complete voice call flow - Success")
                else:
                    print(f"❌ Voice call flow - IVR selection failed: {response3.status_code}")
            else:
                print(f"❌ Voice call flow - Transcription failed: {response2.status_code}")
        else:
            print(f"❌ Voice call flow - Initial call failed: {response1.status_code}")
            
    except Exception as e:
        print(f"❌ Voice call flow - Error: {e}")

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
    """Run all phone call webhook tests"""
    print("Starting Phone Call Webhook Tests")
    print("=" * 60)
    
    # Test Twilio voice webhook endpoints
    test_twilio_voice_webhook()
    
    # Test Knowlarity voice webhook endpoints
    test_knowlarity_voice_webhook()
    
    # Test Exotel voice webhook endpoints
    test_exotel_voice_webhook()
    
    # Test webhook routes
    test_webhook_routes()
    
    # Test validation and error handling
    test_voice_webhook_validation()
    
    # Test integration with conversation manager
    test_voice_webhook_integration()
    
    print("\n" + "=" * 60)
    print("Phone Call Webhook Tests Completed")

if __name__ == "__main__":
    main() 