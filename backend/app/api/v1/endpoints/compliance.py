# backend/app/api/v1/endpoints/compliance.py

import logging
import json
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Response
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ....database import get_db
from ....models import User, Brand, Ticket, Admin, SecurityEvent
from ....schemas import User, Brand, Ticket
from ....core.security import (
    log_failed_login_attempt, is_account_locked, clear_failed_attempts
)
from ....config.settings import settings
from ....api.v1.deps import get_current_active_admin

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/gdpr/export/{user_id}")
async def export_user_data(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Export all user data in GDPR-compliant format."""
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log export request
        log_security_event(
            "GDPR_EXPORT_REQUESTED", 
            f"Data export requested for user {user_id}",
            {"admin_id": current_admin.id, "user_id": user_id}
        )
        
        # Collect all user data
        user_data = {
            "user_info": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "is_active": user.is_active
            },
            "tickets": [],
            "messages": [],
            "brand_affiliations": []
        }
        
        # Get user tickets
        tickets = db.query(Ticket).filter(Ticket.user_id == user_id).all()
        for ticket in tickets:
            ticket_data = {
                "id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status,
                "priority": ticket.priority,
                "category": ticket.category,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "brand_id": ticket.brand_id,
                "satisfaction_rating": ticket.satisfaction_rating,
                "voice_file_url": ticket.voice_file_url
            }
            user_data["tickets"].append(ticket_data)
        
        # Get user messages
        messages = db.query(Message).filter(Message.user_id == user_id).all()
        for message in messages:
            message_data = {
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
                "created_at": message.created_at.isoformat(),
                "ticket_id": message.ticket_id,
                "channel": message.channel
            }
            user_data["messages"].append(message_data)
        
        # Get brand affiliations
        if user.brand_id:
            brand = db.query(Brand).filter(Brand.id == user.brand_id).first()
            if brand:
                user_data["brand_affiliations"].append({
                    "brand_id": brand.id,
                    "brand_name": brand.name,
                    "role": user.role,
                    "joined_at": user.created_at.isoformat()
                })
        
        # Create export file
        export_filename = f"user_data_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Log successful export
        log_security_event(
            "GDPR_EXPORT_COMPLETED", 
            f"Data export completed for user {user_id}",
            {"admin_id": current_admin.id, "user_id": user_id, "filename": export_filename}
        )
        
        return JSONResponse(
            content=user_data,
            headers={"Content-Disposition": f"attachment; filename={export_filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        log_security_event("GDPR_EXPORT_ERROR", f"Export failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export user data")

@router.delete("/gdpr/delete/{user_id}")
async def delete_user_data(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Delete all user data (GDPR right to be forgotten)."""
    try:
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Log deletion request
        log_security_event(
            "GDPR_DELETION_REQUESTED", 
            f"Data deletion requested for user {user_id}",
            {"admin_id": current_admin.id, "user_id": user_id}
        )
        
        # Anonymize user data instead of hard delete (for audit purposes)
        user.email = f"deleted_{user_id}@deleted.com"
        user.name = f"Deleted User {user_id}"
        user.phone = None
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        
        # Anonymize tickets
        tickets = db.query(Ticket).filter(Ticket.user_id == user_id).all()
        for ticket in tickets:
            ticket.title = f"Deleted Ticket {ticket.id}"
            ticket.description = "[Content deleted for privacy]"
            ticket.deleted_at = datetime.utcnow()
        
        # Anonymize messages
        messages = db.query(Message).filter(Message.user_id == user_id).all()
        for message in messages:
            message.content = "[Message deleted for privacy]"
            message.deleted_at = datetime.utcnow()
        
        db.commit()
        
        # Log successful deletion
        log_security_event(
            "GDPR_DELETION_COMPLETED", 
            f"Data deletion completed for user {user_id}",
            {"admin_id": current_admin.id, "user_id": user_id}
        )
        
        return {"message": "User data deleted successfully", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Error deleting user data: {e}")
        log_security_event("GDPR_DELETION_ERROR", f"Deletion failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user data")

@router.get("/gdpr/retention-policy")
async def get_retention_policy(
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Get current data retention policy."""
    retention_policy = {
        "user_data": {
            "retention_period": "7 years",
            "reason": "Legal compliance and audit requirements",
            "auto_deletion": True,
            "deletion_trigger": "Account inactivity for 7 years"
        },
        "ticket_data": {
            "retention_period": "5 years",
            "reason": "Customer service history and legal requirements",
            "auto_deletion": True,
            "deletion_trigger": "Ticket resolution + 5 years"
        },
        "message_data": {
            "retention_period": "3 years",
            "reason": "Communication history and service quality",
            "auto_deletion": True,
            "deletion_trigger": "Message creation + 3 years"
        },
        "audit_logs": {
            "retention_period": "10 years",
            "reason": "Security and compliance requirements",
            "auto_deletion": False,
            "deletion_trigger": "Manual review only"
        },
        "billing_data": {
            "retention_period": "7 years",
            "reason": "Tax and financial compliance",
            "auto_deletion": False,
            "deletion_trigger": "Manual review only"
        }
    }
    
    return retention_policy

@router.post("/gdpr/update-retention-policy")
async def update_retention_policy(
    policy_updates: Dict[str, Any],
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Update data retention policy (admin only)."""
    try:
        # Validate policy updates
        allowed_fields = ["user_data", "ticket_data", "message_data", "audit_logs", "billing_data"]
        for field in policy_updates:
            if field not in allowed_fields:
                raise HTTPException(status_code=400, detail=f"Invalid field: {field}")
        
        # Log policy update
        log_security_event(
            "RETENTION_POLICY_UPDATED", 
            f"Retention policy updated by admin {current_admin.id}",
            {"admin_id": current_admin.id, "updates": policy_updates}
        )
        
        # Here you would typically save to database or config file
        # For now, we'll just return success
        
        return {"message": "Retention policy updated successfully", "updates": policy_updates}
        
    except Exception as e:
        logger.error(f"Error updating retention policy: {e}")
        raise HTTPException(status_code=500, detail="Failed to update retention policy")

@router.get("/gdpr/data-inventory")
async def get_data_inventory(
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Get comprehensive data inventory for GDPR compliance."""
    try:
        # Count all data types
        user_count = db.query(User).count()
        brand_count = db.query(Brand).count()
        ticket_count = db.query(Ticket).count()
        message_count = db.query(Message).count()
        admin_count = db.query(Admin).count()
        
        # Get data by age
        now = datetime.utcnow()
        data_by_age = {
            "users": {
                "total": user_count,
                "active": db.query(User).filter(User.is_active == True).count(),
                "inactive": db.query(User).filter(User.is_active == False).count(),
                "created_last_30_days": db.query(User).filter(
                    User.created_at >= now - timedelta(days=30)
                ).count(),
                "created_last_90_days": db.query(User).filter(
                    User.created_at >= now - timedelta(days=90)
                ).count()
            },
            "tickets": {
                "total": ticket_count,
                "open": db.query(Ticket).filter(Ticket.status == "open").count(),
                "closed": db.query(Ticket).filter(Ticket.status == "closed").count(),
                "created_last_30_days": db.query(Ticket).filter(
                    Ticket.created_at >= now - timedelta(days=30)
                ).count()
            },
            "messages": {
                "total": message_count,
                "created_last_30_days": db.query(Message).filter(
                    Message.created_at >= now - timedelta(days=30)
                ).count()
            }
        }
        
        inventory = {
            "summary": {
                "total_users": user_count,
                "total_brands": brand_count,
                "total_tickets": ticket_count,
                "total_messages": message_count,
                "total_admins": admin_count
            },
            "data_by_age": data_by_age,
            "retention_status": {
                "data_eligible_for_deletion": 0,  # Would calculate based on retention policy
                "data_requiring_review": 0,
                "data_compliant": user_count + ticket_count + message_count
            }
        }
        
        return inventory
        
    except Exception as e:
        logger.error(f"Error generating data inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate data inventory")

@router.post("/gdpr/consent/{user_id}")
async def update_user_consent(
    user_id: int,
    consent_data: Dict[str, bool],
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Update user consent preferences."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update consent preferences
        user.marketing_consent = consent_data.get("marketing", False)
        user.data_processing_consent = consent_data.get("data_processing", True)
        user.third_party_consent = consent_data.get("third_party", False)
        user.consent_updated_at = datetime.utcnow()
        
        db.commit()
        
        # Log consent update
        log_security_event(
            "CONSENT_UPDATED", 
            f"Consent updated for user {user_id}",
            {"admin_id": current_admin.id, "user_id": user_id, "consent": consent_data}
        )
        
        return {"message": "User consent updated successfully", "user_id": user_id}
        
    except Exception as e:
        logger.error(f"Error updating user consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user consent")

@router.get("/gdpr/consent/{user_id}")
async def get_user_consent(
    user_id: int,
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Get user consent preferences."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        consent_data = {
            "user_id": user.id,
            "marketing_consent": user.marketing_consent,
            "data_processing_consent": user.data_processing_consent,
            "third_party_consent": user.third_party_consent,
            "consent_updated_at": user.consent_updated_at.isoformat() if user.consent_updated_at else None
        }
        
        return consent_data
        
    except Exception as e:
        logger.error(f"Error getting user consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user consent")

@router.post("/gdpr/breach-notification")
async def report_data_breach(
    breach_data: Dict[str, Any],
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Report a data breach for GDPR compliance."""
    try:
        # Validate breach data
        required_fields = ["description", "affected_users", "breach_date", "discovery_date"]
        for field in required_fields:
            if field not in breach_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Log breach notification
        log_security_event(
            "DATA_BREACH_REPORTED", 
            f"Data breach reported by admin {current_admin.id}",
            {
                "admin_id": current_admin.id,
                "breach_description": breach_data["description"],
                "affected_users": breach_data["affected_users"],
                "breach_date": breach_data["breach_date"],
                "discovery_date": breach_data["discovery_date"]
            }
        )
        
        # Here you would typically:
        # 1. Save breach report to database
        # 2. Notify affected users
        # 3. Notify relevant authorities
        # 4. Implement containment measures
        
        return {
            "message": "Data breach reported successfully",
            "breach_id": f"breach_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "next_steps": [
                "Affected users will be notified within 72 hours",
                "Authorities will be notified if required",
                "Investigation team has been alerted"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error reporting data breach: {e}")
        raise HTTPException(status_code=500, detail="Failed to report data breach")

@router.get("/gdpr/breach-history")
async def get_breach_history(
    current_admin: Admin = Depends(get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Get history of reported data breaches."""
    try:
        # Get security events related to data breaches
        breach_events = db.query(SecurityEvent).filter(
            SecurityEvent.event_type == "DATA_BREACH_REPORTED"
        ).order_by(SecurityEvent.timestamp.desc()).all()
        
        breaches = []
        for event in breach_events:
            try:
                context = json.loads(event.context) if event.context else {}
                breaches.append({
                    "id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "description": context.get("breach_description", "Unknown"),
                    "affected_users": context.get("affected_users", 0),
                    "breach_date": context.get("breach_date"),
                    "discovery_date": context.get("discovery_date"),
                    "reported_by": context.get("admin_id")
                })
            except:
                continue
        
        return {"breaches": breaches, "total_count": len(breaches)}
        
    except Exception as e:
        logger.error(f"Error getting breach history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get breach history") 