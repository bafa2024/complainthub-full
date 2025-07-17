# backend/app/services/billing.py

import logging
import stripe
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, asc
from app import crud, schemas
from app.models import Brand, Ticket, Transaction, Subscription, PaymentMethod
from app.config.settings import settings
import json
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.complaint_charge = 50  # Rs. 50 per unresolved complaint
        self.free_resolution_window = 24  # 24 hours free resolution window
    
    def process_complaint_charge(self, ticket_id: int, brand_id: int) -> Dict[str, Any]:
        """
        Process charge for unresolved complaint after 24 hours
        """
        try:
            # Get ticket and brand
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            
            if not ticket or not brand:
                return {"success": False, "error": "Ticket or brand not found"}
            
            # Check if ticket is still unresolved after 24 hours
            if ticket.status == "resolved":
                return {"success": True, "message": "Ticket already resolved, no charge"}
            
            # Calculate time since ticket creation
            time_since_creation = datetime.utcnow() - ticket.created_at
            hours_since_creation = time_since_creation.total_seconds() / 3600
            
            if hours_since_creation < self.free_resolution_window:
                return {"success": True, "message": "Within free resolution window"}
            
            # Check if already charged
            existing_charge = self.db.query(Transaction).filter(
                and_(
                    Transaction.ticket_id == ticket_id,
                    Transaction.type == "complaint_charge"
                )
            ).first()
            
            if existing_charge:
                return {"success": True, "message": "Already charged for this ticket"}
            
            # Check brand credit balance
            if brand.credit_balance < self.complaint_charge:
                # Create pending charge
                transaction = Transaction(
                    brand_id=brand_id,
                    ticket_id=ticket_id,
                    type="complaint_charge",
                    amount=self.complaint_charge,
                    status="pending",
                    description=f"Charge for unresolved complaint #{ticket_id}",
                    meta_data={
                        "ticket_title": ticket.title,
                        "hours_since_creation": hours_since_creation,
                        "free_window_exceeded": True
                    }
                )
                self.db.add(transaction)
                self.db.commit()
                
                # Send low balance notification
                self._send_low_balance_notification(brand)
                
                return {
                    "success": True,
                    "message": "Charge pending due to insufficient balance",
                    "transaction_id": transaction.id
                }
            
            # Process the charge
            brand.credit_balance -= self.complaint_charge
            
            # Create transaction record
            transaction = Transaction(
                brand_id=brand_id,
                ticket_id=ticket_id,
                type="complaint_charge",
                amount=self.complaint_charge,
                status="completed",
                description=f"Charge for unresolved complaint #{ticket_id}",
                meta_data={
                    "ticket_title": ticket.title,
                    "hours_since_creation": hours_since_creation,
                    "free_window_exceeded": True
                }
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            logger.info(f"Processed complaint charge: {self.complaint_charge} credits for ticket {ticket_id}")
            
            return {
                "success": True,
                "message": "Charge processed successfully",
                "transaction_id": transaction.id,
                "remaining_balance": brand.credit_balance
            }
            
        except Exception as e:
            logger.error(f"Error processing complaint charge: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def process_credit_topup(self, brand_id: int, amount: float, payment_method: str = "stripe") -> Dict[str, Any]:
        """
        Process credit top-up payment
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Create payment intent with Stripe
            if payment_method == "stripe":
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency="inr",
                    metadata={
                        "brand_id": brand_id,
                        "brand_name": brand.name,
                        "type": "credit_topup"
                    }
                )
                
                # Create pending transaction
                transaction = Transaction(
                    brand_id=brand_id,
                    type="credit_topup",
                    amount=amount,
                    status="pending",
                    payment_intent_id=payment_intent.id,
                    description=f"Credit top-up of {amount} credits",
                    meta_data={
                        "payment_method": "stripe",
                        "payment_intent_id": payment_intent.id
                    }
                )
                
                self.db.add(transaction)
                self.db.commit()
                
                return {
                    "success": True,
                    "payment_intent_id": payment_intent.id,
                    "client_secret": payment_intent.client_secret,
                    "transaction_id": transaction.id
                }
            
            return {"success": False, "error": "Unsupported payment method"}
            
        except Exception as e:
            logger.error(f"Error processing credit topup: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm payment and add credits to brand balance
        """
        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status != "succeeded":
                return {"success": False, "error": "Payment not successful"}
            
            # Find the pending transaction
            transaction = self.db.query(Transaction).filter(
                Transaction.payment_intent_id == payment_intent_id
            ).first()
            
            if not transaction:
                return {"success": False, "error": "Transaction not found"}
            
            # Update transaction status
            transaction.status = "completed"
            transaction.processed_at = datetime.utcnow()
            
            # Add credits to brand balance
            brand = self.db.query(Brand).filter(Brand.id == transaction.brand_id).first()
            if brand:
                brand.credit_balance += transaction.amount
                brand.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Payment confirmed: {transaction.amount} credits added to brand {brand.id}")
            
            return {
                "success": True,
                "message": "Payment confirmed and credits added",
                "transaction_id": transaction.id,
                "credits_added": transaction.amount,
                "new_balance": brand.credit_balance if brand else 0
            }
            
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def create_subscription(self, brand_id: int, plan_type: str, payment_method_id: str) -> Dict[str, Any]:
        """
        Create subscription for a brand
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Define subscription plans
            plans = {
                "basic": {
                    "price_id": settings.STRIPE_BASIC_PLAN_ID,
                    "credits_per_month": 1000,
                    "price": 1000  # Rs. 1000 per month
                },
                "professional": {
                    "price_id": settings.STRIPE_PRO_PLAN_ID,
                    "credits_per_month": 2500,
                    "price": 2000  # Rs. 2000 per month
                },
                "enterprise": {
                    "price_id": settings.STRIPE_ENTERPRISE_PLAN_ID,
                    "credits_per_month": 5000,
                    "price": 3500  # Rs. 3500 per month
                }
            }
            
            if plan_type not in plans:
                return {"success": False, "error": "Invalid plan type"}
            
            plan = plans[plan_type]
            
            # Create Stripe subscription
            subscription = stripe.Subscription.create(
                customer=brand.stripe_customer_id,
                items=[{"price": plan["price_id"]}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "brand_id": brand_id,
                    "brand_name": brand.name,
                    "plan_type": plan_type
                }
            )
            
            # Create subscription record
            db_subscription = Subscription(
                brand_id=brand_id,
                stripe_subscription_id=subscription.id,
                plan_type=plan_type,
                status="active",
                credits_per_month=plan["credits_per_month"],
                monthly_price=plan["price"],
                current_period_start=datetime.fromtimestamp(subscription.current_period_start),
                current_period_end=datetime.fromtimestamp(subscription.current_period_end),
                meta_data={
                    "stripe_subscription_id": subscription.id,
                    "plan_type": plan_type
                }
            )
            
            self.db.add(db_subscription)
            self.db.commit()
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "db_subscription_id": db_subscription.id
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def process_subscription_payment(self, subscription_id: str) -> Dict[str, Any]:
        """
        Process monthly subscription payment and add credits
        """
        try:
            # Get subscription from database
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if not subscription:
                return {"success": False, "error": "Subscription not found"}
            
            # Add monthly credits
            brand = self.db.query(Brand).filter(Brand.id == subscription.brand_id).first()
            if brand:
                brand.credit_balance += subscription.credits_per_month
                brand.updated_at = datetime.utcnow()
            
            # Create transaction record
            transaction = Transaction(
                brand_id=subscription.brand_id,
                type="subscription_payment",
                amount=subscription.monthly_price,
                status="completed",
                description=f"Monthly subscription payment - {subscription.plan_type} plan",
                meta_data={
                    "subscription_id": subscription.id,
                    "plan_type": subscription.plan_type,
                    "credits_added": subscription.credits_per_month
                }
            )
            
            self.db.add(transaction)
            self.db.commit()
            
            logger.info(f"Subscription payment processed: {subscription.credits_per_month} credits added")
            
            return {
                "success": True,
                "credits_added": subscription.credits_per_month,
                "new_balance": brand.credit_balance if brand else 0
            }
            
        except Exception as e:
            logger.error(f"Error processing subscription payment: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_brand_billing_summary(self, brand_id: int) -> Dict[str, Any]:
        """
        Get comprehensive billing summary for a brand
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Get recent transactions
            transactions = self.db.query(Transaction).filter(
                Transaction.brand_id == brand_id
            ).order_by(desc(Transaction.created_at)).limit(10).all()
            
            # Get active subscription
            subscription = self.db.query(Subscription).filter(
                and_(
                    Subscription.brand_id == brand_id,
                    Subscription.status == "active"
                )
            ).first()
            
            # Calculate monthly spending
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.brand_id == brand_id,
                    Transaction.created_at >= month_start,
                    Transaction.status == "completed"
                )
            ).all()
            
            monthly_spending = sum(t.amount for t in monthly_transactions)
            
            # Get pending charges
            pending_charges = self.db.query(Transaction).filter(
                and_(
                    Transaction.brand_id == brand_id,
                    Transaction.status == "pending"
                )
            ).all()
            
            return {
                "success": True,
                "data": {
                    "current_balance": brand.credit_balance,
                    "subscription": {
                        "active": subscription is not None,
                        "plan_type": subscription.plan_type if subscription else None,
                        "credits_per_month": subscription.credits_per_month if subscription else 0,
                        "monthly_price": subscription.monthly_price if subscription else 0,
                        "next_billing_date": subscription.current_period_end if subscription else None
                    },
                    "monthly_spending": monthly_spending,
                    "pending_charges": len(pending_charges),
                    "recent_transactions": [
                        {
                            "id": t.id,
                            "type": t.type,
                            "amount": t.amount,
                            "status": t.status,
                            "description": t.description,
                            "created_at": t.created_at.isoformat()
                        }
                        for t in transactions
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting billing summary: {e}")
            return {"success": False, "error": str(e)}
    
    def get_transaction_history(self, brand_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get detailed transaction history for a brand
        """
        try:
            transactions = self.db.query(Transaction).filter(
                Transaction.brand_id == brand_id
            ).order_by(desc(Transaction.created_at)).offset(offset).limit(limit).all()
            
            total_count = self.db.query(Transaction).filter(
                Transaction.brand_id == brand_id
            ).count()
            
            return {
                "success": True,
                "data": {
                    "transactions": [
                        {
                            "id": t.id,
                            "type": t.type,
                            "amount": t.amount,
                            "status": t.status,
                            "description": t.description,
                            "created_at": t.created_at.isoformat(),
                            "processed_at": t.processed_at.isoformat() if t.processed_at else None,
                            "meta_data": t.meta_data
                        }
                        for t in transactions
                    ],
                    "total_count": total_count,
                    "has_more": offset + limit < total_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return {"success": False, "error": str(e)}
    
    def create_refund(self, transaction_id: int, reason: str) -> Dict[str, Any]:
        """
        Create refund for a transaction
        """
        try:
            transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return {"success": False, "error": "Transaction not found"}
            
            if transaction.status != "completed":
                return {"success": False, "error": "Transaction not completed"}
            
            # Process refund through Stripe if applicable
            if transaction.payment_intent_id:
                refund = stripe.Refund.create(
                    payment_intent=transaction.payment_intent_id,
                    reason="requested_by_customer"
                )
                
                # Create refund transaction
                refund_transaction = Transaction(
                    brand_id=transaction.brand_id,
                    type="refund",
                    amount=-transaction.amount,  # Negative amount for refund
                    status="completed",
                    description=f"Refund for transaction #{transaction_id}: {reason}",
                    meta_data={
                        "original_transaction_id": transaction_id,
                        "stripe_refund_id": refund.id,
                        "reason": reason
                    }
                )
                
                # Update brand balance
                brand = self.db.query(Brand).filter(Brand.id == transaction.brand_id).first()
                if brand:
                    brand.credit_balance += abs(transaction.amount)
                
                self.db.add(refund_transaction)
                self.db.commit()
                
                return {
                    "success": True,
                    "refund_id": refund.id,
                    "amount_refunded": transaction.amount
                }
            
            return {"success": False, "error": "Cannot refund this transaction type"}
            
        except Exception as e:
            logger.error(f"Error creating refund: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def generate_invoice(self, transaction_id: int) -> Dict[str, Any]:
        """
        Generate invoice for a transaction
        """
        try:
            transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
            if not transaction:
                return {"success": False, "error": "Transaction not found"}
            
            brand = self.db.query(Brand).filter(Brand.id == transaction.brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Create invoice data
            invoice_data = {
                "invoice_number": f"INV-{transaction.id:06d}",
                "date": transaction.created_at.strftime("%Y-%m-%d"),
                "due_date": (transaction.created_at + timedelta(days=30)).strftime("%Y-%m-%d"),
                "brand": {
                    "name": brand.name,
                    "email": brand.support_email
                },
                "items": [
                    {
                        "description": transaction.description,
                        "quantity": 1,
                        "unit_price": transaction.amount,
                        "total": transaction.amount
                    }
                ],
                "subtotal": transaction.amount,
                "tax": 0,  # No tax for now
                "total": transaction.amount,
                "status": transaction.status
            }
            
            return {
                "success": True,
                "invoice": invoice_data
            }
            
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_low_balance_notification(self, brand: Brand) -> None:
        """
        Send low balance notification to brand
        """
        try:
            # This would integrate with your notification service
            logger.info(f"Low balance notification sent to brand {brand.name}")
        except Exception as e:
            logger.error(f"Error sending low balance notification: {e}")
    
    def get_billing_analytics(self, brand_id: int, date_range: str = "30d") -> Dict[str, Any]:
        """
        Get billing analytics for a brand
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if date_range == "7d":
                start_date = end_date - timedelta(days=7)
            elif date_range == "30d":
                start_date = end_date - timedelta(days=30)
            elif date_range == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get transactions in date range
            transactions = self.db.query(Transaction).filter(
                and_(
                    Transaction.brand_id == brand_id,
                    Transaction.created_at >= start_date,
                    Transaction.created_at <= end_date
                )
            ).all()
            
            # Calculate analytics
            total_spent = sum(t.amount for t in transactions if t.amount > 0)
            total_credits_added = sum(t.amount for t in transactions if t.type == "credit_topup")
            total_charges = sum(t.amount for t in transactions if t.type == "complaint_charge")
            
            # Group by type
            by_type = {}
            for t in transactions:
                if t.type not in by_type:
                    by_type[t.type] = {"count": 0, "total": 0}
                by_type[t.type]["count"] += 1
                by_type[t.type]["total"] += t.amount
            
            return {
                "success": True,
                "data": {
                    "period": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "summary": {
                        "total_spent": total_spent,
                        "total_credits_added": total_credits_added,
                        "total_charges": total_charges,
                        "transaction_count": len(transactions)
                    },
                    "by_type": by_type,
                    "transactions": [
                        {
                            "id": t.id,
                            "type": t.type,
                            "amount": t.amount,
                            "date": t.created_at.isoformat(),
                            "status": t.status
                        }
                        for t in transactions
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting billing analytics: {e}")
            return {"success": False, "error": str(e)}
