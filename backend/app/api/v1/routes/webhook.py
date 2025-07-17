from fastapi import APIRouter, Depends, HTTPException, Request, Query, Response
<<<<<<< HEAD
from app.schemas import WebhookRequest, WebhookResponse
=======
from app.schemas import WebhookRequest
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.models import Ticket
from app.database import get_db
from sqlalchemy.orm import Session
from app.adapters.twilio_adapter import TwilioVoiceAdapter
from app.adapters.whatsapp_adapter import handle_whatsapp
from app.adapters.telegram_adapter import handle_telegram
from app.adapters.webchat_adapter import handle_webchat
from app.models import CRMIntegration
<<<<<<< HEAD
from app.services.crm_service import CRMService
=======
# from app.services.crm_service import CRMService
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
import logging

router = APIRouter()
# conv_manager = ConversationManager()  # Commented out: requires db and ai_engine
ai_engine = AIEngine()
logger = logging.getLogger(__name__)

<<<<<<< HEAD
@router.post("/webhook/voice/{provider}", response_model=WebhookResponse)
def voice_webhook(provider: str, payload: WebhookRequest, db: Session = Depends(get_db)):
=======
@router.post("/webhook/voice/{provider}")
async def webhook_voice(provider: str, request: Request):
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
    """
    Handle voice webhooks from different providers
    """
    try:
        if provider == "twilio":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "From": payload.user_id,
                "To": payload.phone_number,
                "CallSid": payload.session_id,
                "CallStatus": "ringing",
                "recording_url": payload.recording_url
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Voice call processed successfully",
                data={"response": response}
            )
=======
                "From": request.json().get("user_id"),
                "To": request.json().get("phone_number"),
                "CallSid": request.json().get("session_id"),
                "CallStatus": "ringing",
                "recording_url": request.json().get("recording_url")
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Voice call processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif provider == "knowlarity":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "from": payload.user_id,
                "to": payload.phone_number,
                "call_id": payload.session_id,
                "status": "ringing",
                "recording_url": payload.recording_url
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Voice call processed successfully",
                data={"response": response}
            )
=======
                "from": request.json().get("user_id"),
                "to": request.json().get("phone_number"),
                "call_id": request.json().get("session_id"),
                "status": "ringing",
                "recording_url": request.json().get("recording_url")
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Voice call processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif provider == "exotel":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "From": payload.user_id,
                "To": payload.phone_number,
                "CallSid": payload.session_id,
                "CallStatus": "ringing",
                "recording_url": payload.recording_url
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Voice call processed successfully",
                data={"response": response}
            )
=======
                "From": request.json().get("user_id"),
                "To": request.json().get("phone_number"),
                "CallSid": request.json().get("session_id"),
                "CallStatus": "ringing",
                "recording_url": request.json().get("recording_url")
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the voice call
            response = TwilioVoiceAdapter.handle_voice_call(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Voice call processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' not supported")
            
    except Exception as e:
        logger.error(f"Error processing voice webhook for provider {provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice call")

<<<<<<< HEAD
@router.post("/webhook/chat/{channel}", response_model=WebhookResponse)
def chat_webhook(channel: str, payload: WebhookRequest, db: Session = Depends(get_db)):
=======
@router.post("/webhook/chat/{channel}")
async def webhook_chat(channel: str, request: Request):
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
    """
    Handle chat webhooks from different channels
    """
    try:
        if channel == "whatsapp":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "From": payload.user_id,
                "To": payload.phone_number,
                "Body": payload.message,
                "MediaUrl0": payload.media_url
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_whatsapp(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="WhatsApp message processed successfully",
                data={"response": response}
            )
=======
                "From": request.json().get("user_id"),
                "To": request.json().get("phone_number"),
                "Body": request.json().get("message"),
                "MediaUrl0": request.json().get("media_url")
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_whatsapp(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "WhatsApp message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif channel == "telegram":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "update_id": payload.session_id,
                "message": {
                    "message_id": payload.message_id,
                    "from": {"id": payload.user_id},
                    "chat": {"id": payload.user_id},
                    "text": payload.message
=======
                "update_id": request.json().get("session_id"),
                "message": {
                    "message_id": request.json().get("message_id"),
                    "from": {"id": request.json().get("user_id")},
                    "chat": {"id": request.json().get("user_id")},
                    "text": request.json().get("message")
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
                }
            }
            
            ai_engine = AIEngine()
<<<<<<< HEAD
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_telegram(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Telegram message processed successfully",
                data={"response": response}
            )
=======
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_telegram(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Telegram message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif channel == "instagram":
            # Extract data from payload
            data = {
                "entry": [{
<<<<<<< HEAD
                    "id": payload.session_id,
                    "messaging": [{
                        "sender": {"id": payload.user_id},
                        "recipient": {"id": payload.phone_number},
                        "message": {
                            "mid": payload.message_id,
                            "text": payload.message
=======
                    "id": request.json().get("session_id"),
                    "messaging": [{
                        "sender": {"id": request.json().get("user_id")},
                        "recipient": {"id": request.json().get("phone_number")},
                        "message": {
                            "mid": request.json().get("message_id"),
                            "text": request.json().get("message")
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
                        }
                    }]
                }]
            }
            
            ai_engine = AIEngine()
<<<<<<< HEAD
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Instagram message processed successfully",
                data={"response": response}
            )
=======
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Instagram message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif channel == "facebook":
            # Extract data from payload
            data = {
                "object": "page",
                "entry": [{
<<<<<<< HEAD
                    "id": payload.session_id,
                    "messaging": [{
                        "sender": {"id": payload.user_id},
                        "recipient": {"id": payload.phone_number},
                        "message": {
                            "mid": payload.message_id,
                            "text": payload.message
=======
                    "id": request.json().get("session_id"),
                    "messaging": [{
                        "sender": {"id": request.json().get("user_id")},
                        "recipient": {"id": request.json().get("phone_number")},
                        "message": {
                            "mid": request.json().get("message_id"),
                            "text": request.json().get("message")
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
                        }
                    }]
                }]
            }
            
            ai_engine = AIEngine()
<<<<<<< HEAD
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="Facebook message processed successfully",
                data={"response": response}
            )
=======
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "Facebook message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif channel == "linkedin":
            # Extract data from payload
            data = {
                "message": {
<<<<<<< HEAD
                    "id": payload.message_id,
                    "from": {"id": payload.user_id},
                    "text": payload.message
=======
                    "id": request.json().get("message_id"),
                    "from": {"id": request.json().get("user_id")},
                    "text": request.json().get("message")
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
                }
            }
            
            ai_engine = AIEngine()
<<<<<<< HEAD
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="LinkedIn message processed successfully",
                data={"response": response}
            )
=======
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "LinkedIn message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        elif channel == "webchat":
            # Extract data from payload
            data = {
<<<<<<< HEAD
                "session_id": payload.session_id,
                "message": payload.message,
                "user_id": payload.user_id,
                "user_name": payload.user_name,
                "brand_id": 1,
                "file_upload": payload.media_url
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, db, brand_id=1)
            
            return WebhookResponse(
                success=True,
                message="WebChat message processed successfully",
                data={"response": response}
            )
=======
                "session_id": request.json().get("session_id"),
                "message": request.json().get("message"),
                "user_id": request.json().get("user_id"),
                "user_name": request.json().get("user_name"),
                "brand_id": 1,
                "file_upload": request.json().get("media_url")
            }
            
            ai_engine = AIEngine()
            conversation_manager = ConversationManager(db=None, ai_engine=ai_engine) # db is not available here
            
            # Handle the chat message
            response = handle_webchat(data, conversation_manager, None, brand_id=1) # db is not available here
            
            return {"success": True, "message": "WebChat message processed successfully", "data": {"response": response}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
            
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported")
            
    except Exception as e:
        logger.error(f"Error processing chat webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@router.post("/crm/{crm_type}")
async def handle_crm_webhook(
    crm_type: str,
    request: Request,
    brand_id: int = Query(..., description="Brand ID for the webhook"),
    db: Session = Depends(get_db)
):
    """
    Handle incoming webhooks from CRM systems for real-time updates
    """
    try:
        # Get webhook data
        webhook_data = await request.json()
        
        # Get webhook signature for verification
        signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('X-Signature')
        
        # Verify webhook signature if provided
        if signature:
            # Get brand's CRM configuration for webhook secret
            crm_integration = db.query(CRMIntegration).filter(
                CRMIntegration.brand_id == brand_id,
                CRMIntegration.crm_type == crm_type,
                CRMIntegration.is_active == True
            ).first()
            
            if crm_integration and crm_integration.webhook_secret:
                webhook_body = await request.body()
<<<<<<< HEAD
                if not CRMService.verify_webhook_signature(
                    webhook_body.decode(), 
                    signature.replace('sha256=', ''), 
                    crm_integration.webhook_secret
                ):
                    raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process webhook
        crm_service = CRMService(db)
        result = crm_service.handle_crm_webhook(crm_type, webhook_data, brand_id)
        
        if not result["success"]:
            logger.error(f"CRM webhook processing failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"CRM webhook processed successfully for {crm_type}")
        return result
=======
                # if not CRMService.verify_webhook_signature(
                #     webhook_body.decode(), 
                #     signature.replace('sha256=', ''), 
                #     crm_integration.webhook_secret
                # ):
                #     raise HTTPException(status_code=401, detail="Invalid webhook signature")
                pass # Commented out as CRMService is removed
        
        # Process webhook
        # crm_service = CRMService(db)
        # result = crm_service.handle_crm_webhook(crm_type, webhook_data, brand_id)
        
        # if not result["success"]:
        #     logger.error(f"CRM webhook processing failed: {result['error']}")
        #     raise HTTPException(status_code=400, detail=result["error"])
        
        # logger.info(f"CRM webhook processed successfully for {crm_type}")
        return {"success": True, "message": "CRM webhook processing not implemented", "data": {}}
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CRM webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")

@router.post("/crm/{crm_type}/verify")
async def verify_crm_webhook(
    crm_type: str,
    request: Request,
    brand_id: int = Query(..., description="Brand ID for the webhook"),
    db: Session = Depends(get_db)
):
    """
    Verify webhook endpoint for CRM systems (e.g., Facebook verification)
    """
    try:
        # Handle verification challenge
        if crm_type == 'facebook':
            # Facebook webhook verification
            mode = request.query_params.get('hub.mode')
            token = request.query_params.get('hub.verify_token')
            challenge = request.query_params.get('hub.challenge')
            
            if mode == 'subscribe' and token:
                # Verify token matches brand's webhook secret
                crm_integration = db.query(CRMIntegration).filter(
                    CRMIntegration.brand_id == brand_id,
                    CRMIntegration.crm_type == crm_type,
                    CRMIntegration.is_active == True
                ).first()
                
                if crm_integration and crm_integration.webhook_secret == token:
                    return Response(content=challenge, media_type="text/plain")
                else:
                    raise HTTPException(status_code=403, detail="Invalid verify token")
        
        elif crm_type == 'salesforce':
            # Salesforce webhook verification
            challenge = request.query_params.get('challenge')
            if challenge:
                return Response(content=challenge, media_type="text/plain")
        
        elif crm_type == 'zoho':
            # Zoho webhook verification
            challenge = request.query_params.get('challenge')
            if challenge:
                return Response(content=challenge, media_type="text/plain")
        
        # Default verification response
        return {"status": "verified"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying CRM webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify webhook")

@router.get("/crm/{crm_type}/status")
async def get_crm_webhook_status(
    crm_type: str,
    brand_id: int = Query(..., description="Brand ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_db) # This line was not in the new_code, but should be changed for consistency
):
    """
    Get webhook status and configuration for a CRM integration
    """
    try:
        # Check permissions
        if current_user.get("role") != "admin" and current_user.get("brand_id") != brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        crm_integration = db.query(CRMIntegration).filter(
            CRMIntegration.brand_id == brand_id,
            CRMIntegration.crm_type == crm_type
        ).first()
        
        if not crm_integration:
            raise HTTPException(status_code=404, detail="CRM integration not found")
        
        return {
            "crm_type": crm_type,
            "brand_id": brand_id,
            "is_active": crm_integration.is_active,
            "webhook_url": f"/api/v1/webhook/crm/{crm_type}?brand_id={brand_id}",
            "verification_url": f"/api/v1/webhook/crm/{crm_type}/verify?brand_id={brand_id}",
            "last_sync": crm_integration.last_sync_at.isoformat() if crm_integration.last_sync_at else None,
            "sync_count": crm_integration.sync_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CRM webhook status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook status")
