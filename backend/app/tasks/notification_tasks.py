# backend/app/tasks/notification_tasks.py

import logging
from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.notification_service import NotificationService
from app.models import Notification, User, Brand, Ticket
from app.celery_app import celery_app
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, func, or_

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_pending_notifications")
def send_pending_notifications(self):
    """
    Send all pending notifications that are scheduled for immediate delivery
    """
    db = SessionLocal()
    try:
        logger.info("Starting pending notification processing")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "processing_notifications"}
        )
        
        notification_service = NotificationService(db)
        
        # Find pending notifications that should be sent now
        now = datetime.utcnow()
        pending_notifications = db.query(Notification).filter(
            and_(
                Notification.status == "pending",
                or_(
                    Notification.scheduled_at.is_(None),
                    Notification.scheduled_at <= now
                )
            )
        ).all()
        
        logger.info(f"Found {len(pending_notifications)} pending notifications")
        
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        for notification in pending_notifications:
            try:
                # Get user details
                user = db.query(User).filter(User.id == notification.user_id).first()
                if not user:
                    logger.warning(f"User not found for notification {notification.id}")
                    failed_count += 1
                    continue
                
                # Send notification through all channels
                result = notification_service._send_notification_immediately(notification, user)
                
                if result["success"]:
                    sent_count += 1
                    logger.info(f"Successfully sent notification {notification.id} to user {user.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send notification {notification.id}: {result}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending notification {notification.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Pending notification processing completed: {processed_count} processed, {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in pending notification processing: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_scheduled_notifications")
def send_scheduled_notifications(self):
    """
    Send notifications that are scheduled for specific times
    """
    db = SessionLocal()
    try:
        logger.info("Starting scheduled notification processing")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "processing_scheduled"}
        )
        
        notification_service = NotificationService(db)
        
        # Find scheduled notifications that are due
        now = datetime.utcnow()
        scheduled_notifications = db.query(Notification).filter(
            and_(
                Notification.status == "scheduled",
                Notification.scheduled_at <= now
            )
        ).all()
        
        logger.info(f"Found {len(scheduled_notifications)} scheduled notifications due")
        
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        for notification in scheduled_notifications:
            try:
                # Get user details
                user = db.query(User).filter(User.id == notification.user_id).first()
                if not user:
                    logger.warning(f"User not found for scheduled notification {notification.id}")
                    failed_count += 1
                    continue
                
                # Send notification
                result = notification_service._send_notification_immediately(notification, user)
                
                if result["success"]:
                    sent_count += 1
                    logger.info(f"Successfully sent scheduled notification {notification.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send scheduled notification {notification.id}: {result}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending scheduled notification {notification.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Scheduled notification processing completed: {processed_count} processed, {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in scheduled notification processing: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_daily_digest")
def send_daily_digest(self):
    """
    Send daily digest notifications to brands with activity summary
    """
    db = SessionLocal()
    try:
        logger.info("Starting daily digest generation")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_digest"}
        )
        
        notification_service = NotificationService(db)
        
        # Get all active brands
        active_brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        logger.info(f"Generating daily digest for {len(active_brands)} brands")
        
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        for brand in active_brands:
            try:
                # Get today's activity for the brand
                today = datetime.utcnow().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())
                
                # Get new tickets
                new_tickets = db.query(Ticket).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.created_at >= today_start,
                        Ticket.created_at <= today_end
                    )
                ).count()
                
                # Get resolved tickets
                resolved_tickets = db.query(Ticket).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.status == "resolved",
                        Ticket.updated_at >= today_start,
                        Ticket.updated_at <= today_end
                    )
                ).count()
                
                # Get pending tickets
                pending_tickets = db.query(Ticket).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.status.in_(["open", "in_progress", "pending"])
                    )
                ).count()
                
                # Only send digest if there's activity
                if new_tickets > 0 or resolved_tickets > 0:
                    # Send daily digest to all brand users
                    result = notification_service.send_brand_notification(
                        brand_id=brand.id,
                        notification_type="daily_digest",
                        data={
                            "brand_name": brand.name,
                            "new_tickets": new_tickets,
                            "resolved_tickets": resolved_tickets,
                            "pending_tickets": pending_tickets,
                            "date": today.isoformat()
                        }
                    )
                    
                    if result["success"]:
                        sent_count += 1
                        logger.info(f"Sent daily digest to brand {brand.id}")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed to send daily digest to brand {brand.id}: {result['error']}")
                else:
                    logger.info(f"No activity for brand {brand.id}, skipping daily digest")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error generating daily digest for brand {brand.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Daily digest generation completed: {processed_count} processed, {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in daily digest generation: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_weekly_reports")
def send_weekly_reports(self):
    """
    Send weekly performance reports to brands
    """
    db = SessionLocal()
    try:
        logger.info("Starting weekly report generation")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_reports"}
        )
        
        notification_service = NotificationService(db)
        
        # Get all active brands
        active_brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        logger.info(f"Generating weekly reports for {len(active_brands)} brands")
        
        processed_count = 0
        sent_count = 0
        failed_count = 0
        
        for brand in active_brands:
            try:
                # Get last week's activity
                week_ago = datetime.utcnow() - timedelta(days=7)
                
                # Get weekly statistics
                new_tickets = db.query(Ticket).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.created_at >= week_ago
                    )
                ).count()
                
                resolved_tickets = db.query(Ticket).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.status == "resolved",
                        Ticket.updated_at >= week_ago
                    )
                ).count()
                
                avg_resolution_time = db.query(
                    func.avg(func.extract('epoch', Ticket.updated_at - Ticket.created_at))
                ).filter(
                    and_(
                        Ticket.brand_id == brand.id,
                        Ticket.status == "resolved",
                        Ticket.updated_at >= week_ago
                    )
                ).scalar() or 0
                
                # Convert to hours
                avg_resolution_hours = avg_resolution_time / 3600 if avg_resolution_time > 0 else 0
                
                # Send weekly report
                result = notification_service.send_brand_notification(
                    brand_id=brand.id,
                    notification_type="weekly_report",
                    data={
                        "brand_name": brand.name,
                        "new_tickets": new_tickets,
                        "resolved_tickets": resolved_tickets,
                        "avg_resolution_hours": round(avg_resolution_hours, 2),
                        "period_start": week_ago.isoformat(),
                        "period_end": datetime.utcnow().isoformat()
                    }
                )
                
                if result["success"]:
                    sent_count += 1
                    logger.info(f"Sent weekly report to brand {brand.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send weekly report to brand {brand.id}: {result['error']}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error generating weekly report for brand {brand.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Weekly report generation completed: {processed_count} processed, {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in weekly report generation: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.retry_failed_notifications")
def retry_failed_notifications(self):
    """
    Retry failed notifications with exponential backoff
    """
    db = SessionLocal()
    try:
        logger.info("Starting failed notification retry")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "retrying_notifications"}
        )
        
        notification_service = NotificationService(db)
        
        # Find failed notifications that can be retried
        now = datetime.utcnow()
        failed_notifications = db.query(Notification).filter(
            and_(
                Notification.status == "failed",
                Notification.retry_count < 3,  # Max 3 retries
                Notification.created_at >= now - timedelta(days=7)  # Only retry recent failures
            )
        ).all()
        
        logger.info(f"Found {len(failed_notifications)} failed notifications to retry")
        
        processed_count = 0
        retried_count = 0
        failed_count = 0
        
        for notification in failed_notifications:
            try:
                # Get user details
                user = db.query(User).filter(User.id == notification.user_id).first()
                if not user:
                    logger.warning(f"User not found for failed notification {notification.id}")
                    failed_count += 1
                    continue
                
                # Update retry count
                notification.retry_count = (notification.retry_count or 0) + 1
                notification.status = "pending"
                notification.last_retry_at = now
                
                db.commit()
                
                # Retry sending
                result = notification_service._send_notification_immediately(notification, user)
                
                if result["success"]:
                    retried_count += 1
                    logger.info(f"Successfully retried notification {notification.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Retry failed for notification {notification.id}: {result}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error retrying notification {notification.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "retried_count": retried_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Failed notification retry completed: {processed_count} processed, {retried_count} retried, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "retried_count": retried_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in failed notification retry: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.cleanup_old_notifications")
def cleanup_old_notifications(self, days: int = 90):
    """
    Clean up old notification records to maintain database performance
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting cleanup of notifications older than {days} days")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "cleaning_notifications", "days": days}
        )
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find old notifications
        old_notifications = db.query(Notification).filter(
            and_(
                Notification.created_at < cutoff_date,
                Notification.status.in_(["delivered", "failed"])
            )
        ).all()
        
        logger.info(f"Found {len(old_notifications)} old notifications to cleanup")
        
        deleted_count = 0
        
        for notification in old_notifications:
            try:
                db.delete(notification)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting notification {notification.id}: {e}")
        
        db.commit()
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "deleted_count": deleted_count,
                "cutoff_date": cutoff_date.isoformat(),
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Notification cleanup completed: {deleted_count} notifications deleted")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in notification cleanup: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.notification_tasks.send_urgent_alerts")
def send_urgent_alerts(self):
    """
    Send urgent alerts for critical system events
    """
    db = SessionLocal()
    try:
        logger.info("Starting urgent alert processing")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "processing_alerts"}
        )
        
        notification_service = NotificationService(db)
        
        # Check for urgent situations
        urgent_alerts = []
        
        # Check for brands with very low balance
        low_balance_brands = db.query(Brand).filter(
            Brand.credit_balance < 50.0  # Very low balance threshold
        ).all()
        
        for brand in low_balance_brands:
            urgent_alerts.append({
                "type": "critical_low_balance",
                "brand_id": brand.id,
                "message": f"Brand {brand.name} has critically low balance: {brand.credit_balance} credits",
                "data": {
                    "brand_name": brand.name,
                    "current_balance": brand.credit_balance,
                    "threshold": 50.0
                }
            })
        
        # Check for tickets that have been open for too long
        long_open_tickets = db.query(Ticket).filter(
            and_(
                Ticket.status.in_(["open", "in_progress"]),
                Ticket.created_at <= datetime.utcnow() - timedelta(hours=72)  # 3 days
            )
        ).all()
        
        for ticket in long_open_tickets:
            urgent_alerts.append({
                "type": "long_open_ticket",
                "brand_id": ticket.brand_id,
                "message": f"Ticket #{ticket.id} has been open for over 72 hours",
                "data": {
                    "ticket_id": ticket.id,
                    "ticket_title": ticket.title,
                    "hours_open": int((datetime.utcnow() - ticket.created_at).total_seconds() / 3600)
                }
            })
        
        logger.info(f"Found {len(urgent_alerts)} urgent alerts")
        
        sent_count = 0
        failed_count = 0
        
        for alert in urgent_alerts:
            try:
                # Send urgent alert to brand
                result = notification_service.send_brand_notification(
                    brand_id=alert["brand_id"],
                    notification_type=alert["type"],
                    data=alert["data"],
                    channels=["email", "sms"],  # Use multiple channels for urgent alerts
                    priority="high"
                )
                
                if result["success"]:
                    sent_count += 1
                    logger.info(f"Sent urgent alert: {alert['type']} to brand {alert['brand_id']}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send urgent alert: {alert['type']} to brand {alert['brand_id']}: {result['error']}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending urgent alert: {alert['type']} to brand {alert['brand_id']}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "alert_count": len(urgent_alerts),
                "sent_count": sent_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Urgent alert processing completed: {len(urgent_alerts)} alerts, {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "alert_count": len(urgent_alerts),
            "sent_count": sent_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in urgent alert processing: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close() 