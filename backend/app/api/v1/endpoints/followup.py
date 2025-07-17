# backend/app/api/v1/endpoints/followup.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.models import FollowUpLog, Ticket, User
from app.schemas import FollowUpLog as FollowUpLogSchema, FollowUpResponse, FollowUpStats
from app.services.followup_service import FollowUpService
from app.tasks.followup_tasks import execute_follow_up, retry_failed_followups
import logging
from fastapi import Request, Response

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/schedule/{ticket_id}")
async def schedule_follow_up(
    ticket_id: int,
    delay_hours: int = 24,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Schedule a follow-up for a resolved ticket
    """
    try:
        # Check if user has permission
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        if current_user.role.value == "brand_user" and ticket.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        followup_service = FollowUpService(db)
        result = followup_service.schedule_follow_up(ticket_id, delay_hours)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling follow-up: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule follow-up")

@router.post("/execute/{follow_up_id}")
async def execute_follow_up_endpoint(
    follow_up_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Execute a follow-up immediately
    """
    try:
        # Check if user has permission
        follow_up = db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(status_code=404, detail="Follow-up not found")
        
        if current_user.role.value == "brand_user" and follow_up.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Execute follow-up in background
        background_tasks.add_task(execute_follow_up.delay, follow_up_id)
        
        return {
            "success": True,
            "message": "Follow-up execution started",
            "follow_up_id": follow_up_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing follow-up: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute follow-up")

@router.post("/response")
async def handle_follow_up_response(
    response: FollowUpResponse,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
):
    """
    Handle user response to follow-up
    """
    try:
        from app.tasks.followup_tasks import process_follow_up_response
        
        # Process response in background
        background_tasks.add_task(
            process_follow_up_response.delay,
            response.follow_up_id,
            response.response,
            response.rating
        )
        
        return {
            "success": True,
            "message": "Response received and being processed"
        }
        
    except Exception as e:
        logger.error(f"Error handling follow-up response: {e}")
        raise HTTPException(status_code=500, detail="Failed to process response")

@router.get("/list")
async def list_follow_ups(
    ticket_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List follow-ups with filtering
    """
    try:
        query = db.query(FollowUpLog)
        
        # Apply filters
        if ticket_id:
            query = query.filter(FollowUpLog.ticket_id == ticket_id)
        
        if brand_id:
            query = query.filter(FollowUpLog.brand_id == brand_id)
        elif current_user.role.value == "brand_user":
            # Brand users can only see their brand's follow-ups
            query = query.filter(FollowUpLog.brand_id == current_user.brand_id)
        
        if status:
            query = query.filter(FollowUpLog.status == status)
        
        # Apply pagination
        total = query.count()
        follow_ups = query.offset(offset).limit(limit).all()
        
        return {
            "follow_ups": follow_ups,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing follow-ups: {e}")
        raise HTTPException(status_code=500, detail="Failed to list follow-ups")

@router.get("/stats")
async def get_follow_up_stats(
    brand_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get follow-up statistics
    """
    try:
        # Brand users can only see their brand's stats
        if current_user.role.value == "brand_user":
            brand_id = current_user.brand_id
        
        followup_service = FollowUpService(db)
        stats = followup_service.get_follow_up_stats(brand_id=brand_id, days=days)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting follow-up stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@router.post("/retry-failed")
async def retry_failed_follow_ups_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retry failed follow-ups
    """
    try:
        # Only admins can retry failed follow-ups
        if current_user.role.value != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Execute retry in background
        background_tasks.add_task(retry_failed_followups.delay)
        
        return {
            "success": True,
            "message": "Failed follow-ups retry started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying failed follow-ups: {e}")
        raise HTTPException(status_code=500, detail="Failed to retry follow-ups")

@router.get("/{follow_up_id}")
async def get_follow_up(
    follow_up_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Get specific follow-up details
    """
    try:
        follow_up = db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(status_code=404, detail="Follow-up not found")
        
        # Check permissions
        if current_user.role.value == "brand_user" and follow_up.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return follow_up
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting follow-up: {e}")
        raise HTTPException(status_code=500, detail="Failed to get follow-up")

@router.delete("/{follow_up_id}")
async def cancel_follow_up(
    follow_up_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Cancel a scheduled follow-up
    """
    try:
        follow_up = db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
        if not follow_up:
            raise HTTPException(status_code=404, detail="Follow-up not found")
        
        # Check permissions
        if current_user.role.value == "brand_user" and follow_up.brand_id != current_user.brand_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Only allow cancellation of scheduled follow-ups
        if follow_up.status != "scheduled":
            raise HTTPException(status_code=400, detail="Only scheduled follow-ups can be cancelled")
        
        follow_up.status = "cancelled"
        follow_up.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Follow-up cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling follow-up: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to cancel follow-up")

@router.post("/webhook/voice/follow-up-response")
async def handle_voice_follow_up_response(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """
    Handle voice follow-up response from Twilio
    """
    try:
        data = await request.form()
        digits = data.get('Digits', '')
        call_sid = data.get('CallSid', '')
        
        # Extract follow-up ID from call SID or other identifier
        # This would need to be implemented based on how you track call-to-follow-up mapping
        
        # For now, we'll use a simple approach
        # In production, you'd want to store the mapping in the database
        
        response = ""
        rating = None
        
        if digits == "1":
            response = "resolved"
        elif digits == "2":
            response = "not_resolved"
        elif digits == "3":
            # Handle rating collection
            response = "rating_request"
        else:
            response = "invalid"
        
        # Find the follow-up by call SID or other identifier
        # This is a simplified implementation
        follow_up = db.query(FollowUpLog).filter(
            FollowUpLog.status == "in_progress",
            FollowUpLog.channel == "voice"
        ).first()
        
        if follow_up:
            followup_service = FollowUpService(db)
            result = followup_service.handle_follow_up_response(
                follow_up_id=follow_up.id,
                response=response,
                rating=rating
            )
        
        # Return TwiML response
        from twilio.twiml.voice_response import VoiceResponse
        resp = VoiceResponse()
        
        if response == "resolved":
            resp.say("Thank you for confirming. Your issue has been marked as resolved.")
        elif response == "not_resolved":
            resp.say("We're sorry to hear that. Your ticket has been reopened and our team will contact you shortly.")
        elif response == "rating_request":
            resp.say("Please rate your experience from 1 to 5, where 5 is excellent.")
            resp.gather(num_digits=1, action="/api/v1/followup/webhook/voice/rating", method="POST")
        else:
            resp.say("Thank you for your time. Goodbye!")
        
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling voice follow-up response: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice response")

@router.post("/webhook/voice/rating")
async def handle_voice_rating(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """
    Handle voice rating response
    """
    try:
        data = await request.form()
        digits = data.get('Digits', '')
        
        rating = int(digits) if digits.isdigit() and 1 <= int(digits) <= 5 else None
        
        # Find the follow-up and update rating
        follow_up = db.query(FollowUpLog).filter(
            FollowUpLog.status == "in_progress",
            FollowUpLog.channel == "voice"
        ).first()
        
        if follow_up and rating:
            follow_up.rating = rating
            follow_up.responded_at = datetime.utcnow()
            follow_up.status = "completed"
            db.commit()
        
        # Return TwiML response
        from twilio.twiml.voice_response import VoiceResponse
        resp = VoiceResponse()
        
        if rating:
            resp.say(f"Thank you for rating us {rating} out of 5. We appreciate your feedback!")
        else:
            resp.say("Thank you for your time. Goodbye!")
        
        return Response(content=str(resp), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling voice rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to process rating") 