# backend/app/api/v1/endpoints/conversation.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
import uuid

from app.api.v1.deps import get_db, get_current_user
from app.core.conversation_manager import ConversationManager
from app.core.ai_engine import AIEngine
from app.models import User, Brand, ConversationSession, ConversationTurn, FollowUpTemplate

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/process-message")
def process_message(
    session_id: str,
    message: str,
    brand_id: int,
    channel: str = "web",
    language: str = "en",
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process a user message with contextual follow-ups"""
    try:
        # Check if user has access to this brand
        if current_user.role != "admin" and current_user.brand_id != brand_id:
            raise HTTPException(status_code=403, detail="Access denied to this brand")
        
        ai_engine = AIEngine()
        conversation_manager = ConversationManager(db, ai_engine)
        
        result = conversation_manager.process_message(
            session_id=session_id,
            user_message=message,
            brand_id=brand_id,
            channel=channel,
            language=language,
            user_id=user_id or current_user.id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "response": result
        }
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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