#!/usr/bin/env python3
"""
Test script for CRM webhook processing and follow-up delivery edge case handling
"""

import requests
import json
import time
import hmac
import hashlib
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
BRAND_EMAIL = "brand@example.com"
BRAND_PASSWORD = "brand123"

def test_crm_webhook_processing():
    """Test CRM webhook processing for real-time updates"""
    print("=== Testing CRM Webhook Processing ===")
    
    # Test data for different CRM systems
    webhook_tests = [
        {
            "crm_type": "salesforce",
            "webhook_data": {
                "sobject": {
                    "Id": "5001234567890ABC",
                    "Status": "In Progress",
                    "Subject": "Updated Complaint Subject",
                    "Description": "Updated complaint description"
                }
            },
            "description": "Salesforce case update"
        },
        {
            "crm_type": "zoho",
            "webhook_data": {
                "ticket": {
                    "id": "12345",
                    "status": "Open",
                    "subject": "Zoho ticket update",
                    "description": "Updated ticket description"
                }
            },
            "description": "Zoho ticket update"
        },
        {
            "crm_type": "hubspot",
            "webhook_data": {
                "ticket": {
                    "id": "67890",
                    "hs_ticket_status": "New",
                    "subject": "HubSpot ticket update",
                    "content": "Updated ticket content"
                }
            },
            "description": "HubSpot ticket update"
        },
        {
            "crm_type": "pipedrive",
            "webhook_data": {
                "deal": {
                    "id": "11111",
                    "status": "open",
                    "title": "Pipedrive deal update",
                    "value": 1000
                }
            },
            "description": "Pipedrive deal update"
        }
    ]
    
    for test in webhook_tests:
        print(f"\nTesting {test['description']}...")
        
        try:
            # Send webhook
            response = requests.post(
                f"{BASE_URL}/api/v1/webhook/crm/{test['crm_type']}",
                params={"brand_id": 1},
                json=test['webhook_data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {test['description']} - Success: {result}")
            else:
                print(f"❌ {test['description']} - Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ {test['description']} - Error: {e}")

def test_webhook_signature_verification():
    """Test webhook signature verification"""
    print("\n=== Testing Webhook Signature Verification ===")
    
    webhook_data = {"test": "data"}
    secret = "test_secret"
    
    # Generate signature
    webhook_body = json.dumps(webhook_data)
    signature = hmac.new(
        secret.encode('utf-8'),
        webhook_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/webhook/crm/salesforce",
            params={"brand_id": 1},
            json=webhook_data,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": f"sha256={signature}"
            }
        )
        
        if response.status_code == 200:
            print("✅ Webhook signature verification - Success")
        else:
            print(f"❌ Webhook signature verification - Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook signature verification - Error: {e}")

def test_follow_up_delivery_edge_cases():
    """Test follow-up delivery edge cases and fallback mechanisms"""
    print("\n=== Testing Follow-up Delivery Edge Cases ===")
    
    # Test scenarios
    edge_cases = [
        {
            "scenario": "Voice delivery failure with WhatsApp fallback",
            "channel": "voice",
            "user_phone": "+1234567890",
            "user_email": "test@example.com",
            "description": "Test voice failure with WhatsApp fallback"
        },
        {
            "scenario": "WhatsApp delivery failure with SMS fallback",
            "channel": "whatsapp",
            "user_phone": "+1234567890",
            "user_email": "test@example.com",
            "description": "Test WhatsApp failure with SMS fallback"
        },
        {
            "scenario": "Email delivery failure with SMS fallback",
            "channel": "email",
            "user_phone": "+1234567890",
            "user_email": "test@example.com",
            "description": "Test email failure with SMS fallback"
        },
        {
            "scenario": "Telegram delivery failure with email fallback",
            "channel": "telegram",
            "user_phone": "+1234567890",
            "user_email": "test@example.com",
            "description": "Test Telegram failure with email fallback"
        },
        {
            "scenario": "Instagram delivery failure with webchat fallback",
            "channel": "instagram",
            "user_phone": "+1234567890",
            "user_email": "test@example.com",
            "description": "Test Instagram failure with webchat fallback"
        }
    ]
    
    for case in edge_cases:
        print(f"\nTesting {case['scenario']}...")
        
        try:
            # Create test ticket
            ticket_data = {
                "title": case['description'],
                "description": "Test ticket for edge case handling",
                "user_phone": case['user_phone'],
                "user_email": case['user_email'],
                "channel": case['channel'],
                "brand_id": 1
            }
            
            # Create ticket
            response = requests.post(
                f"{BASE_URL}/api/v1/tickets/",
                json=ticket_data,
                headers={"Authorization": f"Bearer {get_brand_token()}"}
            )
            
            if response.status_code == 200:
                ticket = response.json()
                ticket_id = ticket['id']
                
                # Schedule follow-up
                follow_up_data = {
                    "ticket_id": ticket_id,
                    "scheduled_time": (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                    "follow_up_type": "reminder",
                    "channel": case['channel']
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/followups/",
                    json=follow_up_data,
                    headers={"Authorization": f"Bearer {get_brand_token()}"}
                )
                
                if response.status_code == 200:
                    follow_up = response.json()
                    print(f"✅ {case['scenario']} - Follow-up scheduled: {follow_up['id']}")
                    
                    # Wait for execution
                    time.sleep(70)  # Wait 70 seconds for execution
                    
                    # Check follow-up status
                    response = requests.get(
                        f"{BASE_URL}/api/v1/followups/{follow_up['id']}",
                        headers={"Authorization": f"Bearer {get_brand_token()}"}
                    )
                    
                    if response.status_code == 200:
                        status = response.json()
                        print(f"   Status: {status['status']}")
                        if status.get('error_message'):
                            print(f"   Error: {status['error_message']}")
                    else:
                        print(f"   ❌ Failed to get follow-up status: {response.status_code}")
                        
                else:
                    print(f"❌ {case['scenario']} - Failed to schedule follow-up: {response.status_code}")
            else:
                print(f"❌ {case['scenario']} - Failed to create ticket: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {case['scenario']} - Error: {e}")

def test_retry_mechanisms():
    """Test retry mechanisms for failed deliveries"""
    print("\n=== Testing Retry Mechanisms ===")
    
    try:
        # Create a test ticket with invalid contact info
        ticket_data = {
            "title": "Test retry mechanism",
            "description": "Test ticket for retry mechanism",
            "user_phone": "invalid_phone",
            "user_email": "invalid_email",
            "channel": "voice",
            "brand_id": 1
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/tickets/",
            json=ticket_data,
            headers={"Authorization": f"Bearer {get_brand_token()}"}
        )
        
        if response.status_code == 200:
            ticket = response.json()
            ticket_id = ticket['id']
            
            # Schedule follow-up
            follow_up_data = {
                "ticket_id": ticket_id,
                "scheduled_time": (datetime.utcnow() + timedelta(minutes=1)).isoformat(),
                "follow_up_type": "reminder",
                "channel": "voice"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/followups/",
                json=follow_up_data,
                headers={"Authorization": f"Bearer {get_brand_token()}"}
            )
            
            if response.status_code == 200:
                follow_up = response.json()
                print(f"✅ Retry mechanism test - Follow-up scheduled: {follow_up['id']}")
                
                # Wait for execution and retries
                time.sleep(120)  # Wait 2 minutes for execution and retries
                
                # Check follow-up status
                response = requests.get(
                    f"{BASE_URL}/api/v1/followups/{follow_up['id']}",
                    headers={"Authorization": f"Bearer {get_brand_token()}"}
                )
                
                if response.status_code == 200:
                    status = response.json()
                    print(f"   Final Status: {status['status']}")
                    print(f"   Retry Count: {status.get('retry_count', 0)}")
                    if status.get('error_message'):
                        print(f"   Error: {status['error_message']}")
                else:
                    print(f"   ❌ Failed to get follow-up status: {response.status_code}")
                    
            else:
                print(f"❌ Retry mechanism test - Failed to schedule follow-up: {response.status_code}")
        else:
            print(f"❌ Retry mechanism test - Failed to create ticket: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Retry mechanism test - Error: {e}")

def test_webhook_verification():
    """Test webhook verification endpoints"""
    print("\n=== Testing Webhook Verification ===")
    
    verification_tests = [
        {
            "crm_type": "facebook",
            "params": {
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token",
                "hub.challenge": "test_challenge"
            },
            "description": "Facebook webhook verification"
        },
        {
            "crm_type": "salesforce",
            "params": {
                "challenge": "test_challenge"
            },
            "description": "Salesforce webhook verification"
        },
        {
            "crm_type": "zoho",
            "params": {
                "challenge": "test_challenge"
            },
            "description": "Zoho webhook verification"
        }
    ]
    
    for test in verification_tests:
        print(f"\nTesting {test['description']}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/webhook/crm/{test['crm_type']}/verify",
                params={"brand_id": 1, **test['params']}
            )
            
            if response.status_code == 200:
                print(f"✅ {test['description']} - Success")
            else:
                print(f"❌ {test['description']} - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['description']} - Error: {e}")

def test_webhook_status():
    """Test webhook status endpoint"""
    print("\n=== Testing Webhook Status ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/webhook/crm/salesforce/status",
            params={"brand_id": 1},
            headers={"Authorization": f"Bearer {get_admin_token()}"}
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Webhook status - Success")
            print(f"   CRM Type: {status['crm_type']}")
            print(f"   Is Active: {status['is_active']}")
            print(f"   Webhook URL: {status['webhook_url']}")
            print(f"   Last Sync: {status.get('last_sync', 'Never')}")
        else:
            print(f"❌ Webhook status - Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook status - Error: {e}")

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

def get_brand_token():
    """Get brand authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": BRAND_EMAIL,
                "password": BRAND_PASSWORD
            }
        )
        
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Failed to get brand token: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting brand token: {e}")
        return None

def main():
    """Run all tests"""
    print("Starting CRM Webhook and Follow-up Edge Case Tests")
    print("=" * 60)
    
    # Test CRM webhook processing
    test_crm_webhook_processing()
    
    # Test webhook signature verification
    test_webhook_signature_verification()
    
    # Test webhook verification
    test_webhook_verification()
    
    # Test webhook status
    test_webhook_status()
    
    # Test follow-up delivery edge cases
    test_follow_up_delivery_edge_cases()
    
    # Test retry mechanisms
    test_retry_mechanisms()
    
    print("\n" + "=" * 60)
    print("CRM Webhook and Follow-up Edge Case Tests Completed")

if __name__ == "__main__":
    main() 