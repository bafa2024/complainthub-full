#!/usr/bin/env python3
"""
Test script for chat/message webhook endpoints with /webhook/chat/{channel} handlers
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def test_whatsapp_chat_webhook():
    """Test WhatsApp chat webhook endpoints"""
    print("=== Testing WhatsApp Chat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321",
        "Body": "I have a complaint about your service",
        "MessageSid": "whatsapp_msg_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/whatsapp",
            data=chat_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp chat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp chat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp chat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321",
        "MediaUrl0": "https://example.com/image.jpg",
        "MediaContentType0": "image/jpeg",
        "MessageSid": "whatsapp_msg_123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/whatsapp/media",
            data=media_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "MessageSid": "whatsapp_msg_123",
        "MessageStatus": "delivered"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/whatsapp/status",
            data=status_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "From": "whatsapp:+1234567890",
        "To": "whatsapp:+0987654321"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/whatsapp/typing",
            data=typing_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            print("✅ WhatsApp typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WhatsApp typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp typing webhook - Error: {e}")

def test_telegram_chat_webhook():
    """Test Telegram chat webhook endpoints"""
    print("\n=== Testing Telegram Chat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
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
            f"{BASE_URL}/api/v1/webhook/chat/telegram",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Telegram chat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Telegram chat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram chat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 124,
            "from": {
                "id": 987654321,
                "first_name": "John"
            },
            "chat": {
                "id": 987654321,
                "type": "private"
            },
            "photo": [
                {
                    "file_id": "photo_123",
                    "file_size": 1024
                }
            ],
            "caption": "Screenshot of the issue"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/telegram/media",
            json=media_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Telegram media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Telegram media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 123,
            "from": {"id": 987654321},
            "chat": {"id": 987654321}
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/telegram/status",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Telegram status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Telegram status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "update_id": 123456789,
        "message": {
            "from": {"id": 987654321},
            "chat": {"id": 987654321}
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/telegram/typing",
            json=typing_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Telegram typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Telegram typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram typing webhook - Error: {e}")

def test_instagram_chat_webhook():
    """Test Instagram chat webhook endpoints"""
    print("\n=== Testing Instagram Chat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
        "object": "instagram",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "timestamp": 1234567890000,
                        "message": {
                            "mid": "mid.123456789",
                            "text": "I have a complaint about your service"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/instagram",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Instagram chat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Instagram chat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Instagram chat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "object": "instagram",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "timestamp": 1234567890000,
                        "message": {
                            "mid": "mid.123456789",
                            "attachments": [
                                {
                                    "type": "image",
                                    "payload": {
                                        "url": "https://example.com/image.jpg"
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
            f"{BASE_URL}/api/v1/webhook/chat/instagram/media",
            json=media_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Instagram media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Instagram media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Instagram media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "object": "instagram",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "delivery": {
                            "mids": ["mid.123456789"],
                            "watermark": 1234567890000
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/instagram/status",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Instagram status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Instagram status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Instagram status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "object": "instagram",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "sender_action": "typing_on"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/instagram/typing",
            json=typing_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Instagram typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Instagram typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Instagram typing webhook - Error: {e}")

def test_facebook_chat_webhook():
    """Test Facebook chat webhook endpoints"""
    print("\n=== Testing Facebook Chat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "timestamp": 1234567890000,
                        "message": {
                            "mid": "mid.123456789",
                            "text": "I have a complaint about your service"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/facebook",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Facebook chat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Facebook chat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Facebook chat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "timestamp": 1234567890000,
                        "message": {
                            "mid": "mid.123456789",
                            "attachments": [
                                {
                                    "type": "image",
                                    "payload": {
                                        "url": "https://example.com/image.jpg"
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
            f"{BASE_URL}/api/v1/webhook/chat/facebook/media",
            json=media_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Facebook media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Facebook media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Facebook media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "delivery": {
                            "mids": ["mid.123456789"],
                            "watermark": 1234567890000
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/facebook/status",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Facebook status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Facebook status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Facebook status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": 1234567890,
                "messaging": [
                    {
                        "sender": {"id": "987654321"},
                        "recipient": {"id": "123456789"},
                        "sender_action": "typing_on"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/facebook/typing",
            json=typing_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Facebook typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ Facebook typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Facebook typing webhook - Error: {e}")

def test_linkedin_chat_webhook():
    """Test LinkedIn chat webhook endpoints"""
    print("\n=== Testing LinkedIn Chat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
        "message": {
            "id": "linkedin_msg_123",
            "from": {"id": "987654321"},
            "text": "I have a complaint about your service"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/linkedin",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ LinkedIn chat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ LinkedIn chat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LinkedIn chat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "message": {
            "id": "linkedin_msg_124",
            "from": {"id": "987654321"},
            "attachments": [
                {
                    "type": "image",
                    "url": "https://example.com/image.jpg"
                }
            ]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/linkedin/media",
            json=media_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ LinkedIn media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ LinkedIn media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LinkedIn media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "message": {
            "id": "linkedin_msg_123",
            "from": {"id": "987654321"},
            "status": "delivered"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/linkedin/status",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ LinkedIn status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ LinkedIn status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LinkedIn status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "message": {
            "from": {"id": "987654321"},
            "typing": True
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/linkedin/typing",
            json=typing_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ LinkedIn typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ LinkedIn typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ LinkedIn typing webhook - Error: {e}")

def test_webchat_webhook():
    """Test WebChat webhook endpoints"""
    print("\n=== Testing WebChat Webhook Endpoints ===")
    
    # Test main chat webhook
    chat_data = {
        "session_id": "webchat_session_123",
        "message": "I have a complaint about your service",
        "user_id": "user_123",
        "user_name": "John Doe",
        "brand_id": 1
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/webchat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ WebChat webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WebChat webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebChat webhook - Error: {e}")
    
    # Test media webhook
    media_data = {
        "session_id": "webchat_session_123",
        "message": "Screenshot of the issue",
        "user_id": "user_123",
        "user_name": "John Doe",
        "brand_id": 1,
        "file_upload": {
            "name": "screenshot.png",
            "type": "image/png",
            "size": 1024,
            "url": "https://example.com/file.png"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/webchat/media",
            json=media_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ WebChat media webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WebChat media webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebChat media webhook - Error: {e}")
    
    # Test status webhook
    status_data = {
        "session_id": "webchat_session_123",
        "user_id": "user_123",
        "status": "online"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/webchat/status",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ WebChat status webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WebChat status webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebChat status webhook - Error: {e}")
    
    # Test typing webhook
    typing_data = {
        "session_id": "webchat_session_123",
        "user_id": "user_123",
        "typing": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/webchat/typing",
            json=typing_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ WebChat typing webhook - Success")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"❌ WebChat typing webhook - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WebChat typing webhook - Error: {e}")

def test_chat_webhook_validation():
    """Test chat webhook validation and error handling"""
    print("\n=== Testing Chat Webhook Validation ===")
    
    # Test unsupported channel
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/unsupported",
            json={"test": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print("✅ Unsupported channel validation - Success")
        else:
            print(f"❌ Unsupported channel validation - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Unsupported channel validation - Error: {e}")
    
    # Test invalid data format
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/whatsapp",
            data={"invalid": "data"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code in [200, 400, 500]:
            print("✅ Invalid data format handling - Success")
        else:
            print(f"❌ Invalid data format handling - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Invalid data format handling - Error: {e}")

def test_chat_webhook_integration():
    """Test chat webhook integration with conversation manager"""
    print("\n=== Testing Chat Webhook Integration ===")
    
    # Test complete chat flow
    chat_flow_data = {
        "session_id": "integration_test_123",
        "message": "I have a complaint about your service quality",
        "user_id": "user_123",
        "user_name": "John Doe",
        "brand_id": 1
    }
    
    try:
        # Step 1: Initial message
        response1 = requests.post(
            f"{BASE_URL}/api/v1/webhook/chat/webchat",
            json=chat_flow_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code == 200:
            print("✅ Chat flow - Initial message successful")
            
            # Step 2: Media upload
            media_data = {
                "session_id": "integration_test_123",
                "message": "Here's a screenshot",
                "user_id": "user_123",
                "user_name": "John Doe",
                "brand_id": 1,
                "file_upload": {
                    "name": "screenshot.png",
                    "type": "image/png",
                    "size": 1024,
                    "url": "https://example.com/file.png"
                }
            }
            
            response2 = requests.post(
                f"{BASE_URL}/api/v1/webhook/chat/webchat/media",
                json=media_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response2.status_code == 200:
                print("✅ Chat flow - Media upload successful")
                
                # Step 3: Status update
                status_data = {
                    "session_id": "integration_test_123",
                    "user_id": "user_123",
                    "status": "online"
                }
                
                response3 = requests.post(
                    f"{BASE_URL}/api/v1/webhook/chat/webchat/status",
                    json=status_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response3.status_code == 200:
                    print("✅ Chat flow - Status update successful")
                    print("✅ Complete chat flow - Success")
                else:
                    print(f"❌ Chat flow - Status update failed: {response3.status_code}")
            else:
                print(f"❌ Chat flow - Media upload failed: {response2.status_code}")
        else:
            print(f"❌ Chat flow - Initial message failed: {response1.status_code}")
            
    except Exception as e:
        print(f"❌ Chat flow - Error: {e}")

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
    """Run all chat webhook tests"""
    print("Starting Chat Webhook Tests")
    print("=" * 60)
    
    # Test WhatsApp chat webhook endpoints
    test_whatsapp_chat_webhook()
    
    # Test Telegram chat webhook endpoints
    test_telegram_chat_webhook()
    
    # Test Instagram chat webhook endpoints
    test_instagram_chat_webhook()
    
    # Test Facebook chat webhook endpoints
    test_facebook_chat_webhook()
    
    # Test LinkedIn chat webhook endpoints
    test_linkedin_chat_webhook()
    
    # Test WebChat webhook endpoints
    test_webchat_webhook()
    
    # Test validation and error handling
    test_chat_webhook_validation()
    
    # Test integration with conversation manager
    test_chat_webhook_integration()
    
    print("\n" + "=" * 60)
    print("Chat Webhook Tests Completed")

if __name__ == "__main__":
    main() 