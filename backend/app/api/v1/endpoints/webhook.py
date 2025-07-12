# backend/app/api/v1/endpoints/webhook.py

from fastapi import APIRouter, Depends, Request, HTTPException, Form, File, UploadFile, Response
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine
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
import json
from typing import Dict, Any, Optional

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

@router.post("/{channel}")
async def handle_webhook(
    request: Request,
    channel: str,
    db: Session = Depends(deps.get_db),
):
    """
    Main webhook to handle incoming messages from various channels.
    Supports: whatsapp, telegram, facebook, twilio, webchat, sms, voice
    """
    ai_engine = AIEngine()
    conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)

    try:
        logger.info(f"Processing webhook for channel: {channel}")
        
        # Route to appropriate adapter based on channel
        if channel == "whatsapp":
            return await _handle_whatsapp_webhook(request, conversation_manager, db)
        elif channel == "telegram":
            return await _handle_telegram_webhook(request, conversation_manager, db)
        elif channel == "facebook":
            return await _handle_facebook_webhook(request, conversation_manager, db)
        elif channel == "instagram":
            return await _handle_instagram_webhook(request, conversation_manager, db)
        elif channel == "linkedin":
            return await _handle_linkedin_webhook(request, conversation_manager, db)
        elif channel == "twilio":
            return await _handle_twilio_webhook(request, conversation_manager, db)
        elif channel == "webchat":
            return await _handle_webchat_webhook(request, conversation_manager, db)
        elif channel == "sms":
            return await _handle_sms_webhook(request, conversation_manager, db)
        elif channel == "voice":
            return await _handle_voice_webhook(request, conversation_manager, db)
        elif channel == "knowlarity":
            return await _handle_knowlarity_webhook(request, conversation_manager, db)
        elif channel == "exotel":
            return await _handle_exotel_webhook(request, conversation_manager, db)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported.")

    except Exception as e:
        logger.error(f"Error processing webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message.")

@router.post("/voice/{provider}")
async def handle_voice_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice call webhooks from different providers
    Supports: twilio, knowlarity, exotel
    """
    try:
        logger.info(f"Processing voice webhook for provider: {provider}")
        
        # Route to appropriate provider handler
        if provider == "twilio":
            return await _handle_twilio_voice_webhook(request, db)
        elif provider == "knowlarity":
            return await _handle_knowlarity_voice_webhook(request, db)
        elif provider == "exotel":
            return await _handle_exotel_voice_webhook(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported for voice calls.")

    except Exception as e:
        logger.error(f"Error processing voice webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice call.")

@router.post("/voice/{provider}/transcription")
async def handle_voice_transcription(
    provider: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice transcription callbacks from different providers
    """
    try:
        logger.info(f"Processing transcription webhook for provider: {provider}")
        
        if provider == "twilio":
            return await _handle_twilio_transcription(request, db)
        elif provider == "knowlarity":
            return await _handle_knowlarity_transcription(request, db)
        elif provider == "exotel":
            return await _handle_exotel_transcription(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported for transcription.")

    except Exception as e:
        logger.error(f"Error processing transcription webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process transcription.")

@router.post("/voice/{provider}/recording")
async def handle_voice_recording(
    provider: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice recording callbacks from different providers
    """
    try:
        logger.info(f"Processing recording webhook for provider: {provider}")
        
        if provider == "twilio":
            return await _handle_twilio_recording(request, db)
        elif provider == "knowlarity":
            return await _handle_knowlarity_recording(request, db)
        elif provider == "exotel":
            return await _handle_exotel_recording(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported for recording.")

    except Exception as e:
        logger.error(f"Error processing recording webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process recording.")

@router.post("/voice/{provider}/ivr")
async def handle_voice_ivr(
    provider: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle Interactive Voice Response (IVR) from different providers
    """
    try:
        logger.info(f"Processing IVR webhook for provider: {provider}")
        
        if provider == "twilio":
            return await _handle_twilio_ivr(request, db)
        elif provider == "knowlarity":
            return await _handle_knowlarity_ivr(request, db)
        elif provider == "exotel":
            return await _handle_exotel_ivr(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported for IVR.")

    except Exception as e:
        logger.error(f"Error processing IVR webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process IVR.")

@router.post("/voice/{provider}/menu")
async def handle_voice_menu(
    provider: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice menu selections from different providers
    """
    try:
        logger.info(f"Processing menu webhook for provider: {provider}")
        
        if provider == "twilio":
            return await _handle_twilio_menu(request, db)
        elif provider == "knowlarity":
            return await _handle_knowlarity_menu(request, db)
        elif provider == "exotel":
            return await _handle_exotel_menu(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported for menu.")

    except Exception as e:
        logger.error(f"Error processing menu webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process menu.")

@router.post("/voice/transcription")
async def handle_voice_transcription(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice transcription callback from Twilio
    """
    try:
        data = await request.form()
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        return twilio_adapter._handle_transcription_callback(
            dict(data), conversation_manager, db, brand_id=1
        )
    except Exception as e:
        logger.error(f"Error handling voice transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to process transcription.")

@router.post("/voice/recording")
async def handle_voice_recording(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle voice recording callback from Twilio
    """
    try:
        data = await request.form()
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        return twilio_adapter._handle_recording_callback(
            dict(data), conversation_manager, db, brand_id=1
        )
    except Exception as e:
        logger.error(f"Error handling voice recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to process recording.")

@router.post("/voice/ivr")
async def handle_ivr(
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle Interactive Voice Response (IVR) from Twilio
    """
    try:
        data = await request.form()
        digits = data.get('Digits', '')
        
        # Define IVR options
        options = [
            {"digit": "1", "description": "Lodge a complaint"},
            {"digit": "2", "description": "Check complaint status"},
            {"digit": "3", "description": "Speak to agent"},
            {"digit": "4", "description": "Hear options again"}
        ]
        
        if digits == "1":
            # Route to complaint flow
            return twilio_adapter._generate_initial_voice_response("ivr_complaint", 1)
        elif digits == "2":
            # Route to status check
            return _generate_status_check_response()
        elif digits == "3":
            # Route to agent
            return _generate_agent_transfer_response()
        elif digits == "4":
            # Repeat options
            return twilio_adapter.create_interactive_voice_response(options)
        else:
            # Invalid input
            return _generate_invalid_input_response()
            
    except Exception as e:
        logger.error(f"Error handling IVR: {e}")
        raise HTTPException(status_code=500, detail="Failed to process IVR.")

@router.get("/facebook/verify")
async def verify_facebook_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """
    Verify Facebook webhook
    """
    try:
        if hub_mode == "subscribe" and hub_verify_token == "your_verify_token":
            logger.info("Facebook webhook verified successfully")
            return int(hub_challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    except Exception as e:
        logger.error(f"Error verifying Facebook webhook: {e}")
        raise HTTPException(status_code=500, detail="Verification failed")

@router.post("/telegram/set-webhook")
async def set_telegram_webhook():
    """
    Set Telegram webhook URL
    """
    try:
        # This would typically be called during setup
        webhook_url = "https://your-domain.com/api/v1/webhook/telegram"
        result = telegram_adapter.set_webhook(webhook_url)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Error setting Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to set webhook")

async def _handle_whatsapp_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle WhatsApp webhook"""
    try:
        # Try to get JSON data first (Meta API format)
        try:
            data = await request.json()
        except:
            # Fallback to form data (Twilio format)
            data = await request.form()
            data = dict(data)
        
        brand_id = _determine_brand_id(data, "whatsapp")
        return whatsapp_adapter.handle_webhook(data, conversation_manager, db, brand_id)
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp message")

async def _handle_telegram_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle Telegram webhook"""
    try:
        data = await request.json()
        brand_id = _determine_brand_id(data, "telegram")
        result = telegram_adapter.handle_webhook(data, conversation_manager, db, brand_id)
        
        # Telegram expects a simple response
        if result.get("ok"):
            return {"status": "ok"}
        else:
            return {"status": "error", "message": result.get("error", "Unknown error")}
            
    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram message")

async def _handle_facebook_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle Facebook webhook"""
    try:
        data = await request.json()
        brand_id = _determine_brand_id(data, "facebook")
        result = facebook_adapter.handle_webhook(data, conversation_manager, db, brand_id)
        
        # Facebook expects a simple response
        if result.get("status") == "ok":
            return {"status": "ok"}
        else:
            return {"status": "error", "message": result.get("message", "Unknown error")}
            
    except Exception as e:
        logger.error(f"Error handling Facebook webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Facebook message")

async def _handle_twilio_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle Twilio webhook (voice calls)"""
    try:
        data = await request.form()
        data = dict(data)
        brand_id = _determine_brand_id(data, "twilio")
        return twilio_adapter.handle_voice_call(data, conversation_manager, db, brand_id)
        
    except Exception as e:
        logger.error(f"Error handling Twilio webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio message")

async def _handle_webchat_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle WebChat webhook"""
    try:
        data = await request.json()
        brand_id = _determine_brand_id(data, "webchat")
        result = webchat_adapter.handle_webhook(data, conversation_manager, db, brand_id)
        return result
        
    except Exception as e:
        logger.error(f"Error handling WebChat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WebChat message")

async def _handle_sms_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle SMS webhook"""
    try:
        data = await request.form()
        data = dict(data)
        brand_id = _determine_brand_id(data, "sms")
        return twilio_adapter.handle_sms(data, conversation_manager, db, brand_id)
        
    except Exception as e:
        logger.error(f"Error handling SMS webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process SMS message")

async def _handle_voice_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """Handle voice webhook"""
    try:
        data = await request.form()
        data = dict(data)
        brand_id = _determine_brand_id(data, "voice")
        return twilio_adapter.handle_voice_call(data, conversation_manager, db, brand_id)
        
    except Exception as e:
        logger.error(f"Error handling voice webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice message")

async def _handle_instagram_webhook(request, conversation_manager, db):
    data = await request.json()
    return instagram_adapter.handle_webhook(data, conversation_manager, db, brand_id=None)

async def _handle_linkedin_webhook(request, conversation_manager, db):
    data = await request.json()
    return linkedin_adapter.handle_webhook(data, conversation_manager, db, brand_id=None)

async def _handle_knowlarity_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """
    Handle Knowlarity webhook for voice calls and SMS
    """
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        # Determine webhook type
        if 'call_id' in request_data:
            # Voice call webhook
            response = knowlarity_adapter.handle_voice_call(request_data, conversation_manager, db, brand_id=1)
            return Response(content=response, media_type="application/json")
        elif 'message_id' in request_data:
            # SMS webhook
            response = knowlarity_adapter.handle_sms(request_data, conversation_manager, db, brand_id=1)
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid Knowlarity webhook format")
            
    except Exception as e:
        logger.error(f"Error handling Knowlarity webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity webhook")

async def _handle_exotel_webhook(request: Request, conversation_manager: ConversationManager, db: Session):
    """
    Handle Exotel webhook for voice calls and SMS
    """
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        # Determine webhook type
        if 'CallSid' in request_data:
            # Voice call webhook
            response = exotel_adapter.handle_voice_call(request_data, conversation_manager, db, brand_id=1)
            return Response(content=response, media_type="application/xml")
        elif 'MessageSid' in request_data:
            # SMS webhook
            response = exotel_adapter.handle_sms(request_data, conversation_manager, db, brand_id=1)
            return response
        else:
            raise HTTPException(status_code=400, detail="Invalid Exotel webhook format")
            
    except Exception as e:
        logger.error(f"Error handling Exotel webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel webhook")

# Provider-specific voice webhook handlers

async def _handle_twilio_voice_webhook(request: Request, db: Session):
    """Handle Twilio voice webhook"""
    try:
        data = await request.form()
        data = dict(data)
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the call
        brand_id = _determine_brand_id(data, "voice")
        
        # Handle the voice call
        response = twilio_adapter.handle_voice_call(data, conversation_manager, db, brand_id)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Twilio voice webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio voice call")

async def _handle_knowlarity_voice_webhook(request: Request, db: Session):
    """Handle Knowlarity voice webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the call
        brand_id = _determine_brand_id(request_data, "voice")
        
        # Handle the voice call
        response = knowlarity_adapter.handle_voice_call(request_data, conversation_manager, db, brand_id)
        
        return Response(content=response, media_type="application/json")
        
    except Exception as e:
        logger.error(f"Error handling Knowlarity voice webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity voice call")

async def _handle_exotel_voice_webhook(request: Request, db: Session):
    """Handle Exotel voice webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the call
        brand_id = _determine_brand_id(request_data, "voice")
        
        # Handle the voice call
        response = exotel_adapter.handle_voice_call(request_data, conversation_manager, db, brand_id)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Exotel voice webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel voice call")

# Transcription handlers

async def _handle_twilio_transcription(request: Request, db: Session):
    """Handle Twilio transcription callback"""
    try:
        data = await request.form()
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        return twilio_adapter._handle_transcription_callback(
            dict(data), conversation_manager, db, brand_id=1
        )
    except Exception as e:
        logger.error(f"Error handling Twilio transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio transcription")

async def _handle_knowlarity_transcription(request: Request, db: Session):
    """Handle Knowlarity transcription callback"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Handle transcription callback
        response = knowlarity_adapter._handle_recording_callback(request_data, conversation_manager, db, brand_id=1)
        
        return Response(content=response, media_type="application/json")
        
    except Exception as e:
        logger.error(f"Error handling Knowlarity transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity transcription")

async def _handle_exotel_transcription(request: Request, db: Session):
    """Handle Exotel transcription callback"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Handle transcription callback
        response = exotel_adapter._handle_recording_callback(request_data, conversation_manager, db, brand_id=1)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Exotel transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel transcription")

# Recording handlers

async def _handle_twilio_recording(request: Request, db: Session):
    """Handle Twilio recording callback"""
    try:
        data = await request.form()
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        return twilio_adapter._handle_recording_callback(
            dict(data), conversation_manager, db, brand_id=1
        )
    except Exception as e:
        logger.error(f"Error handling Twilio recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio recording")

async def _handle_knowlarity_recording(request: Request, db: Session):
    """Handle Knowlarity recording callback"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Handle recording callback
        response = knowlarity_adapter._handle_recording_callback(request_data, conversation_manager, db, brand_id=1)
        
        return Response(content=response, media_type="application/json")
        
    except Exception as e:
        logger.error(f"Error handling Knowlarity recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity recording")

async def _handle_exotel_recording(request: Request, db: Session):
    """Handle Exotel recording callback"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Handle recording callback
        response = exotel_adapter._handle_recording_callback(request_data, conversation_manager, db, brand_id=1)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Exotel recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel recording")

# IVR handlers

async def _handle_twilio_ivr(request: Request, db: Session):
    """Handle Twilio IVR"""
    try:
        data = await request.form()
        digits = data.get('Digits', '')
        
        # Define IVR options
        options = [
            {"digit": "1", "description": "Lodge a complaint"},
            {"digit": "2", "description": "Check complaint status"},
            {"digit": "3", "description": "Speak to agent"},
            {"digit": "4", "description": "Hear options again"}
        ]
        
        if digits == "1":
            # Route to complaint flow
            return twilio_adapter._generate_initial_voice_response("ivr_complaint", 1)
        elif digits == "2":
            # Route to status check
            return _generate_status_check_response()
        elif digits == "3":
            # Route to agent
            return _generate_agent_transfer_response()
        elif digits == "4":
            # Repeat options
            return twilio_adapter.create_interactive_voice_response(options)
        else:
            return twilio_adapter._generate_error_response("Invalid selection")
            
    except Exception as e:
        logger.error(f"Error handling Twilio IVR: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio IVR")

async def _handle_knowlarity_ivr(request: Request, db: Session):
    """Handle Knowlarity IVR"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        digits = request_data.get('digits', '')
        
        # Define IVR options
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        # Handle menu selection
        response = knowlarity_adapter.handle_menu_selection(digits, options)
        
        return Response(content=response, media_type="application/json")
        
    except Exception as e:
        logger.error(f"Error handling Knowlarity IVR: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity IVR")

async def _handle_exotel_ivr(request: Request, db: Session):
    """Handle Exotel IVR"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        digits = request_data.get('Digits', '')
        
        # Define IVR options
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        # Handle menu selection
        response = exotel_adapter.handle_menu_selection(digits, options)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Exotel IVR: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel IVR")

# Menu handlers

async def _handle_twilio_menu(request: Request, db: Session):
    """Handle Twilio menu selection"""
    try:
        data = await request.form()
        digits = data.get('Digits', '')
        
        # Define menu options
        options = [
            {"digit": "1", "description": "Lodge a complaint"},
            {"digit": "2", "description": "Check complaint status"},
            {"digit": "3", "description": "Speak to agent"}
        ]
        
        # Handle menu selection
        response = twilio_adapter.handle_menu_selection(digits, options)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Twilio menu: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Twilio menu")

async def _handle_knowlarity_menu(request: Request, db: Session):
    """Handle Knowlarity menu selection"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        digits = request_data.get('digits', '')
        
        # Define menu options
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        # Handle menu selection
        response = knowlarity_adapter.handle_menu_selection(digits, options)
        
        return Response(content=response, media_type="application/json")
        
    except Exception as e:
        logger.error(f"Error handling Knowlarity menu: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Knowlarity menu")

async def _handle_exotel_menu(request: Request, db: Session):
    """Handle Exotel menu selection"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        digits = request_data.get('Digits', '')
        
        # Define menu options
        options = [
            {"description": "Lodge a complaint", "response": "Please describe your issue."},
            {"description": "Check complaint status", "response": "Please provide your ticket number."},
            {"description": "Speak to agent", "response": "Connecting you to an agent."}
        ]
        
        # Handle menu selection
        response = exotel_adapter.handle_menu_selection(digits, options)
        
        return Response(content=response, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling Exotel menu: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Exotel menu")

# Helper functions

def _determine_brand_id(data: Dict[str, Any], channel: str) -> int:
    """Determine brand ID from webhook data"""
    try:
        # Try to extract brand ID from various sources
        to_number = data.get('To', '')
        
        # Check if to_number contains brand identifier
        if to_number:
            # This is a simplified approach - in production, you'd have a mapping
            # of phone numbers to brand IDs
            if '+1800' in to_number:
                return 1  # Default brand
            elif '+911800' in to_number:
                return 1  # Default brand for India
        
        # Default to brand ID 1 if no specific mapping found
        return 1
        
    except Exception as e:
        logger.error(f"Error determining brand ID: {e}")
        return 1

def _generate_status_check_response() -> str:
    """Generate status check response"""
    from twilio.twiml.voice_response import VoiceResponse
    
    resp = VoiceResponse()
    resp.say("Please provide your ticket number to check the status.")
    resp.gather(
        input="dtmf",
        timeout=10,
        num_digits=6,
        action="/api/v1/webhook/voice/twilio/status-check",
        method="POST"
    )
    resp.say("I didn't receive a ticket number. Please call back and try again.")
    
    return str(resp)

def _generate_agent_transfer_response() -> str:
    """Generate agent transfer response"""
    from twilio.twiml.voice_response import VoiceResponse
    
    resp = VoiceResponse()
    resp.say("Please wait while I transfer you to a customer service representative.")
    resp.dial(
        settings.SUPPORT_PHONE_NUMBER,
        timeout=30,
        action="/api/v1/webhook/voice/twilio/transfer-status",
        method="POST"
    )
    resp.say("I'm sorry, but all agents are currently busy. Please try again later or leave a message.")
    
    return str(resp)

def _generate_invalid_input_response():
    """Generate response for invalid input"""
    from twilio.twiml.voice_response import VoiceResponse
    resp = VoiceResponse()
    resp.say(
        "I didn't understand your selection. Please try again.",
        voice='alice',
        language='en-US'
    )
    return str(resp)

@router.post("/chat/{channel}")
async def handle_chat_webhook(
    channel: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle chat/message webhooks from different channels
    Supports: whatsapp, telegram, instagram, facebook, linkedin, webchat
    """
    try:
        logger.info(f"Processing chat webhook for channel: {channel}")
        
        # Route to appropriate channel handler
        if channel == "whatsapp":
            return await _handle_whatsapp_chat_webhook(request, db)
        elif channel == "telegram":
            return await _handle_telegram_chat_webhook(request, db)
        elif channel == "instagram":
            return await _handle_instagram_chat_webhook(request, db)
        elif channel == "facebook":
            return await _handle_facebook_chat_webhook(request, db)
        elif channel == "linkedin":
            return await _handle_linkedin_chat_webhook(request, db)
        elif channel == "webchat":
            return await _handle_webchat_chat_webhook(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported for chat.")

    except Exception as e:
        logger.error(f"Error processing chat webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message.")

@router.post("/chat/{channel}/media")
async def handle_chat_media_webhook(
    channel: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle media file uploads from chat channels
    """
    try:
        logger.info(f"Processing media webhook for channel: {channel}")
        
        if channel == "whatsapp":
            return await _handle_whatsapp_media_webhook(request, db)
        elif channel == "telegram":
            return await _handle_telegram_media_webhook(request, db)
        elif channel == "instagram":
            return await _handle_instagram_media_webhook(request, db)
        elif channel == "facebook":
            return await _handle_facebook_media_webhook(request, db)
        elif channel == "linkedin":
            return await _handle_linkedin_media_webhook(request, db)
        elif channel == "webchat":
            return await _handle_webchat_media_webhook(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported for media.")

    except Exception as e:
        logger.error(f"Error processing media webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process media.")

@router.post("/chat/{channel}/status")
async def handle_chat_status_webhook(
    channel: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle message status updates from chat channels
    """
    try:
        logger.info(f"Processing status webhook for channel: {channel}")
        
        if channel == "whatsapp":
            return await _handle_whatsapp_status_webhook(request, db)
        elif channel == "telegram":
            return await _handle_telegram_status_webhook(request, db)
        elif channel == "instagram":
            return await _handle_instagram_status_webhook(request, db)
        elif channel == "facebook":
            return await _handle_facebook_status_webhook(request, db)
        elif channel == "linkedin":
            return await _handle_linkedin_status_webhook(request, db)
        elif channel == "webchat":
            return await _handle_webchat_status_webhook(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported for status updates.")

    except Exception as e:
        logger.error(f"Error processing status webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process status update.")

@router.post("/chat/{channel}/typing")
async def handle_chat_typing_webhook(
    channel: str,
    request: Request,
    db: Session = Depends(deps.get_db),
):
    """
    Handle typing indicators from chat channels
    """
    try:
        logger.info(f"Processing typing webhook for channel: {channel}")
        
        if channel == "whatsapp":
            return await _handle_whatsapp_typing_webhook(request, db)
        elif channel == "telegram":
            return await _handle_telegram_typing_webhook(request, db)
        elif channel == "instagram":
            return await _handle_instagram_typing_webhook(request, db)
        elif channel == "facebook":
            return await _handle_facebook_typing_webhook(request, db)
        elif channel == "linkedin":
            return await _handle_linkedin_typing_webhook(request, db)
        elif channel == "webchat":
            return await _handle_webchat_typing_webhook(request, db)
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported for typing indicators.")

    except Exception as e:
        logger.error(f"Error processing typing webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process typing indicator.")

# Channel-specific chat webhook handlers

async def _handle_whatsapp_chat_webhook(request: Request, db: Session):
    """Handle WhatsApp chat webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(request_data, "whatsapp")
        
        # Handle the chat message
        response = whatsapp_adapter.handle_webhook(request_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp message")

async def _handle_telegram_chat_webhook(request: Request, db: Session):
    """Handle Telegram chat webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "telegram")
        
        # Handle the chat message
        response = telegram_adapter.handle_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Telegram chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram message")

async def _handle_instagram_chat_webhook(request: Request, db: Session):
    """Handle Instagram chat webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "instagram")
        
        # Handle the chat message
        response = instagram_adapter.handle_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Instagram chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram message")

async def _handle_facebook_chat_webhook(request: Request, db: Session):
    """Handle Facebook chat webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "facebook")
        
        # Handle the chat message
        response = facebook_adapter.handle_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Facebook chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Facebook message")

async def _handle_linkedin_chat_webhook(request: Request, db: Session):
    """Handle LinkedIn chat webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "linkedin")
        
        # Handle the chat message
        response = linkedin_adapter.handle_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling LinkedIn chat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process LinkedIn message")

async def _handle_webchat_chat_webhook(request: Request, db: Session):
    """Handle WebChat webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "webchat")
        
        # Handle the chat message
        response = webchat_adapter.handle_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WebChat webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WebChat message")

# Media webhook handlers

async def _handle_whatsapp_media_webhook(request: Request, db: Session):
    """Handle WhatsApp media webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(request_data, "whatsapp")
        
        # Handle the media message
        response = whatsapp_adapter.handle_media_webhook(request_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp media")

async def _handle_telegram_media_webhook(request: Request, db: Session):
    """Handle Telegram media webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "telegram")
        
        # Handle the media message
        response = telegram_adapter.handle_media_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Telegram media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram media")

async def _handle_instagram_media_webhook(request: Request, db: Session):
    """Handle Instagram media webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "instagram")
        
        # Handle the media message
        response = instagram_adapter.handle_media_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Instagram media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram media")

async def _handle_facebook_media_webhook(request: Request, db: Session):
    """Handle Facebook media webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "facebook")
        
        # Handle the media message
        response = facebook_adapter.handle_media_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Facebook media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Facebook media")

async def _handle_linkedin_media_webhook(request: Request, db: Session):
    """Handle LinkedIn media webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "linkedin")
        
        # Handle the media message
        response = linkedin_adapter.handle_media_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling LinkedIn media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process LinkedIn media")

async def _handle_webchat_media_webhook(request: Request, db: Session):
    """Handle WebChat media webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        
        # Determine brand ID from the message
        brand_id = _determine_brand_id_from_chat(json_data, "webchat")
        
        # Handle the media message
        response = webchat_adapter.handle_media_webhook(json_data, conversation_manager, db, brand_id)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WebChat media webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WebChat media")

# Status webhook handlers

async def _handle_whatsapp_status_webhook(request: Request, db: Session):
    """Handle WhatsApp status webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        # Handle the status update
        response = whatsapp_adapter.handle_status_webhook(request_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp status")

async def _handle_telegram_status_webhook(request: Request, db: Session):
    """Handle Telegram status webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the status update
        response = telegram_adapter.handle_status_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Telegram status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram status")

async def _handle_instagram_status_webhook(request: Request, db: Session):
    """Handle Instagram status webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the status update
        response = instagram_adapter.handle_status_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Instagram status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram status")

async def _handle_facebook_status_webhook(request: Request, db: Session):
    """Handle Facebook status webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the status update
        response = facebook_adapter.handle_status_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Facebook status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Facebook status")

async def _handle_linkedin_status_webhook(request: Request, db: Session):
    """Handle LinkedIn status webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the status update
        response = linkedin_adapter.handle_status_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling LinkedIn status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process LinkedIn status")

async def _handle_webchat_status_webhook(request: Request, db: Session):
    """Handle WebChat status webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the status update
        response = webchat_adapter.handle_status_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WebChat status webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WebChat status")

# Typing webhook handlers

async def _handle_whatsapp_typing_webhook(request: Request, db: Session):
    """Handle WhatsApp typing webhook"""
    try:
        # Get request data
        form_data = await request.form()
        request_data = dict(form_data)
        
        # Get JSON data if available
        try:
            json_data = await request.json()
            request_data.update(json_data)
        except:
            pass
        
        # Handle the typing indicator
        response = whatsapp_adapter.handle_typing_webhook(request_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WhatsApp typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp typing")

async def _handle_telegram_typing_webhook(request: Request, db: Session):
    """Handle Telegram typing webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the typing indicator
        response = telegram_adapter.handle_typing_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Telegram typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram typing")

async def _handle_instagram_typing_webhook(request: Request, db: Session):
    """Handle Instagram typing webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the typing indicator
        response = instagram_adapter.handle_typing_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Instagram typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Instagram typing")

async def _handle_facebook_typing_webhook(request: Request, db: Session):
    """Handle Facebook typing webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the typing indicator
        response = facebook_adapter.handle_typing_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling Facebook typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process Facebook typing")

async def _handle_linkedin_typing_webhook(request: Request, db: Session):
    """Handle LinkedIn typing webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the typing indicator
        response = linkedin_adapter.handle_typing_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling LinkedIn typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process LinkedIn typing")

async def _handle_webchat_typing_webhook(request: Request, db: Session):
    """Handle WebChat typing webhook"""
    try:
        # Get request data
        json_data = await request.json()
        
        # Handle the typing indicator
        response = webchat_adapter.handle_typing_webhook(json_data, db)
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling WebChat typing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process WebChat typing")

# Helper functions

def _determine_brand_id_from_chat(data: Dict[str, Any], channel: str) -> int:
    """Determine brand ID from chat message data"""
    try:
        # Try to extract brand ID from various sources based on channel
        if channel == "whatsapp":
            # Check if message contains brand identifier
            body = data.get('Body', '')
            if 'brand:' in body.lower():
                # Extract brand ID from message
                import re
                match = re.search(r'brand:(\d+)', body.lower())
                if match:
                    return int(match.group(1))
            
            # Check if from number contains brand identifier
            from_number = data.get('From', '')
            if from_number:
                # This is a simplified approach - in production, you'd have a mapping
                if '+1800' in from_number:
                    return 1  # Default brand
                elif '+911800' in from_number:
                    return 1  # Default brand for India
        
        elif channel == "telegram":
            # Check if message contains brand identifier
            text = data.get('message', {}).get('text', '')
            if 'brand:' in text.lower():
                import re
                match = re.search(r'brand:(\d+)', text.lower())
                if match:
                    return int(match.group(1))
        
        elif channel == "instagram":
            # Check if message contains brand identifier
            text = data.get('entry', [{}])[0].get('messaging', [{}])[0].get('message', {}).get('text', '')
            if 'brand:' in text.lower():
                import re
                match = re.search(r'brand:(\d+)', text.lower())
                if match:
                    return int(match.group(1))
        
        elif channel == "facebook":
            # Check if message contains brand identifier
            text = data.get('entry', [{}])[0].get('messaging', [{}])[0].get('message', {}).get('text', '')
            if 'brand:' in text.lower():
                import re
                match = re.search(r'brand:(\d+)', text.lower())
                if match:
                    return int(match.group(1))
        
        elif channel == "linkedin":
            # Check if message contains brand identifier
            text = data.get('message', {}).get('text', '')
            if 'brand:' in text.lower():
                import re
                match = re.search(r'brand:(\d+)', text.lower())
                if match:
                    return int(match.group(1))
        
        elif channel == "webchat":
            # WebChat typically includes brand_id in the message
            brand_id = data.get('brand_id')
            if brand_id:
                return int(brand_id)
        
        # Default to brand ID 1 if no specific mapping found
        return 1
        
    except Exception as e:
        logger.error(f"Error determining brand ID from chat: {e}")
        return 1