# backend/app/tasks/email_outreach_tasks.py

import logging
from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.email_outreach_service import EmailOutreachService
from app.models import Brand, EmailOutreachLog
from app.celery_app import celery_app
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, func
import time

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.discover_brand_contacts")
def discover_brand_contacts(self, brand_id: int, website_url: str = None):
    """
    Discover support contacts for a brand through web scraping
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting contact discovery for brand {brand_id}")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "discovering_contacts", "brand_id": brand_id}
        )
        
        # Get brand details
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            return {"success": False, "error": "Brand not found"}
        
        outreach_service = EmailOutreachService(db)
        
        # Discover contacts
        result = outreach_service.discover_brand_contacts(brand.name, website_url)
        
        if result["success"]:
            # Update brand with discovered contacts
            contacts = result["contacts"]
            brand.support_emails = contacts.get("support_emails", [])
            brand.support_phones = contacts.get("support_phones", [])
            brand.contact_forms = contacts.get("contact_forms", [])
            brand.social_media = contacts.get("social_media", [])
            brand.contact_discovery_date = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Contact discovery completed for brand {brand_id}: {len(contacts.get('support_emails', []))} emails found")
            
            # Update task status
            current_task.update_state(
                state="SUCCESS",
                meta={
                    "brand_id": brand_id,
                    "emails_found": len(contacts.get("support_emails", [])),
                    "phones_found": len(contacts.get("support_phones", [])),
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "success": True,
                "brand_id": brand_id,
                "contacts": contacts,
                "emails_found": len(contacts.get("support_emails", [])),
                "phones_found": len(contacts.get("support_phones", []))
            }
        else:
            logger.error(f"Contact discovery failed for brand {brand_id}: {result['error']}")
            
            # Update task status
            current_task.update_state(
                state="FAILURE",
                meta={
                    "brand_id": brand_id,
                    "error": result["error"],
                    "failed_at": datetime.utcnow().isoformat()
                }
            )
            
            return result
        
    except Exception as e:
        logger.error(f"Error in contact discovery for brand {brand_id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "brand_id": brand_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.send_outreach_campaign")
def send_outreach_campaign(
    self, 
    brand_id: int, 
    email_type: str = "partnership",
    custom_message: str = None,
    max_emails: int = 10
):
    """
    Send outreach campaign to brand support contacts
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting outreach campaign for brand {brand_id}")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "sending_campaign", "brand_id": brand_id}
        )
        
        # Get brand details
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            return {"success": False, "error": "Brand not found"}
        
        outreach_service = EmailOutreachService(db)
        
        # Get support emails
        support_emails = brand.support_emails or []
        if not support_emails:
            return {"success": False, "error": "No support emails found for brand"}
        
        # Limit number of emails
        emails_to_contact = support_emails[:max_emails]
        
        logger.info(f"Sending outreach to {len(emails_to_contact)} contacts for brand {brand_id}")
        
        sent_count = 0
        failed_count = 0
        results = []
        
        for email in emails_to_contact:
            try:
                # Send outreach email
                result = outreach_service.send_outreach_email(
                    brand_id=brand_id,
                    contact_email=email,
                    email_type=email_type,
                    custom_message=custom_message
                )
                
                results.append({
                    "email": email,
                    "success": result["success"],
                    "message": result.get("message", result.get("error", "Unknown error"))
                })
                
                if result["success"]:
                    sent_count += 1
                    logger.info(f"Successfully sent outreach to {email}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to send outreach to {email}: {result.get('error')}")
                
                # Rate limiting delay
                time.sleep(outreach_service.config["rate_limit_delay"])
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error sending outreach to {email}: {e}")
                results.append({
                    "email": email,
                    "success": False,
                    "message": str(e)
                })
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "brand_id": brand_id,
                "sent_count": sent_count,
                "failed_count": failed_count,
                "total_contacts": len(emails_to_contact),
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Outreach campaign completed for brand {brand_id}: {sent_count} sent, {failed_count} failed")
        
        return {
            "success": True,
            "brand_id": brand_id,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_contacts": len(emails_to_contact),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in outreach campaign for brand {brand_id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={
                "brand_id": brand_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
        )
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.send_bulk_outreach")
def send_bulk_outreach(
    self, 
    brand_ids: List[int], 
    email_type: str = "partnership",
    custom_message: str = None,
    max_emails_per_brand: int = 5
):
    """
    Send bulk outreach to multiple brands
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting bulk outreach to {len(brand_ids)} brands")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "sending_bulk_outreach", "total_brands": len(brand_ids)}
        )
        
        outreach_service = EmailOutreachService(db)
        
        total_sent = 0
        total_failed = 0
        brand_results = []
        
        for i, brand_id in enumerate(brand_ids):
            try:
                # Update progress
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "status": "sending_bulk_outreach",
                        "current_brand": i + 1,
                        "total_brands": len(brand_ids),
                        "brand_id": brand_id
                    }
                )
                
                # Get brand details
                brand = db.query(Brand).filter(Brand.id == brand_id).first()
                if not brand:
                    logger.warning(f"Brand {brand_id} not found, skipping")
                    brand_results.append({
                        "brand_id": brand_id,
                        "success": False,
                        "error": "Brand not found"
                    })
                    continue
                
                # Get support emails
                support_emails = brand.support_emails or []
                if not support_emails:
                    logger.warning(f"No support emails found for brand {brand_id}, skipping")
                    brand_results.append({
                        "brand_id": brand_id,
                        "success": False,
                        "error": "No support emails found"
                    })
                    continue
                
                # Limit emails per brand
                emails_to_contact = support_emails[:max_emails_per_brand]
                
                brand_sent = 0
                brand_failed = 0
                
                for email in emails_to_contact:
                    try:
                        # Send outreach email
                        result = outreach_service.send_outreach_email(
                            brand_id=brand_id,
                            contact_email=email,
                            email_type=email_type,
                            custom_message=custom_message
                        )
                        
                        if result["success"]:
                            brand_sent += 1
                            total_sent += 1
                        else:
                            brand_failed += 1
                            total_failed += 1
                        
                        # Rate limiting delay
                        time.sleep(outreach_service.config["rate_limit_delay"])
                        
                    except Exception as e:
                        brand_failed += 1
                        total_failed += 1
                        logger.error(f"Error sending outreach to {email} for brand {brand_id}: {e}")
                
                brand_results.append({
                    "brand_id": brand_id,
                    "brand_name": brand.name,
                    "success": brand_sent > 0,
                    "sent_count": brand_sent,
                    "failed_count": brand_failed,
                    "total_contacts": len(emails_to_contact)
                })
                
                logger.info(f"Completed outreach for brand {brand_id}: {brand_sent} sent, {brand_failed} failed")
                
            except Exception as e:
                logger.error(f"Error processing brand {brand_id}: {e}")
                brand_results.append({
                    "brand_id": brand_id,
                    "success": False,
                    "error": str(e)
                })
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "total_brands": len(brand_ids),
                "total_sent": total_sent,
                "total_failed": total_failed,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Bulk outreach completed: {total_sent} total sent, {total_failed} total failed")
        
        return {
            "success": True,
            "total_brands": len(brand_ids),
            "total_sent": total_sent,
            "total_failed": total_failed,
            "brand_results": brand_results
        }
        
    except Exception as e:
        logger.error(f"Error in bulk outreach: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.retry_failed_outreach")
def retry_failed_outreach(self, max_retries: int = 3):
    """
    Retry failed outreach emails
    """
    db = SessionLocal()
    try:
        logger.info("Starting failed outreach retry")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "retrying_failed_outreach"}
        )
        
        outreach_service = EmailOutreachService(db)
        
        # Find failed outreach logs that can be retried
        failed_logs = db.query(EmailOutreachLog).filter(
            and_(
                EmailOutreachLog.status == "failed",
                EmailOutreachLog.retry_count < max_retries
            )
        ).all()
        
        logger.info(f"Found {len(failed_logs)} failed outreach emails to retry")
        
        retried_count = 0
        successful_count = 0
        failed_count = 0
        
        for log in failed_logs:
            try:
                # Update retry count
                log.retry_count = (log.retry_count or 0) + 1
                log.last_retry_at = datetime.utcnow()
                
                # Retry sending
                result = outreach_service.send_outreach_email(
                    brand_id=log.brand_id,
                    contact_email=log.contact_email,
                    email_type=log.email_type,
                    custom_message=log.message
                )
                
                if result["success"]:
                    log.status = "sent"
                    log.sent_at = datetime.utcnow()
                    successful_count += 1
                    logger.info(f"Successfully retried outreach {log.id}")
                else:
                    log.status = "failed"
                    failed_count += 1
                    logger.warning(f"Retry failed for outreach {log.id}: {result.get('error')}")
                
                retried_count += 1
                
                # Rate limiting delay
                time.sleep(outreach_service.config["rate_limit_delay"])
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error retrying outreach {log.id}: {e}")
        
        db.commit()
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "retried_count": retried_count,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Failed outreach retry completed: {retried_count} retried, {successful_count} successful, {failed_count} failed")
        
        return {
            "success": True,
            "retried_count": retried_count,
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in failed outreach retry: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.generate_outreach_reports")
def generate_outreach_reports(self, days: int = 30):
    """
    Generate outreach reports for all brands
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting outreach report generation for last {days} days")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_reports", "days": days}
        )
        
        outreach_service = EmailOutreachService(db)
        
        # Get all active brands
        active_brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        logger.info(f"Generating reports for {len(active_brands)} brands")
        
        processed_count = 0
        generated_count = 0
        failed_count = 0
        
        for brand in active_brands:
            try:
                # Generate outreach analytics
                analytics = outreach_service.get_outreach_analytics(brand.id, days)
                
                if analytics["success"]:
                    generated_count += 1
                    logger.info(f"Generated outreach report for brand {brand.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to generate report for brand {brand.id}: {analytics['error']}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error generating outreach report for brand {brand.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "generated_count": generated_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Outreach report generation completed: {processed_count} processed, {generated_count} generated, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "generated_count": generated_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in outreach report generation: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.email_outreach_tasks.cleanup_old_outreach_logs")
def cleanup_old_outreach_logs(self, days: int = 365):
    """
    Clean up old outreach logs
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting cleanup of outreach logs older than {days} days")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "cleaning_logs", "days": days}
        )
        
        outreach_service = EmailOutreachService(db)
        
        # Clean up old logs
        result = outreach_service.cleanup_old_outreach_logs(days)
        
        if result["success"]:
            logger.info(f"Cleaned up {result['deleted_count']} old outreach logs")
            
            # Update task status
            current_task.update_state(
                state="SUCCESS",
                meta={
                    "deleted_count": result["deleted_count"],
                    "cutoff_date": result["cutoff_date"],
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
            
            return result
        else:
            logger.error(f"Failed to cleanup outreach logs: {result['error']}")
            
            # Update task status
            current_task.update_state(
                state="FAILURE",
                meta={
                    "error": result["error"],
                    "failed_at": datetime.utcnow().isoformat()
                }
            )
            
            return result
        
    except Exception as e:
        logger.error(f"Error in outreach log cleanup: {e}")
        
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