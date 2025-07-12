# backend/app/api/v1/endpoints/channels.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.config.settings import settings
from app.adapters.whatsapp_adapter import WhatsAppAdapter
from app.adapters.telegram_adapter import TelegramAdapter
from app.adapters.facebook_adapter import FacebookMessengerAdapter
from app.adapters.twilio_adapter import TwilioAdapter
from app.adapters.webchat_adapter import WebChatAdapter
from app.adapters.instagram_adapter import InstagramAdapter
from app.adapters.linkedin_adapter import LinkedInAdapter
from app.adapters.knowlarity_adapter import KnowlarityAdapter
from app.adapters.exotel_adapter import ExotelAdapter
import logging
from typing import Dict, Any, List, Optional
import json
import requests

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize adapters
whatsapp_adapter = WhatsAppAdapter()
telegram_adapter = TelegramAdapter()
facebook_adapter = FacebookMessengerAdapter()
twilio_adapter = TwilioAdapter()
webchat_adapter = WebChatAdapter()
instagram_adapter = InstagramAdapter()
linkedin_adapter = LinkedInAdapter()

# Initialize additional adapters
knowlarity_adapter = KnowlarityAdapter()
exotel_adapter = ExotelAdapter()

@router.get("/")
async def get_channels(
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get all available channels and their status
    """
    try:
        channels = []
        
        # WhatsApp
        whatsapp_status = _check_whatsapp_status()
        channels.append({
            "id": "whatsapp",
            "name": "WhatsApp",
            "enabled": "whatsapp" in settings.ENABLED_CHANNELS,
            "status": whatsapp_status["status"],
            "message": whatsapp_status["message"],
            "config": {
                "twilio_enabled": bool(settings.TWILIO_ACCOUNT_SID),
                "business_api_enabled": bool(settings.WHATSAPP_BUSINESS_TOKEN),
                "phone_number": settings.TWILIO_WHATSAPP_NUMBER or "Not configured"
            }
        })
        
        # Telegram
        telegram_status = _check_telegram_status()
        channels.append({
            "id": "telegram",
            "name": "Telegram",
            "enabled": "telegram" in settings.ENABLED_CHANNELS,
            "status": telegram_status["status"],
            "message": telegram_status["message"],
            "config": {
                "bot_token_configured": bool(settings.TELEGRAM_BOT_TOKEN),
                "webhook_url": settings.TELEGRAM_WEBHOOK_URL or "Not configured"
            }
        })
        
        # Facebook
        facebook_status = _check_facebook_status()
        channels.append({
            "id": "facebook",
            "name": "Facebook Messenger",
            "enabled": "facebook" in settings.ENABLED_CHANNELS,
            "status": facebook_status["status"],
            "message": facebook_status["message"],
            "config": {
                "page_token_configured": bool(settings.FACEBOOK_PAGE_ACCESS_TOKEN),
                "verify_token": settings.FACEBOOK_VERIFY_TOKEN or "Not configured"
            }
        })
        
        # Voice
        voice_status = _check_voice_status()
        channels.append({
            "id": "voice",
            "name": "Voice Calls",
            "enabled": "voice" in settings.ENABLED_CHANNELS,
            "status": voice_status["status"],
            "message": voice_status["message"],
            "config": {
                "twilio_enabled": bool(settings.TWILIO_ACCOUNT_SID),
                "phone_number": settings.TWILIO_PHONE_NUMBER or "Not configured"
            }
        })
        
        # SMS
        sms_status = _check_sms_status()
        channels.append({
            "id": "sms",
            "name": "SMS",
            "enabled": "sms" in settings.ENABLED_CHANNELS,
            "status": sms_status["status"],
            "message": sms_status["message"],
            "config": {
                "twilio_enabled": bool(settings.TWILIO_ACCOUNT_SID),
                "phone_number": settings.TWILIO_PHONE_NUMBER or "Not configured"
            }
        })
        
        # WebChat
        webchat_status = _check_webchat_status()
        channels.append({
            "id": "webchat",
            "name": "Web Chat",
            "enabled": "webchat" in settings.ENABLED_CHANNELS,
            "status": webchat_status["status"],
            "message": webchat_status["message"],
            "config": {
                "websocket_enabled": settings.WEBSOCKET_ENABLED,
                "active_sessions": len(webchat_adapter.active_sessions)
            }
        })
        
        # Instagram
        instagram_status = {"status": "configured" if settings.INSTAGRAM_ACCESS_TOKEN else "not_configured", "message": "Configured" if settings.INSTAGRAM_ACCESS_TOKEN else "Not configured"}
        channels.append({
            "id": "instagram",
            "name": "Instagram DM",
            "enabled": "instagram" in settings.ENABLED_CHANNELS,
            "status": instagram_status["status"],
            "message": instagram_status["message"],
            "config": {
                "access_token_configured": bool(settings.INSTAGRAM_ACCESS_TOKEN)
            }
        })
        # LinkedIn
        linkedin_status = {"status": "configured" if settings.LINKEDIN_ACCESS_TOKEN else "not_configured", "message": "Configured" if settings.LINKEDIN_ACCESS_TOKEN else "Not configured"}
        channels.append({
            "id": "linkedin",
            "name": "LinkedIn Messaging",
            "enabled": "linkedin" in settings.ENABLED_CHANNELS,
            "status": linkedin_status["status"],
            "message": linkedin_status["message"],
            "config": {
                "access_token_configured": bool(settings.LINKEDIN_ACCESS_TOKEN)
            }
        })
        
        return {
            "channels": channels,
            "total_enabled": len([c for c in channels if c["enabled"]]),
            "total_configured": len([c for c in channels if c["status"] == "configured"])
        }
        
    except Exception as e:
        logger.error(f"Error getting channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to get channels")

@router.post("/{channel_id}/test")
async def test_channel(
    channel_id: str,
    test_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Test a specific channel
    """
    try:
        if channel_id == "whatsapp":
            return await _test_whatsapp(test_data)
        elif channel_id == "telegram":
            return await _test_telegram(test_data)
        elif channel_id == "facebook":
            return await _test_facebook(test_data)
        elif channel_id == "voice":
            return await _test_voice(test_data)
        elif channel_id == "sms":
            return await _test_sms(test_data)
        elif channel_id == "webchat":
            return await _test_webchat(test_data)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel_id}' not supported")
            
    except Exception as e:
        logger.error(f"Error testing channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test channel: {str(e)}")

@router.post("/{channel_id}/configure")
async def configure_channel(
    channel_id: str,
    config_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Configure a specific channel
    """
    try:
        if channel_id == "whatsapp":
            return await _configure_whatsapp(config_data)
        elif channel_id == "telegram":
            return await _configure_telegram(config_data)
        elif channel_id == "facebook":
            return await _configure_facebook(config_data)
        elif channel_id == "voice":
            return await _configure_voice(config_data)
        elif channel_id == "sms":
            return await _configure_sms(config_data)
        elif channel_id == "webchat":
            return await _configure_webchat(config_data)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel_id}' not supported")
            
    except Exception as e:
        logger.error(f"Error configuring channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to configure channel: {str(e)}")

@router.get("/{channel_id}/webhook-url")
async def get_webhook_url(
    channel_id: str,
    db: Session = Depends(deps.get_db),
    current_user: dict = Depends(deps.get_current_user)
):
    """
    Get webhook URL for a specific channel
    """
    try:
        base_url = "https://your-domain.com"  # This should be configurable
        
        webhook_urls = {
            "whatsapp": f"{base_url}/api/v1/webhook/whatsapp",
            "telegram": f"{base_url}/api/v1/webhook/telegram",
            "facebook": f"{base_url}/api/v1/webhook/facebook",
            "voice": f"{base_url}/api/v1/webhook/voice",
            "sms": f"{base_url}/api/v1/webhook/sms",
            "webchat": f"{base_url}/api/v1/webhook/webchat"
        }
        
        if channel_id not in webhook_urls:
            raise HTTPException(status_code=400, detail=f"Channel '{channel_id}' not supported")
        
        return {
            "channel": channel_id,
            "webhook_url": webhook_urls[channel_id],
            "method": "POST",
            "content_type": "application/json" if channel_id in ["telegram", "facebook", "webchat"] else "application/x-www-form-urlencoded"
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook URL for {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook URL")

@router.post("/knowlarity/test")
async def test_knowlarity_connection(
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Test Knowlarity connection and configuration
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Test Knowlarity configuration
        if not knowlarity_adapter.api_key:
            return {
                "success": False,
                "error": "Knowlarity API key not configured",
                "config_status": "missing"
            }
        
        # Test API connection
        test_response = requests.get(
            f"{knowlarity_adapter.base_url}/status",
            headers={"Authorization": f"Bearer {knowlarity_adapter.api_key}"}
        )
        
        if test_response.status_code == 200:
            return {
                "success": True,
                "message": "Knowlarity connection successful",
                "config_status": "active"
            }
        else:
            return {
                "success": False,
                "error": f"Knowlarity API error: {test_response.status_code}",
                "config_status": "error"
            }
            
    except Exception as e:
        logger.error(f"Error testing Knowlarity connection: {e}")
        return {
            "success": False,
            "error": str(e),
            "config_status": "error"
        }

@router.post("/exotel/test")
async def test_exotel_connection(
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Test Exotel connection and configuration
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Test Exotel configuration
        if not exotel_adapter.sid or not exotel_adapter.token:
            return {
                "success": False,
                "error": "Exotel credentials not configured",
                "config_status": "missing"
            }
        
        # Test API connection
        test_response = requests.get(
            f"{exotel_adapter.base_url}/Accounts/{exotel_adapter.sid}.json",
            auth=(exotel_adapter.sid, exotel_adapter.token)
        )
        
        if test_response.status_code == 200:
            return {
                "success": True,
                "message": "Exotel connection successful",
                "config_status": "active"
            }
        else:
            return {
                "success": False,
                "error": f"Exotel API error: {test_response.status_code}",
                "config_status": "error"
            }
            
    except Exception as e:
        logger.error(f"Error testing Exotel connection: {e}")
        return {
            "success": False,
            "error": str(e),
            "config_status": "error"
        }

@router.post("/knowlarity/send-sms")
async def send_knowlarity_sms(
    request: Dict[str, Any],
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Send SMS via Knowlarity
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        to_number = request.get("to_number")
        message = request.get("message")
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing to_number or message")
        
        # Send SMS
        success = knowlarity_adapter.send_sms(to_number, message)
        
        if success:
            return {"success": True, "message": "SMS sent successfully"}
        else:
            return {"success": False, "error": "Failed to send SMS"}
            
    except Exception as e:
        logger.error(f"Error sending Knowlarity SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS")

@router.post("/exotel/send-sms")
async def send_exotel_sms(
    request: Dict[str, Any],
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Send SMS via Exotel
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        to_number = request.get("to_number")
        message = request.get("message")
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing to_number or message")
        
        # Send SMS
        success = exotel_adapter.send_sms(to_number, message)
        
        if success:
            return {"success": True, "message": "SMS sent successfully"}
        else:
            return {"success": False, "error": "Failed to send SMS"}
            
    except Exception as e:
        logger.error(f"Error sending Exotel SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS")

@router.post("/knowlarity/make-call")
async def make_knowlarity_call(
    request: Dict[str, Any],
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Make outbound call via Knowlarity
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        to_number = request.get("to_number")
        message = request.get("message")
        voice_id = request.get("voice_id")
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing to_number or message")
        
        # Make call
        success = knowlarity_adapter.make_outbound_call(to_number, message, voice_id)
        
        if success:
            return {"success": True, "message": "Call initiated successfully"}
        else:
            return {"success": False, "error": "Failed to initiate call"}
            
    except Exception as e:
        logger.error(f"Error making Knowlarity call: {e}")
        raise HTTPException(status_code=500, detail="Failed to make call")

@router.post("/exotel/make-call")
async def make_exotel_call(
    request: Dict[str, Any],
    current_user: dict = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    """
    Make outbound call via Exotel
    """
    try:
        # Check if user has permission
        if current_user.get("role") != "admin" and current_user.get("brand_id") is None:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        to_number = request.get("to_number")
        message = request.get("message")
        voice_id = request.get("voice_id")
        
        if not to_number or not message:
            raise HTTPException(status_code=400, detail="Missing to_number or message")
        
        # Make call
        success = exotel_adapter.make_outbound_call(to_number, message, voice_id)
        
        if success:
            return {"success": True, "message": "Call initiated successfully"}
        else:
            return {"success": False, "error": "Failed to initiate call"}
            
    except Exception as e:
        logger.error(f"Error making Exotel call: {e}")
        raise HTTPException(status_code=500, detail="Failed to make call")

def _check_whatsapp_status() -> Dict[str, str]:
    """Check WhatsApp configuration status"""
    if not settings.TWILIO_ACCOUNT_SID and not settings.WHATSAPP_BUSINESS_TOKEN:
        return {"status": "not_configured", "message": "No WhatsApp credentials configured"}
    elif settings.TWILIO_ACCOUNT_SID:
        return {"status": "configured", "message": "Configured via Twilio"}
    else:
        return {"status": "configured", "message": "Configured via WhatsApp Business API"}

def _check_telegram_status() -> Dict[str, str]:
    """Check Telegram configuration status"""
    if not settings.TELEGRAM_BOT_TOKEN:
        return {"status": "not_configured", "message": "Bot token not configured"}
    else:
        return {"status": "configured", "message": "Bot token configured"}

def _check_facebook_status() -> Dict[str, str]:
    """Check Facebook configuration status"""
    if not settings.FACEBOOK_PAGE_ACCESS_TOKEN:
        return {"status": "not_configured", "message": "Page access token not configured"}
    else:
        return {"status": "configured", "message": "Page access token configured"}

def _check_voice_status() -> Dict[str, str]:
    """Check Voice configuration status"""
    if not settings.TWILIO_ACCOUNT_SID:
        return {"status": "not_configured", "message": "Twilio credentials not configured"}
    elif not settings.TWILIO_PHONE_NUMBER:
        return {"status": "partially_configured", "message": "Twilio configured but phone number missing"}
    else:
        return {"status": "configured", "message": "Fully configured"}

def _check_sms_status() -> Dict[str, str]:
    """Check SMS configuration status"""
    if not settings.TWILIO_ACCOUNT_SID:
        return {"status": "not_configured", "message": "Twilio credentials not configured"}
    elif not settings.TWILIO_PHONE_NUMBER:
        return {"status": "partially_configured", "message": "Twilio configured but phone number missing"}
    else:
        return {"status": "configured", "message": "Fully configured"}

def _check_webchat_status() -> Dict[str, str]:
    """Check WebChat configuration status"""
    if settings.WEBSOCKET_ENABLED:
        return {"status": "configured", "message": "WebSocket enabled"}
    else:
        return {"status": "configured", "message": "Basic configuration"}

async def _test_whatsapp(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test WhatsApp channel"""
    try:
        phone_number = test_data.get("phone_number")
        message = test_data.get("message", "Test message from Complaint Management System")
        
        if not phone_number:
            raise ValueError("Phone number is required")
        
        success = whatsapp_adapter.send_message(phone_number, message)
        
        if success:
            return {"status": "success", "message": "Test message sent successfully"}
        else:
            return {"status": "error", "message": "Failed to send test message"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_telegram(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test Telegram channel"""
    try:
        chat_id = test_data.get("chat_id")
        message = test_data.get("message", "Test message from Complaint Management System")
        
        if not chat_id:
            raise ValueError("Chat ID is required")
        
        result = telegram_adapter.send_message(chat_id, message)
        
        if result.get("ok"):
            return {"status": "success", "message": "Test message sent successfully"}
        else:
            return {"status": "error", "message": result.get("error", "Failed to send test message")}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_facebook(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test Facebook channel"""
    try:
        recipient_id = test_data.get("recipient_id")
        message = test_data.get("message", "Test message from Complaint Management System")
        
        if not recipient_id:
            raise ValueError("Recipient ID is required")
        
        success = facebook_adapter.send_message(recipient_id, message)
        
        if success:
            return {"status": "success", "message": "Test message sent successfully"}
        else:
            return {"status": "error", "message": "Failed to send test message"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_voice(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test Voice channel"""
    try:
        phone_number = test_data.get("phone_number")
        message = test_data.get("message", "This is a test call from the Complaint Management System")
        
        if not phone_number:
            raise ValueError("Phone number is required")
        
        success = twilio_adapter.make_outbound_call(phone_number, message)
        
        if success:
            return {"status": "success", "message": "Test call initiated successfully"}
        else:
            return {"status": "error", "message": "Failed to initiate test call"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_sms(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test SMS channel"""
    try:
        phone_number = test_data.get("phone_number")
        message = test_data.get("message", "Test SMS from Complaint Management System")
        
        if not phone_number:
            raise ValueError("Phone number is required")
        
        success = twilio_adapter.send_sms(phone_number, message)
        
        if success:
            return {"status": "success", "message": "Test SMS sent successfully"}
        else:
            return {"status": "error", "message": "Failed to send test SMS"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _test_webchat(test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test WebChat channel"""
    try:
        session_id = test_data.get("session_id")
        message = test_data.get("message", "Test message from WebChat")
        
        if not session_id:
            # Create a test session
            result = webchat_adapter.create_chat_session()
            session_id = result["session"]["session_id"]
        
        # Send a test message
        result = webchat_adapter.send_system_message(session_id, message, "test")
        
        if result["status"] == "success":
            return {"status": "success", "message": "Test message sent successfully", "session_id": session_id}
        else:
            return {"status": "error", "message": "Failed to send test message"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def _configure_whatsapp(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure WhatsApp channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "WhatsApp configuration updated"}

async def _configure_telegram(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure Telegram channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "Telegram configuration updated"}

async def _configure_facebook(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure Facebook channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "Facebook configuration updated"}

async def _configure_voice(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure Voice channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "Voice configuration updated"}

async def _configure_sms(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure SMS channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "SMS configuration updated"}

async def _configure_webchat(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Configure WebChat channel"""
    # In a real implementation, this would save to database or environment
    return {"status": "success", "message": "WebChat configuration updated"} 