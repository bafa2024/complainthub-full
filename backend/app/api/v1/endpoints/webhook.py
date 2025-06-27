# backend/app/api/v1/endpoints/webhook.py

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.api.v1 import deps # CORRECTED IMPORT PATH
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{channel}")
async def handle_webhook(
    request: Request,
    channel: str,
    db: Session = Depends(deps.get_db),
):
    """
    Main webhook to handle incoming messages from various channels.
    """
    ai_engine = AIEngine()
    conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)

    try:
        # --- Adapter Logic (Simplified) ---
        # In a real app, you would have an adapter for each channel
        # to parse the request and extract necessary details.
        if channel == "twilio":
            data = await request.form()
            session_id = data.get("From") # User's phone number
            user_message = data.get("Body")
            brand_id = 1 # This should be determined from the 'To' number
        elif channel == "webchat":
            data = await request.json()
            session_id = data.get("session_id")
            user_message = data.get("message")
            brand_id = data.get("brand_id")
        else:
            raise HTTPException(status_code=400, detail=f"Channel '{channel}' not supported.")

        if not all([session_id, user_message, brand_id]):
            raise HTTPException(status_code=422, detail="Missing required fields in webhook payload.")

        logger.info(f"Processing message from session {session_id} on channel {channel}")
        
        # Process the message and get a response
        bot_response = conversation_manager.process_message(
            session_id=session_id,
            user_message=user_message,
            brand_id=brand_id,
            channel=channel
        )

        # --- Response Formatting (Simplified) ---
        # Format the response for the specific channel
        if channel == "twilio":
            # Twilio expects TwiML for SMS responses
            from twilio.twiml.messaging_response import MessagingResponse
            response = MessagingResponse()
            response.message(bot_response)
            return str(response)
        else: # For webchat and others
            return {"reply": bot_response}

    except Exception as e:
        logger.error(f"Error processing webhook for channel {channel}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message.")