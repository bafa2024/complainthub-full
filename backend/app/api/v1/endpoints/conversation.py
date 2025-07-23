# backend/app/api/v1/endpoints/conversation.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import uuid

from app.api.v1.deps import get_db, get_current_user
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine
from app.models import User, Brand, ConversationSession, ConversationTurn, FollowUpTemplate, Ticket

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/chat")
async def process_chat_message(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a chat message from user and return AI response.
    This is the main conversational AI endpoint.
    """
    try:
        logger.info(f"Processing chat message from user {current_user.id}")
        
        message = request.get("message", "")
        brand_id = request.get("brand_id")
        channel_type = request.get("channel_type", "webchat")
        language = request.get("language", "en")
        brand_context = request.get("brand_context", "")
        
        # Initialize AI engine
        ai_engine = AIEngine()
        
        # Get or create conversation session
        session_id = request.get("session_id") or str(uuid.uuid4())
        
        # Get conversation history (simplified for now)
        conversation_history = []
        
        # Process message with AI
        ai_response = await process_message_with_ai(
            message, conversation_history, brand_context, language, current_user.id, ai_engine
        )
        
        # If AI suggests creating a ticket, create it
        ticket_id = None
        if ai_response.get("create_ticket", False):
            ticket_data = ai_response.get("ticket_data", {})
            try:
                # Create ticket using ticket service
                from app.services.ticket_service import TicketService
                ticket_service = TicketService(db)
                
                ticket = ticket_service.create_ticket(
                    title=ticket_data.get("title", "Customer inquiry via chat"),
                    description=ticket_data.get("description", message),
                    category=ticket_data.get("category", "complaint"),
                    urgency=ticket_data.get("urgency", "medium"),
                    user_id=current_user.id,
                    brand_id=brand_id,
                    language=language,
                    channel=channel_type,
                    metadata={
                        "session_id": session_id,
                        "ai_analysis": ai_response.get("metadata", {}),
                        "sentiment_score": ticket_data.get("sentiment_score", 0.0),
                        "toxicity_score": ticket_data.get("metadata", {}).get("toxicity_score", 0.0)
                    }
                )
                
                ticket_id = ticket.id
                logger.info(f"Created ticket {ticket_id} from conversation session {session_id}")
                
            except Exception as e:
                logger.error(f"Failed to create ticket from conversation: {e}")
                # Continue without ticket creation
        
        return {
            "success": True,
            "response": ai_response["response"],
            "session_id": session_id,
            "metadata": ai_response.get("metadata", {}),
            "requires_followup": ai_response.get("requires_followup", False),
            "ticket_created": ai_response.get("create_ticket", False),
            "ticket_id": ticket_id,
            "suggested_actions": ai_response.get("suggested_actions", [])
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_message_with_ai(
    message: str, 
    conversation_history: List[Dict[str, Any]], 
    brand_context: str = "",
    language: str = "en",
    user_id: int = None,
    ai_engine: AIEngine = None
) -> Dict[str, Any]:
    """Process message with AI engine and return structured response."""
    try:
        if not ai_engine:
            ai_engine = AIEngine()
            
        # Detect language if not specified
        if not language or language == "auto":
            language_detection = ai_engine.detect_language(message)
            language = language_detection["language_code"]
        
        # Analyze message with context
        analysis = ai_engine.analyze_text_with_context(message, brand_context)
        
        # Determine if this is a complete complaint or needs follow-up
        follow_up_needed = should_ask_followup(analysis, conversation_history)
        
        if follow_up_needed:
            # Generate follow-up question
            response = ai_engine.generate_follow_up_question(
                conversation_history, brand_context, language
            )
            
            return {
                "response": response,
                "requires_followup": True,
                "create_ticket": False,
                "metadata": {
                    "analysis": analysis,
                    "language": language,
                    "conversation_turns": len(conversation_history)
                }
            }
        else:
            # Generate final response and prepare ticket data
            response = generate_completion_response(analysis, language)
            ticket_data = extract_ticket_data(analysis, conversation_history, brand_context)
            
            return {
                "response": response,
                "requires_followup": False,
                "create_ticket": True,
                "ticket_data": ticket_data,
                "metadata": {
                    "analysis": analysis,
                    "language": language,
                    "conversation_turns": len(conversation_history)
                },
                "suggested_actions": ["create_ticket", "send_confirmation"]
            }
        
    except Exception as e:
        logger.error(f"Error processing message with AI: {e}")
        return {
            "response": "I understand your concern. Let me help you with that. Could you please provide more details?",
            "requires_followup": True,
            "create_ticket": False,
            "metadata": {"error": str(e)}
        }

def should_ask_followup(analysis: Dict[str, Any], conversation_history: List[Dict[str, Any]]) -> bool:
    """Determine if follow-up questions are needed."""
    try:
        # Check conversation length (max 5 turns)
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        if len(user_messages) >= 5:
            return False  # Stop asking questions after 5 user messages
        
        # Check if essential information is missing
        intent_analysis = analysis.get("intent_analysis", {})
        
        # For complaints, check for essential details
        if intent_analysis.get("category") == "complaint":
            extracted_details = intent_analysis.get("extracted_details", "")
            
            # Check for missing order number, product details, etc.
            missing_info = []
            if not any(keyword in extracted_details.lower() for keyword in ["order", "#", "product", "item"]):
                missing_info.append("product_order_info")
            
            if not any(keyword in extracted_details.lower() for keyword in ["date", "when", "yesterday", "today"]):
                missing_info.append("date_info")
            
            return len(missing_info) > 0
        
        # For other categories, check if we have enough detail
        if len(intent_analysis.get("extracted_details", "")) < 20:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error determining follow-up need: {e}")
        return False

def generate_completion_response(analysis: Dict[str, Any], language: str) -> str:
    """Generate completion response when conversation is done."""
    try:
        intent_analysis = analysis.get("intent_analysis", {})
        category = intent_analysis.get("category", "complaint")
        
        responses = {
            "en": {
                "complaint": "Thank you for providing the details. I've recorded your complaint and created a ticket for you. Our team will review this and get back to you within 24 hours. You'll receive a confirmation email shortly with your ticket number.",
                "feedback": "Thank you for your valuable feedback. We've recorded your suggestions and will share them with the relevant team for consideration.",
                "support": "Thank you for reaching out. I've created a support ticket for your inquiry. Our technical team will assist you shortly.",
                "general": "Thank you for contacting us. I've recorded your message and our team will respond to you soon."
            },
            "hi": {
                "complaint": "विवरण प्रदान करने के लिए धन्यवाद। मैंने आपकी शिकायत दर्ज की है और आपके लिए एक टिकट बनाया है। हमारी टीम इसकी समीक्षा करेगी और 24 घंटों के भीतर आपसे संपर्क करेगी।",
                "feedback": "आपकी मूल्यवान प्रतिक्रिया के लिए धन्यवाद। हमने आपके सुझावों को दर्ज किया है।",
                "support": "संपर्क करने के लिए धन्यवाद। मैंने आपकी पूछताछ के लिए एक सहायता टिकट बनाया है।",
                "general": "हमसे संपर्क करने के लिए धन्यवाद। मैंने आपका संदेश दर्ज किया है।"
            }
        }
        
        lang_responses = responses.get(language, responses["en"])
        return lang_responses.get(category, lang_responses["general"])
        
    except Exception as e:
        logger.error(f"Error generating completion response: {e}")
        return "Thank you for contacting us. We've recorded your message and will respond soon."

def extract_ticket_data(
    analysis: Dict[str, Any], 
    conversation_history: List[Dict[str, Any]], 
    brand_context: str
) -> Dict[str, Any]:
    """Extract ticket data from conversation analysis."""
    try:
        intent_analysis = analysis.get("intent_analysis", {})
        sentiment_analysis = analysis.get("sentiment_analysis", {})
        
        # Combine all user messages
        user_messages = [msg.get("content", "") for msg in conversation_history if msg.get("role") == "user"]
        full_conversation = "\n".join(user_messages)
        
        return {
            "title": intent_analysis.get("title", "Customer inquiry via chat"),
            "description": full_conversation,
            "category": intent_analysis.get("category", "complaint"),
            "urgency": intent_analysis.get("urgency", "medium"),
            "abuse_flag": intent_analysis.get("abuse_flag", False),
            "sentiment_score": sentiment_analysis.get("combined_sentiment", {}).get("sentiment_score", 0.0),
            "extracted_details": intent_analysis.get("extracted_details", ""),
            "language": analysis.get("language_info", {}).get("language_code", "en"),
            "channel": "webchat",
            "metadata": {
                "conversation_turns": len(conversation_history),
                "ai_confidence": intent_analysis.get("ml_confidence", 0.5),
                "toxicity_score": analysis.get("toxicity_analysis", {}).get("toxicity_score", 0.0)
            }
        }
        
    except Exception as e:
        logger.error(f"Error extracting ticket data: {e}")
        return {
            "title": "Customer inquiry via chat",
            "description": "Customer contacted via chat",
            "category": "complaint",
            "urgency": "medium",
            "abuse_flag": False
        }

@router.get("/session/{session_id}/history")
def get_conversation_history(
    session_id: str,
    brand_id: int,
    limit: int = Query(20, description="Number of turns to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history for a session"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        history = conversation_manager.get_conversation_history(session_id, brand_id, limit)
        
        return {
            "success": True,
            "session_id": session_id,
            "history": history,
            "total_turns": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/resume")
def resume_conversation(
    session_id: str,
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resume an existing conversation"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        result = conversation_manager.resume_conversation(session_id, brand_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "session_id": session_id,
            "response": result
        }
        
    except Exception as e:
        logger.error(f"Error resuming conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}/close")
def close_conversation(
    session_id: str,
    brand_id: int,
    reason: str = Query("completed", description="Reason for closing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close a conversation session"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        success = conversation_manager.close_conversation(session_id, brand_id, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Conversation closed: {reason}"
        }
        
    except Exception as e:
        logger.error(f"Error closing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/context")
def get_session_context(
    session_id: str,
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get session context information"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        # Get session
        session = db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id,
            ConversationSession.brand_id == brand_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get context from conversation manager
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        context = conversation_manager._get_session_context(session.id)
        
        return {
            "success": True,
            "session_id": session_id,
            "context": context,
            "session_info": {
                "status": session.status,
                "language": session.language,
                "channel": session.channel,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "context_summary": session.context_summary
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting session context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/follow-up-templates")
def create_follow_up_template(
    brand_id: int,
    template_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a follow-up template for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        # Validate required fields
        required_fields = ["trigger_intent", "follow_up_type", "template_text"]
        for field in required_fields:
            if field not in template_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create template
        template = FollowUpTemplate(
            brand_id=brand_id,
            trigger_intent=template_data["trigger_intent"],
            trigger_urgency=template_data.get("trigger_urgency"),
            trigger_entities=template_data.get("trigger_entities"),
            follow_up_type=template_data["follow_up_type"],
            template_text=template_data["template_text"],
            variables=template_data.get("variables"),
            language=template_data.get("language", "en"),
            priority=template_data.get("priority", 1)
        )
        
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return {
            "success": True,
            "template_id": template.id,
            "message": "Follow-up template created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating follow-up template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/follow-up-templates")
def get_follow_up_templates(
    brand_id: int,
    trigger_intent: Optional[str] = None,
    follow_up_type: Optional[str] = None,
    language: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get follow-up templates for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        query = db.query(FollowUpTemplate).filter(
            FollowUpTemplate.brand_id == brand_id,
            FollowUpTemplate.is_active == True
        )
        
        if trigger_intent:
            query = query.filter(FollowUpTemplate.trigger_intent == trigger_intent)
        
        if follow_up_type:
            query = query.filter(FollowUpTemplate.follow_up_type == follow_up_type)
        
        if language:
            query = query.filter(FollowUpTemplate.language == language)
        
        templates = query.order_by(FollowUpTemplate.priority.asc()).all()
        
        return {
            "success": True,
            "templates": [
                {
                    "id": template.id,
                    "trigger_intent": template.trigger_intent,
                    "trigger_urgency": template.trigger_urgency,
                    "trigger_entities": template.trigger_entities,
                    "follow_up_type": template.follow_up_type,
                    "template_text": template.template_text,
                    "variables": template.variables,
                    "language": template.language,
                    "priority": template.priority,
                    "usage_count": template.usage_count,
                    "success_rate": template.success_rate,
                    "created_at": template.created_at.isoformat()
                }
                for template in templates
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting follow-up templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/follow-up-templates/{template_id}")
def update_follow_up_template(
    template_id: int,
    template_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a follow-up template"""
    try:
        template = db.query(FollowUpTemplate).filter(
            FollowUpTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != template.brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this template")
        
        # Update fields
        updateable_fields = [
            "trigger_intent", "trigger_urgency", "trigger_entities", 
            "follow_up_type", "template_text", "variables", "language", 
            "priority", "is_active"
        ]
        
        for field in updateable_fields:
            if field in template_data:
                setattr(template, field, template_data[field])
        
        db.commit()
        db.refresh(template)
        
        return {
            "success": True,
            "template_id": template.id,
            "message": "Follow-up template updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating follow-up template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/follow-up-templates/{template_id}")
def delete_follow_up_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a follow-up template"""
    try:
        template = db.query(FollowUpTemplate).filter(
            FollowUpTemplate.id == template_id
        ).first()
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != template.brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this template")
        
        # Soft delete by setting is_active to False
        template.is_active = False
        db.commit()
        
        return {
            "success": True,
            "template_id": template.id,
            "message": "Follow-up template deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting follow-up template: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/active-sessions")
def get_active_sessions(
    brand_id: int,
    limit: int = Query(50, description="Number of sessions to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active conversation sessions for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        sessions = db.query(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationSession.status == "active"
        ).order_by(ConversationSession.last_activity.desc()).limit(limit).all()
        
        return {
            "success": True,
            "sessions": [
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "ticket_id": session.ticket_id,
                    "channel": session.channel,
                    "language": session.language,
                    "status": session.status,
                    "context_summary": session.context_summary,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "turn_count": db.query(ConversationTurn).filter(
                        ConversationTurn.session_id == session.id
                    ).count()
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/brand/{brand_id}/analyze-context")
def analyze_message_with_context(
    brand_id: int,
    message: str,
    context: Optional[str] = "",
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze a message with conversation context"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        # If session_id provided, get session context
        if session_id:
            session = db.query(ConversationSession).filter(
                ConversationSession.session_id == session_id,
                ConversationSession.brand_id == brand_id
            ).first()
            
            if session:
                recent_turns = conversation_manager._get_recent_conversation_turns(session.id)
                session_context = conversation_manager._get_session_context(session.id)
                context = conversation_manager._build_context_string(recent_turns, session_context)
        
        # Analyze with context
        analysis = ai_engine.analyze_text_with_context(
            text=message,
            context=context,
            brand_id=brand_id
        )
        
        return {
            "success": True,
            "message": message,
            "context": context,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing message with context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brand/{brand_id}/conversation-stats")
def get_conversation_statistics(
    brand_id: int,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation statistics for a brand"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get session statistics
        total_sessions = db.query(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationSession.created_at >= cutoff_date
        ).count()
        
        active_sessions = db.query(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationSession.status == "active",
            ConversationSession.last_activity >= cutoff_date
        ).count()
        
        completed_sessions = db.query(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationSession.status == "completed",
            ConversationSession.updated_at >= cutoff_date
        ).count()
        
        # Get turn statistics
        total_turns = db.query(ConversationTurn).join(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationTurn.created_at >= cutoff_date
        ).count()
        
        # Get average turns per session
        avg_turns_per_session = total_turns / total_sessions if total_sessions > 0 else 0
        
        # Get follow-up statistics
        follow_up_turns = db.query(ConversationTurn).join(ConversationSession).filter(
            ConversationSession.brand_id == brand_id,
            ConversationTurn.follow_up_required == True,
            ConversationTurn.created_at >= cutoff_date
        ).count()
        
        return {
            "success": True,
            "statistics": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "completed_sessions": completed_sessions,
                "total_turns": total_turns,
                "avg_turns_per_session": round(avg_turns_per_session, 2),
                "follow_up_turns": follow_up_turns,
                "follow_up_rate": round((follow_up_turns / total_turns * 100), 2) if total_turns > 0 else 0,
                "analysis_period_days": days
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 