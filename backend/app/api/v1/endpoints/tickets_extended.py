from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.models import User, Ticket, TicketStatusEnum, TicketCategoryEnum, TicketUrgencyEnum
from app import crud, schemas
from app.services.speech.deepgram import deepgram_service
from app.core.ai_engine import AIEngine
from app.services.followup_service import FollowUpService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update ticket status"""
    try:
        ticket = crud.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check if user has permission (brand user or admin)
        if current_user.role == models.RoleEnum.brand_user and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Map status string to enum
        status_map = {
            "new": TicketStatusEnum.new,
            "open": TicketStatusEnum.open,
            "in-progress": TicketStatusEnum.in_progress,
            "resolved": TicketStatusEnum.resolved,
            "closed": TicketStatusEnum.closed
        }
        
        if status not in status_map:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Update ticket status
        ticket_update = schemas.TicketUpdate(status=status_map[status])
        updated_ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
        
        if status == "resolved":
            # Schedule follow-up workflow
            followup_service = FollowUpService(db)
            
            # Get user contact information
            user = db.query(User).filter(User.id == ticket.owner_id).first()
            if user:
                # Schedule follow-up based on original channel
                followup_result = followup_service.schedule_follow_up(
                    ticket_id=ticket_id,
                    delay_hours=24  # 24 hours after resolution
                )
                
                if followup_result["success"]:
                    logger.info(f"Follow-up scheduled for ticket {ticket_id}")
                else:
                    logger.warning(f"Failed to schedule follow-up for ticket {ticket_id}: {followup_result['error']}")
        
        return {"success": True, "new_status": status}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ticket status: {str(e)}")

@router.post("/{ticket_id}/responses")
async def add_ticket_response(
    ticket_id: int,
    message: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Add response to ticket"""
    try:
        ticket = crud.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # For now, just update the ticket description with the response
        # In a full implementation, you'd have a separate TicketResponse model
        current_description = ticket.description or ""
        new_description = f"{current_description}\n\nResponse from {current_user.full_name or current_user.email}:\n{message}"
        
        ticket_update = schemas.TicketUpdate(description=new_description)
        crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
        
        # TODO: Send notification to user
        # send_notification(
        #     user_id=ticket.owner_id,
        #     type="ticket_response",
        #     data={"ticket_id": ticket_id, "message": message[:100]}
        # )
        
        return {"success": True, "message": "Response added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add response: {str(e)}")

@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: int,
    rating: int,
    comment: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Rate ticket resolution"""
    try:
        ticket = crud.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Verify user owns the ticket
        if ticket.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Verify ticket is resolved
        if ticket.status != TicketStatusEnum.resolved:
            raise HTTPException(status_code=400, detail="Can only rate resolved tickets")
        
        # Update ticket with rating
        ticket_update = schemas.TicketUpdate(
            satisfaction_rating=rating
        )
        crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
        
        return {"success": True, "rating": rating}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rate ticket: {str(e)}")

@router.post("/voice")
async def upload_voice_complaint(
    audio: UploadFile = File(...),
    metadata: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Upload voice complaint with enhanced processing"""
    try:
        print(f"Voice complaint submission - User: {current_user.id}, Email: {current_user.email}")
        
        # Parse metadata
        meta = json.loads(metadata) if metadata else {}
        print(f"Metadata received: {meta}")
        
        # Validate required fields
        if not meta.get("brand_id"):
            raise HTTPException(status_code=400, detail="Brand ID is required")
        
        if not meta.get("title"):
            raise HTTPException(status_code=400, detail="Title is required")
        
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads/voice", exist_ok=True)
        
        # Save audio file
        timestamp = datetime.utcnow().timestamp()
        file_path = f"uploads/voice/{current_user.id}_{timestamp}.webm"
        with open(file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Process audio with Deepgram
        language = meta.get("language", "en")
        transcription_result = await deepgram_service.transcribe_audio_file(file_path, language)
        
        # Extract transcription and sentiment
        transcript = transcription_result.get("transcript", meta.get("description", "Voice recording submitted"))
        sentiment_score = transcription_result.get("sentiment_score", 0.0)
        confidence = transcription_result.get("confidence", 0.8)
        
        # Use AI engine to analyze the transcript
        ai_engine = AIEngine()
        analysis = ai_engine.classify_intent_and_extract_details(transcript)
        
        # Determine category and urgency from AI analysis
        category = analysis.get("category", meta.get("category", "complaint"))
        urgency = analysis.get("urgency", meta.get("priority", "medium"))
        
        # Map category string to enum
        category_map = {
            "complaint": TicketCategoryEnum.complaint,
            "suggestion": TicketCategoryEnum.suggestion,
            "feedback": TicketCategoryEnum.feedback,
            "support": TicketCategoryEnum.support
        }
        
        # Map urgency string to enum
        urgency_map = {
            "low": TicketUrgencyEnum.low,
            "medium": TicketUrgencyEnum.medium,
            "high": TicketUrgencyEnum.high,
            "urgent": TicketUrgencyEnum.high
        }
        
        print(f"Creating ticket with data: title={meta.get('title')}, brand_id={meta.get('brand_id')}, category={category}")
        
        # Create ticket using the proper CRUD function
        ticket_data = schemas.TicketCreate(
            title=meta.get("title"),
            description=transcript,
            brand_id=int(meta.get("brand_id")),
            category=category_map.get(category, TicketCategoryEnum.complaint),
            urgency=urgency_map.get(urgency, TicketUrgencyEnum.medium),
            channel="voice"
        )
        
        ticket = crud.create_ticket(db=db, ticket=ticket_data, owner_id=current_user.id)
        print(f"Ticket created with ID: {ticket.id}")
        
        # Update the ticket with voice-specific fields and AI analysis
        ticket.transcript = transcript
        ticket.voice_recording_url = file_path
        ticket.abuse_level_flag = analysis.get("abuse_flag", False)
        
        # Store additional analysis data in a JSON field or separate table
        # For now, we'll store it as a comment in the description
        analysis_summary = f"""
        AI Analysis:
        - Sentiment Score: {sentiment_score:.2f}
        - Confidence: {confidence:.2f}
        - Toxicity Score: {analysis.get('toxicity_score', 0.0):.2f}
        - Detected Language: {transcription_result.get('language', 'en')}
        - Entities: {', '.join([e['name'] for e in analysis.get('entities', [])])}
        """
        
        ticket.description = f"{transcript}\n\n{analysis_summary}"
        
        db.commit()
        db.refresh(ticket)
        
        print(f"Voice complaint processed successfully - Ticket ID: {ticket.id}")
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "transcript": transcript,
            "category": ticket.category.value,
            "urgency": ticket.urgency.value,
            "sentiment_score": sentiment_score,
            "confidence": confidence,
            "toxicity_score": analysis.get("toxicity_score", 0.0),
            "language": transcription_result.get("language", "en"),
            "entities": analysis.get("entities", []),
            "abuse_flag": analysis.get("abuse_flag", False)
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process voice complaint: {str(e)}")

@router.post("/voice/transcribe")
async def transcribe_audio_only(
    audio: UploadFile = File(...),
    language: str = "en",
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    """Transcribe audio without creating a ticket"""
    try:
        # Create temporary file
        temp_file_path = f"temp_audio_{current_user.id if current_user else 'anonymous'}_{datetime.utcnow().timestamp()}.webm"
        
        with open(temp_file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Transcribe with Deepgram
        transcription_result = await deepgram_service.transcribe_audio_file(temp_file_path, language)
        
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return {
            "success": True,
            "transcript": transcription_result.get("transcript", ""),
            "confidence": transcription_result.get("confidence", 0.0),
            "sentiment_score": transcription_result.get("sentiment_score", 0.0),
            "sentiment": transcription_result.get("sentiment", "neutral"),
            "language": transcription_result.get("language", language),
            "duration": transcription_result.get("duration", 0.0),
            "words": transcription_result.get("words", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

@router.get("/voice/languages")
async def get_supported_languages():
    """Get list of supported languages for voice transcription"""
    try:
        languages = deepgram_service.get_supported_languages()
        return {
            "success": True,
            "languages": languages,
            "count": len(languages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {str(e)}")

@router.post("/voice/analyze")
async def analyze_voice_sentiment(
    audio: UploadFile = File(...),
    language: str = "en",
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    """Analyze voice sentiment and extract insights"""
    try:
        # Create temporary file
        temp_file_path = f"temp_analysis_{current_user.id if current_user else 'anonymous'}_{datetime.utcnow().timestamp()}.webm"
        
        with open(temp_file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # Transcribe with Deepgram
        transcription_result = await deepgram_service.transcribe_audio_file(temp_file_path, language)
        
        # Analyze with AI engine
        ai_engine = AIEngine()
        analysis = ai_engine.classify_intent_and_extract_details(transcription_result.get("transcript", ""))
        
        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except:
            pass
        
        return {
            "success": True,
            "transcript": transcription_result.get("transcript", ""),
            "sentiment_analysis": {
                "deepgram_sentiment": transcription_result.get("sentiment", "neutral"),
                "deepgram_score": transcription_result.get("sentiment_score", 0.0),
                "ai_category": analysis.get("category", "complaint"),
                "ai_urgency": analysis.get("urgency", "medium"),
                "ai_toxicity_score": analysis.get("toxicity_score", 0.0),
                "ai_abuse_flag": analysis.get("abuse_flag", False),
                "ai_entities": analysis.get("entities", [])
            },
            "confidence": transcription_result.get("confidence", 0.0),
            "language": transcription_result.get("language", language),
            "duration": transcription_result.get("duration", 0.0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze voice: {str(e)}")

@router.get("/public")
async def get_public_complaints(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db)
):
    """Get public unresolved complaints"""
    try:
        # Only show complaints that are unresolved for > 48 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=48)
        
        complaints = db.query(Ticket).filter(
            Ticket.category == TicketCategoryEnum.complaint,
            Ticket.status != TicketStatusEnum.resolved,
            Ticket.created_at < cutoff_time,
            Ticket.is_public == True  # Brand can opt-out of public display
        ).offset(skip).limit(limit).all()
        
        # Anonymize user data
        public_complaints = []
        for complaint in complaints:
            days_unresolved = (datetime.utcnow() - complaint.created_at).days
            
            public_complaints.append({
                "id": complaint.id,
                "brand_name": complaint.brand.name if complaint.brand else "Unknown Brand",
                "description": (complaint.description or "")[:200] + "..." if complaint.description else "No description",
                "days_unresolved": days_unresolved,
                "created_at": complaint.created_at.isoformat()
            })
        
        return public_complaints
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch public complaints: {str(e)}")

@router.post("/{ticket_id}/auto-tag")
async def auto_tag_ticket(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Auto-tag a ticket using AI analysis"""
    try:
        # Get ticket
        ticket = crud.get_ticket(db, ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Check permissions
        if current_user.role == models.RoleEnum.brand_user and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Use AI engine to analyze the ticket
        ai_engine = AIEngine()
        
        # Analyze the ticket content
        analysis = ai_engine.classify_intent_and_extract_details(
            ticket.description or ticket.title,
            brand_context=f"Brand: {ticket.brand.name if ticket.brand else 'Unknown'}"
        )
        
        # Determine severity level based on AI analysis
        severity_level = 1  # Default medium
        
        # Use sentiment and toxicity scores to determine severity
        sentiment_score = analysis.get("sentiment_score", 0)
        toxicity_score = analysis.get("toxicity_score", 0)
        abuse_flag = analysis.get("abuse_flag", False)
        
        if abuse_flag or toxicity_score > 0.7:
            severity_level = 5  # Abuse
        elif toxicity_score > 0.5 or sentiment_score < -0.8:
            severity_level = 4  # Emergency
        elif toxicity_score > 0.3 or sentiment_score < -0.6:
            severity_level = 3  # Critical
        elif sentiment_score < -0.4:
            severity_level = 2  # High
        elif sentiment_score > 0.2:
            severity_level = 0  # Low
        
        # Determine urgency based on AI analysis
        urgency = analysis.get("urgency", "medium")
        
        # Update ticket with AI analysis
        ticket_update = schemas.TicketUpdate(
            severity_level=severity_level,
            urgency=urgency,
            abuse_level_flag=abuse_flag
        )
        
        updated_ticket = crud.update_ticket(db=db, ticket_id=ticket_id, ticket_update=ticket_update)
        
        # Store AI analysis results
        ai_analysis_data = {
            "sentiment_score": sentiment_score,
            "toxicity_score": toxicity_score,
            "confidence": analysis.get("ml_confidence", 0.8),
            "language": analysis.get("language", "en"),
            "entities": analysis.get("entities", []),
            "category": analysis.get("category"),
            "auto_tagged_at": datetime.utcnow().isoformat()
        }
        
        # Store AI analysis in ticket description or create a separate field
        # For now, we'll append it to the description
        if updated_ticket.description:
            ai_summary = f"\n\n--- AI Analysis ---\nSeverity: {severity_level} ({getSeverityLabel(severity_level)})\nUrgency: {urgency}\nAbuse Flag: {abuse_flag}\nSentiment: {sentiment_score:.2f}\nToxicity: {toxicity_score:.2f}\nConfidence: {analysis.get('ml_confidence', 0.8):.2f}"
            updated_ticket.description += ai_summary
        else:
            updated_ticket.description = f"AI Analysis:\nSeverity: {severity_level} ({getSeverityLabel(severity_level)})\nUrgency: {urgency}\nAbuse Flag: {abuse_flag}\nSentiment: {sentiment_score:.2f}\nToxicity: {toxicity_score:.2f}\nConfidence: {analysis.get('ml_confidence', 0.8):.2f}"
        
        db.commit()
        db.refresh(updated_ticket)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "auto_tagging_results": {
                "severity_level": severity_level,
                "severity_label": getSeverityLabel(severity_level),
                "urgency": urgency,
                "abuse_level_flag": abuse_flag,
                "sentiment_score": sentiment_score,
                "toxicity_score": toxicity_score,
                "confidence": analysis.get("ml_confidence", 0.8),
                "ai_analysis": ai_analysis_data
            },
            "message": "Ticket auto-tagged successfully using AI analysis"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-tagging ticket {ticket_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-tag ticket: {str(e)}")

def getSeverityLabel(severity_level):
    """Get human-readable severity label"""
    labels = {
        0: "Low",
        1: "Medium", 
        2: "High",
        3: "Critical",
        4: "Emergency",
        5: "Abuse"
    }
    return labels.get(severity_level, "Unknown")

# Helper functions (simplified for now)
def send_brand_notification(brand_id: int, ticket_id: int):
    """Send notification to brand about new complaint"""
    # TODO: Implement email/webhook notification
    pass

def schedule_follow_up_call(ticket_id: int, delay_hours: int = 24):
    """Schedule a follow-up call for a resolved ticket"""
    # This would integrate with a task queue like Celery
    # For now, just log the intention
    print(f"Scheduling follow-up call for ticket {ticket_id} in {delay_hours} hours")
    # TODO: Implement actual scheduling logic