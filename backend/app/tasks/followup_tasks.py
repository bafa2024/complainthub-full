# backend/app/tasks/followup_tasks.py

import logging
from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.followup_service import FollowUpService
from app.models import FollowUpLog, Ticket
from app.celery_app import celery_app
from typing import Optional

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.followup_tasks.execute_follow_up")
def execute_follow_up(self, follow_up_id: int):
    """
    Execute a scheduled follow-up
    """
    db = SessionLocal()
    try:
        logger.info(f"Executing follow-up {follow_up_id}")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"follow_up_id": follow_up_id, "status": "executing"}
        )
        
        # Execute follow-up
        followup_service = FollowUpService(db)
        result = followup_service.execute_follow_up(follow_up_id)
        
        # Update task status
        current_task.update_state(
            state="SUCCESS" if result["success"] else "FAILURE",
            meta={
                "follow_up_id": follow_up_id,
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Follow-up {follow_up_id} completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error executing follow-up {follow_up_id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "follow_up_id": follow_up_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        # Update follow-up status
        try:
            follow_up = db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
            if follow_up:
                follow_up.status = "failed"
                follow_up.error_message = str(e)
                follow_up.completed_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Error updating follow-up status: {db_error}")
        
        raise
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.check_pending_followups")
def check_pending_followups():
    """
    Check for pending follow-ups that should be executed
    """
    db = SessionLocal()
    try:
        logger.info("Checking for pending follow-ups")
        
        # Find follow-ups that are scheduled but past their time
        now = datetime.utcnow()
        pending_followups = db.query(FollowUpLog).filter(
            FollowUpLog.status == "scheduled",
            FollowUpLog.scheduled_time <= now
        ).all()
        
        logger.info(f"Found {len(pending_followups)} pending follow-ups")
        
        # Execute each pending follow-up
        for follow_up in pending_followups:
            try:
                execute_follow_up.delay(follow_up.id)
                logger.info(f"Scheduled follow-up {follow_up.id} for execution")
            except Exception as e:
                logger.error(f"Error scheduling follow-up {follow_up.id}: {e}")
        
        return {
            "success": True,
            "pending_count": len(pending_followups),
            "checked_at": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking pending follow-ups: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.auto_close_expired_tickets")
def auto_close_expired_tickets():
    """
    Automatically close tickets that have been resolved for 48 hours without response
    """
    db = SessionLocal()
    try:
        logger.info("Checking for expired tickets to auto-close")
        
        # Find tickets that were resolved 48+ hours ago but not confirmed
        cutoff_time = datetime.utcnow() - timedelta(hours=48)
        expired_tickets = db.query(Ticket).filter(
            Ticket.status == "resolved",
            Ticket.updated_at <= cutoff_time,
            Ticket.resolved_at.is_(None)  # Not manually confirmed
        ).all()
        
        logger.info(f"Found {len(expired_tickets)} expired tickets")
        
        followup_service = FollowUpService(db)
        closed_count = 0
        
        for ticket in expired_tickets:
            try:
                result = followup_service.auto_close_ticket(ticket.id)
                if result["success"]:
                    closed_count += 1
                    logger.info(f"Auto-closed ticket {ticket.id}")
            except Exception as e:
                logger.error(f"Error auto-closing ticket {ticket.id}: {e}")
        
        return {
            "success": True,
            "expired_count": len(expired_tickets),
            "closed_count": closed_count,
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error auto-closing expired tickets: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.cleanup_old_followups")
def cleanup_old_followups():
    """
    Clean up old follow-up logs (older than 90 days)
    """
    db = SessionLocal()
    try:
        logger.info("Cleaning up old follow-up logs")
        
        # Find follow-ups older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        old_followups = db.query(FollowUpLog).filter(
            FollowUpLog.created_at <= cutoff_date
        ).all()
        
        logger.info(f"Found {len(old_followups)} old follow-ups to clean up")
        
        # Delete old follow-ups
        for follow_up in old_followups:
            try:
                db.delete(follow_up)
            except Exception as e:
                logger.error(f"Error deleting follow-up {follow_up.id}: {e}")
        
        db.commit()
        
        return {
            "success": True,
            "cleaned_count": len(old_followups),
            "cleaned_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old follow-ups: {e}")
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.retry_failed_followups")
def retry_failed_followups():
    """
    Retry failed follow-ups with exponential backoff
    """
    db = SessionLocal()
    try:
        logger.info("Checking for failed follow-ups to retry")
        
        # Find failed follow-ups that can be retried
        now = datetime.utcnow()
        failed_followups = db.query(FollowUpLog).filter(
            FollowUpLog.status == "failed",
            FollowUpLog.retry_count < 3,  # Max 3 retries
            FollowUpLog.scheduled_time <= now
        ).all()
        
        logger.info(f"Found {len(failed_followups)} failed follow-ups to retry")
        
        retry_count = 0
        for follow_up in failed_followups:
            try:
                # Calculate retry delay (exponential backoff)
                retry_delay = 2 ** follow_up.retry_count  # 1, 2, 4 hours
                
                # Update retry count
                follow_up.retry_count += 1
                follow_up.status = "scheduled"
                follow_up.scheduled_time = now + timedelta(hours=retry_delay)
                follow_up.last_retry_at = now
                
                db.commit()
                
                # Schedule retry
                execute_follow_up.apply_async(
                    args=[follow_up.id],
                    countdown=retry_delay * 3600  # Convert to seconds
                )
                
                retry_count += 1
                logger.info(f"Scheduled retry {follow_up.retry_count} for follow-up {follow_up.id}")
                
            except Exception as e:
                logger.error(f"Error scheduling retry for follow-up {follow_up.id}: {e}")
        
        return {
            "success": True,
            "retry_count": retry_count,
            "checked_at": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrying failed follow-ups: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.send_follow_up_reminder")
def send_follow_up_reminder(ticket_id: int):
    """
    Send a reminder follow-up if no response received
    """
    db = SessionLocal()
    try:
        logger.info(f"Sending follow-up reminder for ticket {ticket_id}")
        
        # Get ticket details
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found")
            return {"success": False, "error": "Ticket not found"}
        
        # Check if ticket is still resolved but not confirmed
        if ticket.status != "resolved":
            logger.info(f"Ticket {ticket_id} is not in resolved status")
            return {"success": False, "error": "Ticket not in resolved status"}
        
        # Create reminder follow-up
        followup_service = FollowUpService(db)
        result = followup_service.schedule_follow_up(
            ticket_id=ticket_id,
            delay_hours=0  # Send immediately
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending follow-up reminder for ticket {ticket_id}: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.process_follow_up_response")
def process_follow_up_response(follow_up_id: int, response: str, rating: Optional[int] = None):
    """
    Process user response to follow-up
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing follow-up response for {follow_up_id}: {response}")
        
        followup_service = FollowUpService(db)
        result = followup_service.handle_follow_up_response(
            follow_up_id=follow_up_id,
            response=response,
            rating=rating
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing follow-up response: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.tasks.followup_tasks.generate_follow_up_report")
def generate_follow_up_report(brand_id: Optional[int] = None, days: int = 30):
    """
    Generate follow-up performance report
    """
    db = SessionLocal()
    try:
        logger.info(f"Generating follow-up report for brand {brand_id}, days: {days}")
        
        followup_service = FollowUpService(db)
        stats = followup_service.get_follow_up_stats(brand_id=brand_id, days=days)
        
        # Add report metadata
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "brand_id": brand_id,
            "period_days": days,
            "stats": stats
        }
        
        logger.info(f"Follow-up report generated: {stats}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating follow-up report: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close() 