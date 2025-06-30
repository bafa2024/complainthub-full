from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from app.api.v1 import deps
from app.models import User, Ticket

router = APIRouter()

@router.patch("/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update ticket status"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check if user has permission (brand user or admin)
    if current_user.role == "brand" and ticket.brand_id != current_user.brand_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    old_status = ticket.status
    ticket.status = status
    
    if status == "resolved":
        ticket.resolved_at = datetime.utcnow()
        # Trigger follow-up workflow
        schedule_follow_up_call(ticket_id, delay_hours=24)
    
    db.commit()
    
    # Log status change
    log_entry = TicketLog(
        ticket_id=ticket_id,
        user_id=current_user.id,
        action="status_change",
        details=f"Status changed from {old_status} to {status}"
    )
    db.add(log_entry)
    db.commit()
    
    return {"success": True, "new_status": status}

@router.post("/{ticket_id}/responses")
async def add_ticket_response(
    ticket_id: int,
    message: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Add response to ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    response = TicketResponse(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=message,
        created_at=datetime.utcnow()
    )
    db.add(response)
    db.commit()
    
    # Send notification to user
    send_notification(
        user_id=ticket.user_id,
        type="ticket_response",
        data={"ticket_id": ticket_id, "message": message[:100]}
    )
    
    return {"success": True, "response_id": response.id}

@router.post("/{ticket_id}/rate")
async def rate_ticket(
    ticket_id: int,
    rating: int,
    comment: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Rate ticket resolution"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify user owns the ticket
    if ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify ticket is resolved
    if ticket.status != "resolved":
        raise HTTPException(status_code=400, detail="Can only rate resolved tickets")
    
    ticket.rating = rating
    ticket.rating_comment = comment
    ticket.rated_at = datetime.utcnow()
    db.commit()
    
    return {"success": True, "rating": rating}

@router.post("/voice")
async def upload_voice_complaint(
    audio: UploadFile = File(...),
    metadata: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Upload voice complaint"""
    # Parse metadata
    meta = json.loads(metadata) if metadata else {}
    
    # Save audio file
    file_path = f"uploads/voice/{current_user.id}_{datetime.utcnow().timestamp()}.webm"
    with open(file_path, "wb") as f:
        content = await audio.read()
        f.write(content)
    
    # Process with speech-to-text
    transcript = await process_speech_to_text(file_path)
    
    # Analyze sentiment and category
    analysis = await analyze_complaint_text(transcript)
    
    # Create ticket
    ticket = Ticket(
        user_id=current_user.id,
        brand_id=meta.get("brand_id"),
        channel="voice",
        description=transcript,
        transcript=transcript,
        voice_recording_url=file_path,
        category=analysis.get("category", "complaint"),
        urgency=analysis.get("urgency", 1),
        sentiment_score=analysis.get("sentiment", 0),
        created_at=datetime.utcnow()
    )
    db.add(ticket)
    db.commit()
    
    # Notify brand
    send_brand_notification(ticket.brand_id, ticket.id)
    
    return {
        "success": True,
        "ticket_id": ticket.id,
        "transcript": transcript,
        "category": ticket.category
    }

@router.get("/public")
async def get_public_complaints(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(deps.get_db)
):
    """Get public unresolved complaints"""
    # Only show complaints that are unresolved for > 48 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=48)
    
    complaints = db.query(Ticket).filter(
        Ticket.category == "complaint",
        Ticket.status != "resolved",
        Ticket.created_at < cutoff_time,
        Ticket.is_public == True  # Brand can opt-out of public display
    ).offset(skip).limit(limit).all()
    
    # Anonymize user data
    public_complaints = []
    for complaint in complaints:
        days_unresolved = (datetime.utcnow() - complaint.created_at).days
        
        public_complaints.append({
            "id": complaint.id,
            "brand_name": complaint.brand.name,
            "description": complaint.description[:200] + "...",
            "days_unresolved": days_unresolved,
            "views": complaint.view_count,
            "location": complaint.user.city if complaint.user.city else "India",
            "created_at": complaint.created_at.isoformat()
        })
    
    return public_complaints

# Helper functions
async def process_speech_to_text(file_path: str) -> str:
    """Process audio file to text using Deepgram"""
    # Deepgram integration
    from deepgram import Deepgram
    dg_client = Deepgram(settings.DEEPGRAM_API_KEY)
    
    with open(file_path, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/webm'}
        response = await dg_client.transcription.prerecorded(
            source,
            {
                'punctuate': True,
                'language': 'en-IN',
                'model': 'general',
                'sentiment': True
            }
        )
    
    return response['results']['channels'][0]['alternatives'][0]['transcript']

async def analyze_complaint_text(text: str) -> dict:
    """Analyze complaint text for category and urgency"""
    # Use Google Cloud Natural Language API
    from google.cloud import language_v1
    client = language_v1.LanguageServiceClient()
    
    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT,
    )
    
    # Analyze sentiment
    sentiment = client.analyze_sentiment(
        request={'document': document}
    ).document_sentiment
    
    # Classify content
    categories = client.classify_text(
        request={'document': document}
    ).categories
    
    # Determine urgency based on sentiment and keywords
    urgency = 1  # Default medium
    if sentiment.score < -0.5:
        urgency = 2  # High
    if any(word in text.lower() for word in ['urgent', 'emergency', 'immediately']):
        urgency = 3  # Critical
    
    # Determine category
    category = "complaint"  # Default
    if any(word in text.lower() for word in ['suggest', 'recommendation', 'idea']):
        category = "suggestion"
    elif any(word in text.lower() for word in ['feedback', 'review']):
        category = "feedback"
    elif any(word in text.lower() for word in ['help', 'support', 'how to']):
        category = "support"
    
    return {
        "category": category,
        "urgency": urgency,
        "sentiment": sentiment.score
    }

def send_brand_notification(brand_id: int, ticket_id: int):
    """Send notification to brand about new complaint"""
    # Implementation for email/webhook notification
    pass

def schedule_follow_up_call(ticket_id: int, delay_hours: int):
    """Schedule follow-up call after resolution"""
    # Implementation for scheduling follow-up
    pass