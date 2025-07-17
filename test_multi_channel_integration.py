#!/usr/bin/env python3
"""
Multi-Channel Integration Test Script
Tests all channel adapters and webhook endpoints
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class MultiChannelTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data or {},
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        return success
    
    def test_channels_api(self):
        """Test the channels API endpoints"""
        logger.info("🔧 Testing Channels API...")
        
        # Test getting channels list
        try:
            response = self.session.get(f"{API_BASE}/channels/")
            if response.status_code == 200:
                channels = response.json()
                self.log_test(
                    "Get Channels List",
                    True,
                    f"Found {len(channels.get('channels', []))} channels",
                    channels
                )
            else:
                self.log_test(
                    "Get Channels List",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Channels List", False, str(e))
        
        # Test getting webhook URLs
        for channel in ["whatsapp", "telegram", "facebook", "webchat", "voice", "sms"]:
            try:
                response = self.session.get(f"{API_BASE}/channels/{channel}/webhook-url")
                if response.status_code == 200:
                    webhook_info = response.json()
                    self.log_test(
                        f"Get {channel.title()} Webhook URL",
                        True,
                        f"URL: {webhook_info.get('webhook_url', 'N/A')}",
                        webhook_info
                    )
                else:
                    self.log_test(
                        f"Get {channel.title()} Webhook URL",
                        False,
                        f"Status code: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"Get {channel.title()} Webhook URL", False, str(e))
    
    def test_webhook_endpoints(self):
        """Test webhook endpoints with sample data"""
        logger.info("🔗 Testing Webhook Endpoints...")
        
        # Test WhatsApp webhook (Twilio format)
        whatsapp_data = {
            "From": "whatsapp:+1234567890",
            "To": "whatsapp:+0987654321",
            "Body": "Test complaint from WhatsApp",
            "MessageSid": "test_sid_123"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/whatsapp",
                data=whatsapp_data
            )
            if response.status_code == 200:
                self.log_test(
                    "WhatsApp Webhook (Twilio)",
                    True,
                    "Webhook processed successfully"
                )
            else:
                self.log_test(
                    "WhatsApp Webhook (Twilio)",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("WhatsApp Webhook (Twilio)", False, str(e))
        
        # Test Telegram webhook
        telegram_data = {
            "update_id": 123456789,
            "message": {
                "message_id": 123,
                "from": {
                    "id": 987654321,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 987654321,
                    "type": "private"
                },
                "date": int(time.time()),
                "text": "Test complaint from Telegram"
            }
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/telegram",
                json=telegram_data
            )
            if response.status_code == 200:
                self.log_test(
                    "Telegram Webhook",
                    True,
                    "Webhook processed successfully"
                )
            else:
                self.log_test(
                    "Telegram Webhook",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Telegram Webhook", False, str(e))
        
        # Test Facebook webhook
        facebook_data = {
            "object": "page",
            "entry": [
                {
                    "id": "123456789",
                    "time": int(time.time()),
                    "messaging": [
                        {
                            "sender": {"id": "987654321"},
                            "recipient": {"id": "123456789"},
                            "timestamp": int(time.time() * 1000),
                            "message": {
                                "mid": "mid.123456789",
                                "text": "Test complaint from Facebook"
                            }
                        }
                    ]
                }
            ]
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/facebook",
                json=facebook_data
            )
            if response.status_code == 200:
                self.log_test(
                    "Facebook Webhook",
                    True,
                    "Webhook processed successfully"
                )
            else:
                self.log_test(
                    "Facebook Webhook",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Facebook Webhook", False, str(e))
        
        # Test WebChat webhook
        webchat_data = {
            "session_id": "test_session_123",
            "message": "Test complaint from WebChat",
            "user_id": "user_123",
            "user_name": "Test User",
            "brand_id": 1
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/webchat",
                json=webchat_data
            )
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "WebChat Webhook",
                    True,
                    f"Response: {result.get('reply', 'N/A')}",
                    result
                )
            else:
                self.log_test(
                    "WebChat Webhook",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("WebChat Webhook", False, str(e))
        
        # Test SMS webhook
        sms_data = {
            "From": "+1234567890",
            "To": "+0987654321",
            "Body": "Test complaint from SMS",
            "MessageSid": "test_sms_sid_123"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/sms",
                data=sms_data
            )
            if response.status_code == 200:
                self.log_test(
                    "SMS Webhook",
                    True,
                    "Webhook processed successfully"
                )
            else:
                self.log_test(
                    "SMS Webhook",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("SMS Webhook", False, str(e))
        
        # Test Voice webhook
        voice_data = {
            "From": "+1234567890",
            "To": "+0987654321",
            "CallSid": "test_call_sid_123",
            "CallStatus": "ringing"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/voice",
                data=voice_data
            )
            if response.status_code == 200:
                self.log_test(
                    "Voice Webhook",
                    True,
                    "Webhook processed successfully"
                )
            else:
                self.log_test(
                    "Voice Webhook",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Voice Webhook", False, str(e))
    
    def test_voice_transcription(self):
        """Test voice transcription callback"""
        logger.info("🎤 Testing Voice Transcription...")
        
        transcription_data = {
            "TranscriptionText": "This is a test complaint about poor service",
            "TranscriptionStatus": "completed",
            "CallSid": "test_call_sid_123",
            "RecordingUrl": "https://example.com/recording.wav",
            "RecordingDuration": "30"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/voice/transcription",
                data=transcription_data
            )
            if response.status_code == 200:
                self.log_test(
                    "Voice Transcription Callback",
                    True,
                    "Transcription processed successfully"
                )
            else:
                self.log_test(
                    "Voice Transcription Callback",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Voice Transcription Callback", False, str(e))
    
    def test_voice_recording(self):
        """Test voice recording callback"""
        logger.info("🎵 Testing Voice Recording...")
        
        recording_data = {
            "RecordingUrl": "https://example.com/recording.wav",
            "RecordingDuration": "30",
            "CallSid": "test_call_sid_123",
            "RecordingSid": "test_recording_sid_123"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/webhook/voice/recording",
                data=recording_data
            )
            if response.status_code == 200:
                self.log_test(
                    "Voice Recording Callback",
                    True,
                    "Recording processed successfully"
                )
            else:
                self.log_test(
                    "Voice Recording Callback",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Voice Recording Callback", False, str(e))
    
    def test_ivr(self):
        """Test Interactive Voice Response"""
        logger.info("📞 Testing IVR...")
        
        # Test different IVR options
        ivr_options = [
            ("1", "Lodge a complaint"),
            ("2", "Check complaint status"),
            ("3", "Speak to agent"),
            ("4", "Hear options again"),
            ("5", "Invalid option")
        ]
        
        for digit, description in ivr_options:
            try:
                response = self.session.post(
                    f"{API_BASE}/webhook/voice/ivr",
                    data={"Digits": digit}
                )
                if response.status_code == 200:
                    self.log_test(
                        f"IVR Option {digit}",
                        True,
                        f"IVR processed: {description}"
                    )
                else:
                    self.log_test(
                        f"IVR Option {digit}",
                        False,
                        f"Status code: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"IVR Option {digit}", False, str(e))
    
    def test_facebook_verification(self):
        """Test Facebook webhook verification"""
        logger.info("📘 Testing Facebook Verification...")
        
        try:
            response = self.session.get(
                f"{API_BASE}/webhook/facebook/verify",
                params={
                    "hub.mode": "subscribe",
                    "hub.verify_token": "your_verify_token",
                    "hub.challenge": "123456789"
                }
            )
            if response.status_code == 200:
                self.log_test(
                    "Facebook Webhook Verification",
                    True,
                    "Verification successful"
                )
            else:
                self.log_test(
                    "Facebook Webhook Verification",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Facebook Webhook Verification", False, str(e))
    
    def test_channel_testing(self):
        """Test channel testing endpoints"""
        logger.info("🧪 Testing Channel Testing Endpoints...")
        
        # Test WebChat (doesn't require external credentials)
        webchat_test_data = {
            "session_id": "test_session_456",
            "message": "Test message for channel testing"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/channels/webchat/test",
                json=webchat_test_data
            )
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "WebChat Channel Test",
                    True,
                    f"Test result: {result.get('status', 'N/A')}",
                    result
                )
            else:
                self.log_test(
                    "WebChat Channel Test",
                    False,
                    f"Status code: {response.status_code}"
                )
        except Exception as e:
            self.log_test("WebChat Channel Test", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Multi-Channel Integration Tests...")
        
        self.test_channels_api()
        self.test_webhook_endpoints()
        self.test_voice_transcription()
        self.test_voice_recording()
        self.test_ivr()
        self.test_facebook_verification()
        self.test_channel_testing()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    logger.info(f"  - {result['test']}: {result['message']}")
        
        logger.info("\n" + "="*60)
        
        # Save results to file
        with open("multi_channel_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        logger.info("📄 Test results saved to multi_channel_test_results.json")

def main():
    """Main function"""
    tester = MultiChannelTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 