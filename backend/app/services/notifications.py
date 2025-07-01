import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from app.config.settings import Settings

logger = logging.getLogger(__name__)

# Get settings
settings = Settings()

# Email configuration
SMTP_SERVER = settings.SMTP_SERVER
SMTP_PORT = settings.SMTP_PORT
SMTP_USERNAME = settings.SMTP_USERNAME
SMTP_PASSWORD = settings.SMTP_PASSWORD
FROM_EMAIL = settings.FROM_EMAIL

def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """Send email using SMTP"""
    try:
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_team_invitation_email(invitee_email: str, inviter_name: str, brand_name: str, role: str, invitation_link: str):
    """Send team invitation email"""
    subject = f"You're invited to join {brand_name} on ComplaintHubBot"
    
    # HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Team Invitation - {brand_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .button:hover {{
                background: #5a6fd8;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
            .highlight {{
                background: #fff3cd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎉 You're Invited!</h1>
            <p>Join the {brand_name} team on ComplaintHubBot</p>
        </div>
        
        <div class="content">
            <h2>Hello!</h2>
            <p><strong>{inviter_name}</strong> has invited you to join the <strong>{brand_name}</strong> team on ComplaintHubBot as a <strong>{role}</strong>.</p>
            
            <div class="highlight">
                <strong>What is ComplaintHubBot?</strong><br>
                ComplaintHubBot is a comprehensive complaint management platform that helps brands handle customer complaints efficiently across multiple channels including WhatsApp, Telegram, web chat, and voice calls.
            </div>
            
            <p>As a team member, you'll be able to:</p>
            <ul>
                <li>View and respond to customer complaints</li>
                <li>Access analytics and performance metrics</li>
                <li>Collaborate with your team members</li>
                <li>Manage customer relationships effectively</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="{invitation_link}" class="button">Accept Invitation</a>
            </div>
            
            <p style="font-size: 14px; color: #666;">
                <strong>Important:</strong> This invitation link will expire in 7 days. If you have any questions, please contact {inviter_name} or our support team.
            </p>
        </div>
        
        <div class="footer">
            <p>This invitation was sent from ComplaintHubBot. If you didn't expect this invitation, you can safely ignore this email.</p>
            <p>© 2024 ComplaintHubBot. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # Text content (fallback)
    text_content = f"""
    You're Invited to Join {brand_name} on ComplaintHubBot
    
    Hello!
    
    {inviter_name} has invited you to join the {brand_name} team on ComplaintHubBot as a {role}.
    
    What is ComplaintHubBot?
    ComplaintHubBot is a comprehensive complaint management platform that helps brands handle customer complaints efficiently across multiple channels including WhatsApp, Telegram, web chat, and voice calls.
    
    As a team member, you'll be able to:
    - View and respond to customer complaints
    - Access analytics and performance metrics
    - Collaborate with your team members
    - Manage customer relationships effectively
    
    Accept your invitation here: {invitation_link}
    
    Important: This invitation link will expire in 7 days. If you have any questions, please contact {inviter_name} or our support team.
    
    This invitation was sent from ComplaintHubBot. If you didn't expect this invitation, you can safely ignore this email.
    
    © 2024 ComplaintHubBot. All rights reserved.
    """
    
    return send_email(invitee_email, subject, html_content, text_content)

def send_notification(user_id: int, type: str, data: dict):
    """Send notification to user (placeholder for future implementation)"""
    logger.info(f"Sending notification to user {user_id}: {type} - {data}")
    # This can be expanded to send push notifications, SMS, etc.
    pass
