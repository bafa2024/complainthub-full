# backend/app/api/v1/endpoints/brand_management.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.api.v1 import deps
from app.models import User, Brand, Ticket, PhoneNumber, Transaction
from app.services.telephony import TelephonyService
from app.services.billing import BillingService
from app.services.analytics import AnalyticsService
from app.services.notification_service import NotificationService
from app.services.seo_indexing_service import SEOIndexingService
from app.tasks.brand_tasks import process_brand_analytics_task, send_brand_notifications_task
import logging
from sqlalchemy import and_

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================================================
# PHONE NUMBER MANAGEMENT
# ============================================================================

@router.get("/phone-numbers/providers")
async def get_telephony_providers(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get available telephony providers"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        telephony_service = TelephonyService(db)
        providers = telephony_service.get_providers()
        
        return {
            "success": True,
            "providers": providers
        }
        
    except Exception as e:
        logger.error(f"Error getting telephony providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get providers")

@router.get("/phone-numbers/search")
async def search_available_numbers(
    country_code: str = Query("IN", description="Country code"),
    number_type: str = Query("toll-free", description="Number type"),
    capabilities: str = Query("voice,sms", description="Comma-separated capabilities"),
    provider: str = Query("twilio", description="Provider name"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Search for available phone numbers"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        telephony_service = TelephonyService(db)
        capabilities_list = [cap.strip() for cap in capabilities.split(",")]
        
        numbers = telephony_service.search_numbers(
            country_code=country_code,
            number_type=number_type,
            capabilities=capabilities_list,
            provider=provider
        )
        
        return {
            "success": True,
            "numbers": numbers
        }
        
    except Exception as e:
        logger.error(f"Error searching numbers: {e}")
        raise HTTPException(status_code=500, detail="Failed to search numbers")

@router.post("/phone-numbers/purchase")
async def purchase_phone_number(
    purchase_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Purchase a phone number"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        telephony_service = TelephonyService(db)
        result = telephony_service.purchase_number(
            phone_number=purchase_data["phone_number"],
            provider=purchase_data["provider"],
            brand_id=current_user.brand_id,
            capabilities=purchase_data.get("capabilities", ["voice", "sms"])
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing number: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase number")

@router.get("/phone-numbers")
async def get_brand_phone_numbers(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get all phone numbers for the brand"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        phone_numbers = db.query(PhoneNumber).filter(
            PhoneNumber.brand_id == current_user.brand_id
        ).all()
        
        return {
            "success": True,
            "phone_numbers": [
                {
                    "id": pn.id,
                    "phone_number": pn.phone_number,
                    "provider": pn.provider,
                    "number_type": pn.number_type,
                    "capabilities": pn.capabilities,
                    "status": pn.status,
                    "monthly_cost": pn.monthly_cost,
                    "webhook_url": pn.webhook_url,
                    "created_at": pn.created_at.isoformat()
                }
                for pn in phone_numbers
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting phone numbers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone numbers")

@router.patch("/phone-numbers/{phone_number}/status")
async def update_phone_number_status(
    phone_number: str,
    status_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update phone number status"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        pn = db.query(PhoneNumber).filter(
            and_(
                PhoneNumber.phone_number == phone_number,
                PhoneNumber.brand_id == current_user.brand_id
            )
        ).first()
        
        if not pn:
            raise HTTPException(status_code=404, detail="Phone number not found")
        
        pn.status = status_data["status"]
        pn.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Phone number status updated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating phone number status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")

@router.delete("/phone-numbers/{phone_number}")
async def release_phone_number(
    phone_number: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Release a phone number"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        telephony_service = TelephonyService(db)
        result = telephony_service.release_number(
            phone_number=phone_number,
            brand_id=current_user.brand_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error releasing number: {e}")
        raise HTTPException(status_code=500, detail="Failed to release number")

# ============================================================================
# BILLING & CREDIT SYSTEM
# ============================================================================

@router.get("/billing/summary")
async def get_billing_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get billing summary for the brand"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        summary = billing_service.get_billing_summary(current_user.brand_id)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting billing summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing summary")

@router.get("/billing/transactions")
async def get_billing_transactions(
    limit: int = Query(50, description="Number of transactions to return"),
    offset: int = Query(0, description="Number of transactions to skip"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get billing transaction history"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        transactions = billing_service.get_transactions(
            brand_id=current_user.brand_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "transactions": transactions
        }
        
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")

@router.post("/billing/topup")
async def create_credit_topup(
    topup_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a credit top-up payment"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        result = billing_service.process_credit_topup(
            brand_id=current_user.brand_id,
            amount=topup_data["amount"],
            payment_method=topup_data.get("payment_method", "stripe")
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating topup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create topup")

@router.post("/billing/confirm-payment")
async def confirm_payment(
    payment_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Confirm payment and add credits"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        result = billing_service.confirm_payment(payment_data["payment_intent_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm payment")

@router.get("/billing/plans")
async def get_subscription_plans(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get available subscription plans"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        plans = billing_service.get_subscription_plans()
        
        return {
            "success": True,
            "plans": plans
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plans")

@router.post("/billing/subscription/create")
async def create_subscription(
    subscription_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a subscription"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        billing_service = BillingService(db)
        result = billing_service.create_subscription(
            brand_id=current_user.brand_id,
            plan_type=subscription_data["plan_type"],
            payment_method_id=subscription_data["payment_method_id"]
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

# ============================================================================
# ANALYTICS & INSIGHTS
# ============================================================================

@router.get("/analytics/overview")
async def get_brand_analytics(
    date_range: str = Query("30d", description="Date range for analytics"),
    start_date: Optional[str] = Query(None, description="Custom start date"),
    end_date: Optional[str] = Query(None, description="Custom end date"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get brand analytics overview"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        analytics_service = AnalyticsService(db)
        analytics = analytics_service.get_brand_analytics(
            brand_id=current_user.brand_id,
            date_range=date_range,
            start_date=start_date,
            end_date=end_date
        )
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting brand analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/analytics/tat")
async def get_tat_analytics(
    date_range: str = Query("30d", description="Date range for TAT analysis"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get TAT (Turnaround Time) analytics"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        analytics_service = AnalyticsService(db)
        tat_data = analytics_service.get_tat_analytics(
            brand_id=current_user.brand_id,
            date_range=date_range
        )
        
        return {
            "success": True,
            "tat_analytics": tat_data
        }
        
    except Exception as e:
        logger.error(f"Error getting TAT analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get TAT analytics")

@router.get("/analytics/abuse-patterns")
async def get_abuse_pattern_analytics(
    date_range: str = Query("30d", description="Date range for abuse analysis"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get abuse pattern analytics"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        analytics_service = AnalyticsService(db)
        abuse_data = analytics_service.get_abuse_pattern_analytics(
            brand_id=current_user.brand_id,
            date_range=date_range
        )
        
        return {
            "success": True,
            "abuse_analytics": abuse_data
        }
        
    except Exception as e:
        logger.error(f"Error getting abuse analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get abuse analytics")

@router.get("/analytics/team-performance")
async def get_team_performance_analytics(
    date_range: str = Query("30d", description="Date range for team analysis"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get team performance analytics"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        analytics_service = AnalyticsService(db)
        team_data = analytics_service.get_team_performance_analytics(
            brand_id=current_user.brand_id,
            date_range=date_range
        )
        
        return {
            "success": True,
            "team_analytics": team_data
        }
        
    except Exception as e:
        logger.error(f"Error getting team analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get team analytics")

@router.post("/analytics/export")
async def export_analytics_report(
    report_type: str,
    format: str = Query("csv", description="Export format"),
    filters: Dict[str, Any] = None,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Export analytics report"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        background_tasks.add_task(
            process_brand_analytics_task,
            brand_id=current_user.brand_id,
            report_type=report_type,
            format=format,
            filters=filters
        )
        
        return {
            "success": True,
            "message": "Report generation started",
            "task_id": f"export_{datetime.utcnow().timestamp()}"
        }
        
    except Exception as e:
        logger.error(f"Error exporting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to export analytics")

# ============================================================================
# NOTIFICATIONS & ALERTS
# ============================================================================

@router.get("/notifications")
async def get_user_notifications(
    limit: int = Query(50, description="Number of notifications to return"),
    offset: int = Query(0, description="Number of notifications to skip"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get user notifications"""
    try:
        notification_service = NotificationService(db)
        notifications = notification_service.get_user_notifications(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        return notifications
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Mark notification as read"""
    try:
        notification_service = NotificationService(db)
        result = notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user.id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification read")

@router.get("/notifications/stats")
async def get_notification_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get notification statistics"""
    try:
        notification_service = NotificationService(db)
        stats = notification_service.get_notification_stats(user_id=current_user.id)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notification stats")

@router.post("/notifications/send")
async def send_brand_notification(
    notification_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Send notification to brand users"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        background_tasks.add_task(
            send_brand_notifications_task,
            brand_id=current_user.brand_id,
            notification_type=notification_data["type"],
            data=notification_data["data"],
            channels=notification_data.get("channels", ["email", "in_app"])
        )
        
        return {
            "success": True,
            "message": "Notification queued for delivery"
        }
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

# ============================================================================
# COMPLAINT MANAGEMENT ENHANCEMENTS
# ============================================================================

@router.post("/tickets/{ticket_id}/escalate")
async def escalate_ticket(
    ticket_id: int,
    escalation_data: Dict[str, Any] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Escalate a ticket"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.id == ticket_id,
                Ticket.brand_id == current_user.brand_id
            )
        ).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket status
        ticket.status = "escalated"
        ticket.updated_at = datetime.utcnow()
        
        # Send escalation notification
        notification_service = NotificationService(db)
        notification_service.send_escalation_notification(ticket_id)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Ticket escalated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error escalating ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to escalate ticket")

@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    assignment_data: Dict[str, Any],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Assign a ticket to a team member"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        ticket = db.query(Ticket).filter(
            and_(
                Ticket.id == ticket_id,
                Ticket.brand_id == current_user.brand_id
            )
        ).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Verify assignee is from the same brand
        assignee = db.query(User).filter(
            and_(
                User.id == assignment_data["assignee_id"],
                User.brand_id == current_user.brand_id,
                User.role == "brand_user"
            )
        ).first()
        
        if not assignee:
            raise HTTPException(status_code=400, detail="Invalid assignee")
        
        ticket.assignee_id = assignment_data["assignee_id"]
        ticket.updated_at = datetime.utcnow()
        
        # Send assignment notification
        notification_service = NotificationService(db)
        notification_service.send_notification(
            user_id=assignee.id,
            notification_type="ticket_assigned",
            data={
                "ticket_id": ticket.id,
                "ticket_title": ticket.title,
                "assigned_by": current_user.full_name
            }
        )
        
        db.commit()
        
        return {
            "success": True,
            "message": "Ticket assigned successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning ticket: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign ticket")

# ============================================================================
# SEO & STATIC PAGE GENERATION
# ============================================================================

@router.post("/seo/generate-pages")
async def generate_brand_seo_pages(
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Generate SEO pages for brand complaints"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        seo_service = SEOIndexingService(db)
        result = seo_service.bulk_generate_static_pages_for_brand(
            brand_id=current_user.brand_id
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error generating SEO pages: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SEO pages")

@router.get("/seo/analytics")
async def get_brand_seo_analytics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Get SEO analytics for the brand"""
    try:
        if current_user.role.value != "brand_user":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        seo_service = SEOIndexingService(db)
        analytics = seo_service.get_seo_analytics(
            brand_id=current_user.brand_id
        )
        
        return {
            "success": True,
            "seo_analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error getting SEO analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SEO analytics") 