# backend/app/tasks/billing_tasks.py

import logging
from datetime import datetime, timedelta
from celery import current_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.billing import BillingService
from app.services.notification_service import NotificationService
from app.models import Ticket, Brand, Transaction
from app.celery_app import celery_app
from typing import Optional
from sqlalchemy import and_, func

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.tasks.billing_tasks.check_complaint_charges")
def check_complaint_charges(self):
    """
    Check for unresolved complaints that need to be charged after 24 hours
    """
    db = SessionLocal()
    try:
        logger.info("Starting complaint charge check")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "checking_complaints"}
        )
        
        billing_service = BillingService(db)
        notification_service = NotificationService(db)
        
        # Find tickets that are unresolved and older than 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        unresolved_tickets = db.query(Ticket).filter(
            and_(
                Ticket.status.in_(["open", "in_progress", "pending"]),
                Ticket.created_at <= cutoff_time
            )
        ).all()
        
        logger.info(f"Found {len(unresolved_tickets)} unresolved tickets older than 24 hours")
        
        processed_count = 0
        charged_count = 0
        failed_count = 0
        
        for ticket in unresolved_tickets:
            try:
                # Check if already charged
                existing_charge = db.query(Transaction).filter(
                    and_(
                        Transaction.ticket_id == ticket.id,
                        Transaction.type == "complaint_charge"
                    )
                ).first()
                
                if existing_charge:
                    logger.info(f"Ticket {ticket.id} already charged, skipping")
                    continue
                
                # Process the charge
                result = billing_service.process_complaint_charge(ticket.id, ticket.brand_id)
                
                if result["success"]:
                    charged_count += 1
                    logger.info(f"Successfully charged ticket {ticket.id}: {result['message']}")
                    
                    # Send notification to brand if charge was successful
                    if "transaction_id" in result:
                        notification_service.send_ticket_alert(
                            ticket_id=ticket.id,
                            alert_type="complaint_charged",
                            data={
                                "amount": 50.0,
                                "transaction_id": result["transaction_id"],
                                "remaining_balance": result.get("remaining_balance", 0)
                            }
                        )
                else:
                    failed_count += 1
                    logger.warning(f"Failed to charge ticket {ticket.id}: {result['error']}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing charge for ticket {ticket.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "charged_count": charged_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Complaint charge check completed: {processed_count} processed, {charged_count} charged, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "charged_count": charged_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in complaint charge check: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.billing_tasks.process_pending_charges")
def process_pending_charges(self):
    """
    Process pending charges for brands that now have sufficient balance
    """
    db = SessionLocal()
    try:
        logger.info("Starting pending charge processing")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "processing_pending"}
        )
        
        billing_service = BillingService(db)
        notification_service = NotificationService(db)
        
        # Find pending charges
        pending_charges = db.query(Transaction).filter(
            and_(
                Transaction.status == "pending",
                Transaction.type == "complaint_charge"
            )
        ).all()
        
        logger.info(f"Found {len(pending_charges)} pending charges")
        
        processed_count = 0
        successful_count = 0
        failed_count = 0
        
        for charge in pending_charges:
            try:
                # Get brand current balance
                brand = db.query(Brand).filter(Brand.id == charge.brand_id).first()
                if not brand:
                    logger.warning(f"Brand not found for charge {charge.id}")
                    failed_count += 1
                    continue
                
                # Check if brand now has sufficient balance
                if brand.credit_balance >= charge.amount:
                    # Process the charge
                    brand.credit_balance -= charge.amount
                    charge.status = "completed"
                    charge.processed_at = datetime.utcnow()
                    
                    db.commit()
                    
                    successful_count += 1
                    logger.info(f"Successfully processed pending charge {charge.id} for brand {brand.id}")
                    
                    # Send notification
                    notification_service.send_ticket_alert(
                        ticket_id=charge.ticket_id,
                        alert_type="pending_charge_processed",
                        data={
                            "amount": charge.amount,
                            "transaction_id": charge.id,
                            "remaining_balance": brand.credit_balance
                        }
                    )
                else:
                    logger.info(f"Insufficient balance for brand {brand.id}, charge {charge.id} remains pending")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing pending charge {charge.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Pending charge processing completed: {processed_count} processed, {successful_count} successful, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in pending charge processing: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.billing_tasks.check_low_balance_brands")
def check_low_balance_brands(self):
    """
    Check for brands with low balance and send notifications
    """
    db = SessionLocal()
    try:
        logger.info("Starting low balance check")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "checking_balances"}
        )
        
        notification_service = NotificationService(db)
        
        # Find brands with low balance
        low_balance_brands = db.query(Brand).filter(
            Brand.credit_balance < 100.0  # Low balance threshold
        ).all()
        
        logger.info(f"Found {len(low_balance_brands)} brands with low balance")
        
        notified_count = 0
        
        for brand in low_balance_brands:
            try:
                # Send low balance notification
                result = notification_service.send_low_balance_alert(brand.id)
                
                if result["success"]:
                    notified_count += 1
                    logger.info(f"Sent low balance notification to brand {brand.id}")
                else:
                    logger.warning(f"Failed to send low balance notification to brand {brand.id}: {result['error']}")
                
            except Exception as e:
                logger.error(f"Error sending low balance notification to brand {brand.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "low_balance_count": len(low_balance_brands),
                "notified_count": notified_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Low balance check completed: {len(low_balance_brands)} brands checked, {notified_count} notified")
        
        return {
            "success": True,
            "low_balance_count": len(low_balance_brands),
            "notified_count": notified_count
        }
        
    except Exception as e:
        logger.error(f"Error in low balance check: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.billing_tasks.process_subscription_renewals")
def process_subscription_renewals(self):
    """
    Process monthly subscription renewals and add credits
    """
    db = SessionLocal()
    try:
        logger.info("Starting subscription renewal processing")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "processing_renewals"}
        )
        
        billing_service = BillingService(db)
        notification_service = NotificationService(db)
        
        # Find active subscriptions that need renewal
        now = datetime.utcnow()
        subscriptions_to_renew = db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.current_period_end <= now
            )
        ).all()
        
        logger.info(f"Found {len(subscriptions_to_renew)} subscriptions to renew")
        
        processed_count = 0
        successful_count = 0
        failed_count = 0
        
        for subscription in subscriptions_to_renew:
            try:
                # Process subscription renewal
                result = billing_service.process_subscription_payment(subscription.stripe_subscription_id)
                
                if result["success"]:
                    successful_count += 1
                    logger.info(f"Successfully renewed subscription {subscription.id}")
                    
                    # Send notification to brand
                    notification_service.send_brand_notification(
                        brand_id=subscription.brand_id,
                        notification_type="subscription_renewed",
                        data={
                            "subscription_id": subscription.id,
                            "plan_type": subscription.plan_type,
                            "credits_added": subscription.credits_per_month,
                            "amount": subscription.monthly_price
                        }
                    )
                else:
                    failed_count += 1
                    logger.warning(f"Failed to renew subscription {subscription.id}: {result['error']}")
                
                processed_count += 1
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error processing subscription renewal {subscription.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "processed_count": processed_count,
                "successful_count": successful_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Subscription renewal processing completed: {processed_count} processed, {successful_count} successful, {failed_count} failed")
        
        return {
            "success": True,
            "processed_count": processed_count,
            "successful_count": successful_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in subscription renewal processing: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.billing_tasks.generate_monthly_billing_reports")
def generate_monthly_billing_reports(self):
    """
    Generate monthly billing reports for all brands
    """
    db = SessionLocal()
    try:
        logger.info("Starting monthly billing report generation")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "generating_reports"}
        )
        
        billing_service = BillingService(db)
        notification_service = NotificationService(db)
        
        # Get all active brands
        active_brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        logger.info(f"Generating reports for {len(active_brands)} brands")
        
        generated_count = 0
        failed_count = 0
        
        for brand in active_brands:
            try:
                # Generate billing analytics for the last 30 days
                analytics = billing_service.get_billing_analytics(brand.id, "30d")
                
                if analytics["success"]:
                    # Send monthly report notification
                    notification_service.send_brand_notification(
                        brand_id=brand.id,
                        notification_type="monthly_billing_report",
                        data={
                            "brand_name": brand.name,
                            "analytics": analytics["data"],
                            "report_period": "30d"
                        }
                    )
                    
                    generated_count += 1
                    logger.info(f"Generated monthly report for brand {brand.id}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to generate report for brand {brand.id}: {analytics['error']}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error generating report for brand {brand.id}: {e}")
        
        # Update task status
        current_task.update_state(
            state="SUCCESS",
            meta={
                "generated_count": generated_count,
                "failed_count": failed_count,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Monthly billing report generation completed: {generated_count} generated, {failed_count} failed")
        
        return {
            "success": True,
            "generated_count": generated_count,
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.error(f"Error in monthly billing report generation: {e}")
        
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

@celery_app.task(bind=True, name="app.tasks.billing_tasks.cleanup_old_transactions")
def cleanup_old_transactions(self, days: int = 365):
    """
    Clean up old transaction records to maintain database performance
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting cleanup of transactions older than {days} days")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "cleaning_transactions", "days": days}
        )
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Find old transactions
        old_transactions = db.query(Transaction).filter(
            Transaction.created_at < cutoff_date
        ).all()
        
        logger.info(f"Found {len(old_transactions)} old transactions to cleanup")
        
        deleted_count = 0
        
        for transaction in old_transactions:
            try:
                db.delete(transaction)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting transaction {transaction.id}: {e}")
        
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
        
        logger.info(f"Transaction cleanup completed: {deleted_count} transactions deleted")
        
        return {
            "success": True,
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in transaction cleanup: {e}")
        
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