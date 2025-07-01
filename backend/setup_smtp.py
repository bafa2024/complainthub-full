#!/usr/bin/env python3
"""
SMTP Setup Script for ComplaintHubBot
This script helps you configure SMTP settings for email invitations
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with SMTP configuration"""
    
    print("🔧 SMTP Setup for ComplaintHubBot")
    print("=" * 50)
    
    # Get user input
    print("\n📧 Email Configuration")
    print("For Gmail setup, you need:")
    print("1. 2-factor authentication enabled")
    print("2. App Password generated")
    print("3. Your Gmail address")
    print()
    
    email = input("Enter your Gmail address: ").strip()
    if not email or '@' not in email:
        print("❌ Please enter a valid email address")
        return False
    
    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    if len(app_password) != 16:
        print("❌ App Password should be 16 characters long")
        print("To generate an App Password:")
        print("1. Go to https://myaccount.google.com/security")
        print("2. Enable 2-factor authentication if not already enabled")
        print("3. Go to 'App passwords'")
        print("4. Generate a password for 'Mail'")
        return False
    
    frontend_url = input("Enter your frontend URL (default: http://localhost:3000): ").strip()
    if not frontend_url:
        frontend_url = "http://localhost:3000"
    
    # Create .env content
    env_content = f"""# Database Configuration
DATABASE_URL=sqlite:///./voicebot.db

# Security
SECRET_KEY=your_secret_key_here_change_in_production

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Email Configuration (for team invitations)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME={email}
SMTP_PASSWORD={app_password}
FROM_EMAIL={email}

# Frontend URL (for invitation links)
FRONTEND_URL={frontend_url}

# Configuration completed on {os.popen('date').read().strip()}
"""
    
    # Write to .env file
    env_path = Path('.env')
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"\n✅ .env file created successfully at {env_path.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_smtp_configuration():
    """Test the SMTP configuration"""
    print("\n🧪 Testing SMTP Configuration")
    print("=" * 30)
    
    try:
        from app.services.notifications import send_team_invitation_email
        from app.config.settings import Settings
        
        settings = Settings()
        
        print(f"SMTP Server: {settings.SMTP_SERVER}")
        print(f"SMTP Port: {settings.SMTP_PORT}")
        print(f"SMTP Username: {settings.SMTP_USERNAME}")
        print(f"From Email: {settings.FROM_EMAIL}")
        print(f"Frontend URL: {settings.FRONTEND_URL}")
        
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            print("\n❌ Email credentials not configured!")
            return False
        
        print("\n✅ Email credentials configured")
        
        # Test email sending
        test_email = input("\nEnter a test email address to send invitation to: ").strip()
        if not test_email:
            print("❌ No test email provided")
            return False
        
        print("\n📧 Sending test email...")
        
        test_invitation_link = f"{settings.FRONTEND_URL}/team-invitation/test-token-123"
        
        email_sent = send_team_invitation_email(
            invitee_email=test_email,
            inviter_name="Test User",
            brand_name="Test Brand",
            role="brand_user",
            invitation_link=test_invitation_link
        )
        
        if email_sent:
            print(f"✅ Test email sent successfully to {test_email}")
            print("Check your email inbox (and spam folder) for the test invitation")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SMTP configuration: {e}")
        return False

def main():
    """Main setup function"""
    print("Welcome to ComplaintHubBot SMTP Setup!")
    print("This will help you configure email sending for team invitations.")
    print()
    
    # Check if .env already exists
    if Path('.env').exists():
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Create .env file
    if not create_env_file():
        print("Setup failed. Please try again.")
        return
    
    # Test configuration
    print("\n" + "="*50)
    test_smtp = input("Do you want to test the SMTP configuration now? (Y/n): ").strip().lower()
    if test_smtp != 'n':
        if test_smtp_configuration():
            print("\n🎉 SMTP setup completed successfully!")
            print("You can now send team invitations from your application.")
        else:
            print("\n❌ SMTP test failed. Please check your configuration.")
    
    print("\n📝 Next steps:")
    print("1. Restart your backend server to load the new environment variables")
    print("2. Try sending a team invitation from the frontend")
    print("3. Check the logs if you encounter any issues")

if __name__ == "__main__":
    main() 