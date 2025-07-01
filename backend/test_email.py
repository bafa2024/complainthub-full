#!/usr/bin/env python3
"""
Test script for email functionality
"""

import os
import sys
from app.services.notifications import send_team_invitation_email
from app.config.settings import Settings

def test_email_configuration():
    """Test email configuration and sending"""
    
    print("🧪 Testing Email Configuration")
    print("=" * 50)
    
    # Load settings
    settings = Settings()
    
    print(f"SMTP Server: {settings.SMTP_SERVER}")
    print(f"SMTP Port: {settings.SMTP_PORT}")
    print(f"SMTP Username: {settings.SMTP_USERNAME}")
    print(f"From Email: {settings.FROM_EMAIL}")
    print(f"Frontend URL: {settings.FRONTEND_URL}")
    
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("\n❌ Email credentials not configured!")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD in your environment variables or .env file")
        print("\nFor Gmail setup:")
        print("1. Enable 2-factor authentication on your Gmail account")
        print("2. Generate an App Password")
        print("3. Set SMTP_USERNAME=your_email@gmail.com")
        print("4. Set SMTP_PASSWORD=your_app_password")
        return False
    
    print("\n✅ Email credentials configured")
    
    # Test email sending
    print("\n📧 Testing email sending...")
    
    test_email = "test@example.com"  # Change this to your test email
    test_invitation_link = f"{settings.FRONTEND_URL}/team-invitation/test-token-123"
    
    try:
        email_sent = send_team_invitation_email(
            invitee_email=test_email,
            inviter_name="Test User",
            brand_name="Test Brand",
            role="brand_user",
            invitation_link=test_invitation_link
        )
        
        if email_sent:
            print(f"✅ Test email sent successfully to {test_email}")
            print("Check your email inbox for the test invitation")
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False
    
    print("\n🎉 Email functionality test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_email_configuration()
    sys.exit(0 if success else 1) 