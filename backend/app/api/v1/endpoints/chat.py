from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.v1 import deps
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine
from app import crud, schemas
import logging
import uuid
from typing import List, Optional

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for frontend chat sessions
FRONTEND_CHAT_SESSIONS = {}

@router.post("/send")
async def send_chat_message(
    message_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user_optional)
):
    """
    Send a message to the AI chat bot and get a response.
    """
    try:
        message = message_data.get("message", "").strip()
        session_id = message_data.get("sessionId")
        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        if not session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")

        # Initialize AI engine and conversation manager
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db=db, ai_engine=ai_engine)
        brand_id = 1

        # Process the message through the conversation manager
        bot_response = conversation_manager.process_message(
            session_id=session_id,
            user_message=message,
            brand_id=brand_id,
            channel="webchat"
        )

        # Store messages in memory
        if session_id not in FRONTEND_CHAT_SESSIONS:
            FRONTEND_CHAT_SESSIONS[session_id] = []
        FRONTEND_CHAT_SESSIONS[session_id].append({
            "sender": "user",
            "text": message,
            "timestamp": str(uuid.uuid4())
        })
        FRONTEND_CHAT_SESSIONS[session_id].append({
            "sender": "bot",
            "text": bot_response,
            "timestamp": str(uuid.uuid4())
        })

        # Return the bot response in the expected format
        return {
            "sender": "bot",
            "text": bot_response,
            "timestamp": str(uuid.uuid4())
        }

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return {
            "sender": "bot",
            "text": "I apologize, but I'm having trouble processing your message right now. Please try again or contact support if the issue persists.",
            "timestamp": str(uuid.uuid4())
        }

@router.get("/history/{ticket_id}")
async def get_chat_history(
    ticket_id: int = None,
    session_id: str = None,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user_optional)
):
    """
    Get chat history for a specific session or ticket.
    """
    try:
        # If session_id is provided, return its messages
        if session_id and session_id in FRONTEND_CHAT_SESSIONS:
            return {"messages": FRONTEND_CHAT_SESSIONS[session_id]}
        # Otherwise, fallback to mock data
        return {
            "messages": [
                {
                    "sender": "bot",
                    "text": "Hello! I'm here to help you with your complaint. How can I assist you today?",
                    "timestamp": "2024-01-01T10:00:00Z"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return {"messages": []}

@router.post("/start/{ticket_id}")
async def start_chat(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[dict] = Depends(deps.get_current_user_optional)
):
    """
    Start a new chat session for a ticket.
    """
    try:
        session_id = str(uuid.uuid4())
        # Initialize empty message list for this session
        FRONTEND_CHAT_SESSIONS[session_id] = []
        return {
            "success": True,
            "session_id": session_id,
            "message": "Chat session started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to start chat session") 