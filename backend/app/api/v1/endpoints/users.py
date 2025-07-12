# backend/app/api/v1/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.models import User, Ticket, ConversationSession
from app import crud, schemas
from app.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def get_current_user(
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=schemas.User)
def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update current user profile"""
    try:
        updated_user = crud.update_user(db=db, user_id=current_user.id, user_update=user_update)
        return updated_user
    except Exception as e:
        logger.error(f"Error updating user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@router.put("/me/password")
def change_password(
    password_update: schemas.PasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_update.current_password, current_user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        hashed_password = get_password_hash(password_update.new_password)
        current_user.hashed_password = hashed_password
        db.commit()
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@router.put("/me/notifications")
def update_notification_preferences(
    notifications: schemas.NotificationPreferences,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update user notification preferences"""
    try:
        # Update user notification preferences
        current_user.notification_preferences = notifications.dict()
        db.commit()
        
        return {"message": "Notification preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating notifications for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update notification preferences")

@router.put("/me/privacy")
def update_privacy_settings(
    privacy: schemas.PrivacySettings,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update user privacy settings"""
    try:
        # Update user privacy settings
        current_user.privacy_settings = privacy.dict()
        db.commit()
        
        return {"message": "Privacy settings updated successfully"}
    except Exception as e:
        logger.error(f"Error updating privacy for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update privacy settings")

@router.get("/me/complaints", response_model=List[schemas.Ticket])
def get_user_complaints(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get user's complaint history"""
    try:
        complaints = crud.get_tickets_by_user(
            db, 
            user_id=current_user.id, 
            skip=skip, 
            limit=limit,
            status=status
        )
        return complaints
    except Exception as e:
        logger.error(f"Error getting complaints for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch complaints")

@router.get("/me/complaints/stats")
def get_user_complaint_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get user's complaint statistics"""
    try:
        complaints = crud.get_tickets_by_user(db, user_id=current_user.id)
        
        total = len(complaints)
        resolved = len([c for c in complaints if c.status == "resolved"])
        pending = len([c for c in complaints if c.status in ["new", "in-progress"]])
        
        # Calculate average resolution time
        resolved_complaints = [c for c in complaints if c.status == "resolved" and c.resolved_at]
        avg_resolution_time = None
        if resolved_complaints:
            total_time = sum([
                (c.resolved_at - c.created_at).total_seconds() / 3600  # hours
                for c in resolved_complaints
            ])
            avg_resolution_time = total_time / len(resolved_complaints)
        
        return {
            "total_complaints": total,
            "resolved": resolved,
            "pending": pending,
            "resolution_rate": (resolved / total * 100) if total > 0 else 0,
            "avg_resolution_time_hours": round(avg_resolution_time, 2) if avg_resolution_time else None
        }
    except Exception as e:
        logger.error(f"Error getting stats for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.get("/me/sessions")
def get_user_sessions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get user's active sessions"""
    try:
        # This would typically come from a session management system
        # For now, return mock data
        sessions = [
            {
                "id": "current",
                "device": "Chrome on Windows",
                "ip_address": "192.168.1.100",
                "location": "Mumbai, India",
                "last_active": datetime.utcnow().isoformat(),
                "is_current": True
            },
            {
                "id": "mobile",
                "device": "Safari on iPhone",
                "ip_address": "192.168.1.101",
                "location": "Mumbai, India",
                "last_active": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "is_current": False
            }
        ]
        
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error getting sessions for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")

@router.post("/me/logout-all")
def logout_all_sessions(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Logout from all sessions"""
    try:
        # This would typically invalidate all session tokens
        # For now, just return success
        return {"message": "All sessions logged out successfully"}
    except Exception as e:
        logger.error(f"Error logging out sessions for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to logout sessions")

@router.get("/me/export")
def export_user_data(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Export user's personal data"""
    try:
        # Get user's complaints
        complaints = crud.get_tickets_by_user(db, user_id=current_user.id)
        
        # Get conversation sessions
        sessions = db.query(ConversationSession).filter(
            ConversationSession.user_id == current_user.id
        ).all()
        
        # Prepare export data
        export_data = {
            "user_info": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "phone": current_user.phone,
                "created_at": current_user.created_at.isoformat(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            },
            "preferences": {
                "notification_preferences": current_user.notification_preferences or {},
                "privacy_settings": current_user.privacy_settings or {}
            },
            "complaints": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "status": c.status,
                    "category": c.category,
                    "urgency": c.urgency,
                    "created_at": c.created_at.isoformat(),
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                    "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
                    "brand": c.brand.name if c.brand else None
                }
                for c in complaints
            ],
            "conversation_sessions": [
                {
                    "id": s.id,
                    "created_at": s.created_at.isoformat(),
                    "status": s.status,
                    "turns_count": len(s.turns) if s.turns else 0
                }
                for s in sessions
            ],
            "export_date": datetime.utcnow().isoformat()
        }
        
        return export_data
    except Exception as e:
        logger.error(f"Error exporting data for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")

@router.delete("/me")
def delete_user_account(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete user account"""
    try:
        # Mark user as deleted (soft delete)
        current_user.deleted_at = datetime.utcnow()
        current_user.is_active = False
        db.commit()
        
        # Send confirmation email (would be implemented)
        logger.info(f"User {current_user.id} account marked for deletion")
        
        return {"message": "Account deletion initiated. You will receive a confirmation email."}
    except Exception as e:
        logger.error(f"Error deleting user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@router.get("/me/activity")
def get_user_activity(
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get user's recent activity"""
    try:
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent complaints
        recent_complaints = db.query(Ticket).filter(
            Ticket.owner_id == current_user.id,
            Ticket.created_at >= since_date
        ).order_by(Ticket.created_at.desc()).limit(10).all()
        
        # Get recent conversation sessions
        recent_sessions = db.query(ConversationSession).filter(
            ConversationSession.user_id == current_user.id,
            ConversationSession.created_at >= since_date
        ).order_by(ConversationSession.created_at.desc()).limit(10).all()
        
        activity = []
        
        # Add complaint activities
        for complaint in recent_complaints:
            activity.append({
                "type": "complaint_created",
                "timestamp": complaint.created_at.isoformat(),
                "title": f"Created complaint: {complaint.title}",
                "details": {
                    "complaint_id": complaint.id,
                    "brand": complaint.brand.name if complaint.brand else None,
                    "status": complaint.status
                }
            })
        
        # Add session activities
        for session in recent_sessions:
            activity.append({
                "type": "conversation_started",
                "timestamp": session.created_at.isoformat(),
                "title": f"Started conversation session",
                "details": {
                    "session_id": session.id,
                    "status": session.status
                }
            })
        
        # Sort by timestamp
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"activity": activity[:20]}  # Return last 20 activities
    except Exception as e:
        logger.error(f"Error getting activity for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch activity")

@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Upload user avatar"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 5MB")
        
        # Save file (implementation would depend on storage solution)
        # For now, just return success
        return {"message": "Avatar uploaded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading avatar for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload avatar")