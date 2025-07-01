# Team Invitation Setup Guide

This guide will help you set up the Brand Team management functionality with email invitations for ComplaintHubBot.

## Overview

The team invitation system allows brand administrators to invite team members (agents and admins) to join their brand on the platform. When an invitation is sent, the invitee receives an email with a secure link to register and join the team.

## Features

- ✅ Send team invitations via email
- ✅ Secure invitation tokens with 7-day expiry
- ✅ Beautiful HTML email templates
- ✅ Public invitation acceptance page
- ✅ Role-based team management (Agent/Admin)
- ✅ Invitation status tracking
- ✅ Delete pending invitations

## Setup Instructions

### 1. Email Configuration

The system uses SMTP to send invitation emails. Follow these steps to configure email:

#### For Gmail:

1. **Enable 2-Factor Authentication**
   - Go to your Google Account settings
   - Enable 2-factor authentication

2. **Generate App Password**
   - Go to Security settings
   - Generate an App Password for "Mail"
   - Save the 16-character password

3. **Configure Environment Variables**
   Create a `.env` file in the `backend/` directory:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_character_app_password
FROM_EMAIL=noreply@complainthubbot.com

# Frontend URL (for invitation links)
FRONTEND_URL=http://localhost:3000
```

#### For Other Email Providers:

Update the SMTP settings according to your provider:
- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **Yahoo**: `smtp.mail.yahoo.com:587`
- **Custom SMTP**: Use your provider's SMTP settings

### 2. Test Email Configuration

Run the email test script to verify your configuration:

```bash
cd backend
python test_email.py
```

This will:
- Check your email configuration
- Send a test invitation email
- Verify the email was sent successfully

### 3. Frontend URL Configuration

Make sure the `FRONTEND_URL` in your environment variables matches your frontend application URL:

- **Development**: `http://localhost:3000`
- **Production**: `https://yourdomain.com`

## Usage

### For Brand Administrators

1. **Access Team Management**
   - Log in to your brand account
   - Navigate to "Team" in the sidebar
   - Click "Invite New Member"

2. **Send Invitation**
   - Enter the invitee's email address
   - Select their role (Agent or Admin)
   - Click "Send Invite"

3. **Monitor Invitations**
   - View pending invitations
   - See invitation status (Pending/Accepted/Expired)
   - Delete expired or unwanted invitations

### For Invitees

1. **Receive Email**
   - Check email for invitation from ComplaintHubBot
   - Click the "Accept Invitation" button

2. **Complete Registration**
   - Fill in your full name
   - Create a password
   - Optionally add phone number
   - Click "Accept Invitation & Create Account"

3. **Access Platform**
   - Log in with your email and password
   - Access brand dashboard and features

## API Endpoints

### Team Invitations

- `POST /api/v1/brands/{brand_id}/invitations` - Create invitation
- `GET /api/v1/brands/{brand_id}/invitations` - List invitations
- `DELETE /api/v1/brands/{brand_id}/invitations/{invitation_id}` - Delete invitation

### Team Members

- `GET /api/v1/brands/{brand_id}/team-members` - List team members

### Public Endpoints

- `GET /api/v1/brands/invitations/{token}` - Get invitation details
- `POST /api/v1/brands/invitations/{token}/accept` - Accept invitation

## Email Template

The invitation email includes:
- Brand name and inviter details
- Role information (Agent/Admin)
- Secure invitation link
- Platform description
- Expiration information

## Security Features

- **Secure Tokens**: 32-character random tokens
- **Time-limited**: 7-day expiration
- **Single-use**: Tokens become invalid after acceptance
- **Email Verification**: Invitations are tied to specific email addresses

## Troubleshooting

### Email Not Sending

1. **Check SMTP Configuration**
   - Verify SMTP server and port
   - Ensure username and password are correct
   - Check if 2FA is enabled (for Gmail)

2. **Check Logs**
   - Look for email-related errors in backend logs
   - Verify email credentials are loaded

3. **Test Configuration**
   - Run `python test_email.py` to test email setup

### Invitation Links Not Working

1. **Check Frontend URL**
   - Verify `FRONTEND_URL` is correct
   - Ensure frontend is running and accessible

2. **Check Token Validity**
   - Verify invitation hasn't expired
   - Check if invitation was already accepted

### Database Issues

1. **Check Database Schema**
   - Ensure `team_invitations` table exists
   - Verify all required columns are present

2. **Check Relationships**
   - Verify foreign key relationships
   - Check brand and user references

## Development Notes

### Adding New Email Templates

1. Create new function in `backend/app/services/notifications.py`
2. Follow the pattern of `send_team_invitation_email`
3. Use HTML and text versions for compatibility

### Customizing Email Content

Edit the HTML and text content in `send_team_invitation_email()` function to customize:
- Email styling
- Brand messaging
- Call-to-action buttons
- Footer information

### Extending Team Roles

1. Add new roles to `RoleEnum` in `models.py`
2. Update frontend role selection
3. Modify email templates to include new roles

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend logs for error messages
3. Test email configuration with the provided test script
4. Verify all environment variables are set correctly 