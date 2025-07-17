# backend/app/celery_app.py

import os
import logging
from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings
from datetime import datetime, timedelta
<<<<<<< HEAD
from app.database.session import SessionLocal
from app.services.followup_service import FollowUpService
from app.models.followup_log import FollowUpLog
=======
from app.database import SessionLocal
from app.services.followup_service import FollowUpService
from app.models import FollowUpLog
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "complainthubbot",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=[
        "app.tasks.followup_tasks",
        "app.tasks.billing_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.email_outreach_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
    result_expires=3600,  # 1 hour
    task_always_eager=False,  # Set to True for testing without Redis
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Daily tasks (2 AM UTC)
    "daily-ticket-cleanup": {
        "task": "app.tasks.followup_tasks.cleanup_old_followups",
        "schedule": crontab(hour=2, minute=0),
    },
    "daily-billing-check": {
        "task": "app.tasks.billing_tasks.check_complaint_charges",
        "schedule": crontab(hour=2, minute=15),
    },
    "daily-notification-cleanup": {
        "task": "app.tasks.notification_tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=30),
    },
    "daily-outreach-cleanup": {
        "task": "app.tasks.email_outreach_tasks.cleanup_old_outreach_logs",
        "schedule": crontab(hour=2, minute=45),
    },
    
    # Daily billing tasks (3 AM UTC)
    "daily-pending-charges": {
        "task": "app.tasks.billing_tasks.process_pending_charges",
        "schedule": crontab(hour=3, minute=0),
    },
    "daily-low-balance-check": {
        "task": "app.tasks.billing_tasks.check_low_balance_brands",
        "schedule": crontab(hour=3, minute=15),
    },
    "daily-subscription-renewals": {
        "task": "app.tasks.billing_tasks.process_subscription_renewals",
        "schedule": crontab(hour=3, minute=30),
    },
    
    # Daily notification tasks (4 AM UTC)
    "daily-pending-notifications": {
        "task": "app.tasks.notification_tasks.send_pending_notifications",
        "schedule": crontab(hour=4, minute=0),
    },
    "daily-scheduled-notifications": {
        "task": "app.tasks.notification_tasks.send_scheduled_notifications",
        "schedule": crontab(hour=4, minute=15),
    },
    "daily-urgent-alerts": {
        "task": "app.tasks.notification_tasks.send_urgent_alerts",
        "schedule": crontab(hour=4, minute=30),
    },
    
    # Daily digest and reports (5 AM UTC)
    "daily-digest": {
        "task": "app.tasks.notification_tasks.send_daily_digest",
        "schedule": crontab(hour=5, minute=0),
    },
    "daily-outreach-reports": {
        "task": "app.tasks.email_outreach_tasks.generate_outreach_reports",
        "schedule": crontab(hour=5, minute=15),
    },
    
    # Hourly tasks
    "hourly-followup-check": {
        "task": "app.tasks.followup_tasks.check_pending_followups",
        "schedule": crontab(minute=0),  # Every hour
    },
    "hourly-failed-notifications-retry": {
        "task": "app.tasks.notification_tasks.retry_failed_notifications",
        "schedule": crontab(minute=15),  # Every hour at 15 minutes
    },
    "hourly-failed-outreach-retry": {
        "task": "app.tasks.email_outreach_tasks.retry_failed_outreach",
        "schedule": crontab(minute=30),  # Every hour at 30 minutes
    },
    
    # Every 15 minutes
    "frequent-auto-close": {
        "task": "app.tasks.followup_tasks.auto_close_expired_tickets",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    
    # Weekly tasks (Sunday 6 AM UTC)
    "weekly-reports": {
        "task": "app.tasks.notification_tasks.send_weekly_reports",
        "schedule": crontab(day_of_week=0, hour=6, minute=0),  # Sunday 6 AM
    },
    "weekly-billing-reports": {
        "task": "app.tasks.billing_tasks.generate_monthly_billing_reports",
        "schedule": crontab(day_of_week=0, hour=6, minute=15),  # Sunday 6:15 AM
    },
    "weekly-transaction-cleanup": {
        "task": "app.tasks.billing_tasks.cleanup_old_transactions",
        "schedule": crontab(day_of_week=0, hour=6, minute=30),  # Sunday 6:30 AM
    },
    
    # Monthly tasks (1st of month 7 AM UTC)
    "monthly-billing-reports": {
        "task": "app.tasks.billing_tasks.generate_monthly_billing_reports",
<<<<<<< HEAD
        "schedule": crontab(day=1, hour=7, minute=0),  # 1st of month 7 AM
=======
        "schedule": crontab(day_of_month=1, hour=7, minute=0),  # 1st of month 7 AM
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
    },
}

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    logger.info(f"Request: {self.request!r}")
    return "Celery is working!"

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def execute_follow_up_with_retry(self, follow_up_id: int):
    """
    Execute follow-up with comprehensive retry logic and fallback handling
    """
    try:
        db = SessionLocal()
        follow_up_service = FollowUpService(db)
        
        # Get follow-up details
        follow_up = db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
        if not follow_up:
            logger.error(f"Follow-up {follow_up_id} not found")
            return {"success": False, "error": "Follow-up not found"}
        
        # Check if already completed
        if follow_up.status in ["completed", "failed"]:
            logger.info(f"Follow-up {follow_up_id} already {follow_up.status}")
            return {"success": True, "status": follow_up.status}
        
        # Execute follow-up with fallback handling
        result = follow_up_service.execute_follow_up(follow_up_id)
        
        if result["success"]:
            logger.info(f"Follow-up {follow_up_id} executed successfully")
            return result
        else:
            # Handle delivery failure with intelligent retry
            error = result.get("error", "Unknown error")
            attempt_count = getattr(self.request, 'retries', 0)
            
            if attempt_count < 3:
                # Calculate exponential backoff delay
                delay = 60 * (2 ** attempt_count)  # 1min, 2min, 4min
                
                logger.warning(f"Follow-up {follow_up_id} failed (attempt {attempt_count + 1}/3): {error}")
                logger.info(f"Retrying follow-up {follow_up_id} in {delay} seconds")
                
                # Retry with exponential backoff
                raise self.retry(countdown=delay, exc=Exception(error))
            else:
                # Max retries exceeded, handle failure
                logger.error(f"Follow-up {follow_up_id} failed after {attempt_count} retries: {error}")
                
                # Update follow-up status
                follow_up.status = "failed"
                follow_up.error_message = f"Max retries exceeded: {error}"
                follow_up.completed_at = datetime.utcnow()
                db.commit()
                
                # Notify brand about failed follow-up
                follow_up_service._notify_brand_of_failed_followup(follow_up, error)
                
                return {"success": False, "error": f"Max retries exceeded: {error}"}
                
    except Exception as e:
        logger.error(f"Error executing follow-up {follow_up_id}: {e}")
        
        # Handle specific error types
        if "rate limit" in str(e).lower():
            # Rate limit error - retry with longer delay
            delay = 300  # 5 minutes
            logger.warning(f"Rate limit hit for follow-up {follow_up_id}, retrying in {delay} seconds")
            raise self.retry(countdown=delay, exc=e)
        
        elif "authentication" in str(e).lower():
            # Authentication error - don't retry
            logger.error(f"Authentication error for follow-up {follow_up_id}: {e}")
            return {"success": False, "error": f"Authentication error: {e}"}
        
        elif "network" in str(e).lower() or "timeout" in str(e).lower():
            # Network error - retry with exponential backoff
            attempt_count = getattr(self.request, 'retries', 0)
            if attempt_count < 3:
                delay = 30 * (2 ** attempt_count)  # 30s, 1min, 2min
                logger.warning(f"Network error for follow-up {follow_up_id}, retrying in {delay} seconds")
                raise self.retry(countdown=delay, exc=e)
            else:
                logger.error(f"Network error for follow-up {follow_up_id} after {attempt_count} retries")
                return {"success": False, "error": f"Network error after {attempt_count} retries: {e}"}
        
        else:
            # Generic error - retry with exponential backoff
            attempt_count = getattr(self.request, 'retries', 0)
            if attempt_count < 3:
                delay = 60 * (2 ** attempt_count)
                logger.warning(f"Generic error for follow-up {follow_up_id}, retrying in {delay} seconds")
                raise self.retry(countdown=delay, exc=e)
            else:
                logger.error(f"Generic error for follow-up {follow_up_id} after {attempt_count} retries")
                return {"success": False, "error": f"Generic error after {attempt_count} retries: {e}"}
    
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=2, default_retry_delay=120)
def retry_failed_follow_ups(self):
    """
    Retry failed follow-ups with different channels
    """
    try:
        db = SessionLocal()
        follow_up_service = FollowUpService(db)
        
        # Get failed follow-ups from the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        failed_follow_ups = db.query(FollowUpLog).filter(
            FollowUpLog.status == "failed",
            FollowUpLog.created_at >= yesterday
        ).all()
        
        retry_count = 0
        success_count = 0
        
        for follow_up in failed_follow_ups:
            try:
                # Try with a different channel
                result = follow_up_service._execute_channel_follow_up_with_fallback(follow_up, "", None)
                
                if result["success"]:
                    follow_up.status = "completed"
                    follow_up.completed_at = datetime.utcnow()
                    follow_up.retry_count = (follow_up.retry_count or 0) + 1
                    success_count += 1
                    logger.info(f"Retry successful for follow-up {follow_up.id}")
                else:
                    logger.warning(f"Retry failed for follow-up {follow_up.id}: {result.get('error')}")
                
                retry_count += 1
                
            except Exception as e:
                logger.error(f"Error retrying follow-up {follow_up.id}: {e}")
        
        db.commit()
        
        logger.info(f"Retry process completed: {retry_count} attempted, {success_count} successful")
        return {"retry_count": retry_count, "success_count": success_count}
        
    except Exception as e:
        logger.error(f"Error in retry_failed_follow_ups task: {e}")
        raise self.retry(countdown=300, exc=e)  # Retry in 5 minutes
    
    finally:
        db.close()

@celery_app.task
def cleanup_old_follow_up_logs():
    """
    Clean up old follow-up logs to prevent database bloat
    """
    try:
        db = SessionLocal()
        
        # Delete completed/failed follow-ups older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        deleted_count = db.query(FollowUpLog).filter(
            FollowUpLog.status.in_(["completed", "failed"]),
            FollowUpLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleaned up {deleted_count} old follow-up logs")
        return {"deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Error cleaning up old follow-up logs: {e}")
        return {"error": str(e)}
    
    finally:
        db.close()

@celery_app.task
def monitor_follow_up_delivery_health():
    """
    Monitor follow-up delivery health and alert on issues
    """
    try:
        db = SessionLocal()
        
        # Check delivery success rate for the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        total_follow_ups = db.query(FollowUpLog).filter(
            FollowUpLog.created_at >= yesterday
        ).count()
        
        successful_follow_ups = db.query(FollowUpLog).filter(
            FollowUpLog.status == "completed",
            FollowUpLog.created_at >= yesterday
        ).count()
        
        failed_follow_ups = db.query(FollowUpLog).filter(
            FollowUpLog.status == "failed",
            FollowUpLog.created_at >= yesterday
        ).count()
        
        if total_follow_ups > 0:
            success_rate = (successful_follow_ups / total_follow_ups) * 100
            
            # Alert if success rate is below 80%
            if success_rate < 80:
                logger.warning(f"Low follow-up delivery success rate: {success_rate:.1f}%")
                
                # Send alert to admin
                alert_message = f"""
                Follow-up Delivery Alert
                
                Success Rate: {success_rate:.1f}%
                Total Follow-ups: {total_follow_ups}
                Successful: {successful_follow_ups}
                Failed: {failed_follow_ups}
                
                Please investigate the delivery system.
                """
                
                # Send alert (implement based on your notification system)
                # send_admin_alert(alert_message)
        
        return {
            "total_follow_ups": total_follow_ups,
            "successful_follow_ups": successful_follow_ups,
            "failed_follow_ups": failed_follow_ups,
            "success_rate": success_rate if total_follow_ups > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error monitoring follow-up delivery health: {e}")
        return {"error": str(e)}
    
    finally:
        db.close()

if __name__ == "__main__":
    celery_app.start() 