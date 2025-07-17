# backend/app/api/v1/endpoints/billing.py

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.api.v1 import deps
from app.services.billing import BillingService
from app import crud, schemas
import logging
import stripe
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/topup")
async def create_credit_topup(
    topup_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Create a credit top-up payment
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        brand_id = current_user.brand_id
        if not brand_id:
            raise HTTPException(status_code=400, detail="User not associated with a brand")
        
        amount = topup_data.get("amount")
        payment_method = topup_data.get("payment_method", "stripe")
        
        if not amount or amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        billing_service = BillingService(db)
        result = billing_service.process_credit_topup(brand_id, amount, payment_method)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "payment_intent_id": result["payment_intent_id"],
            "client_secret": result["client_secret"],
            "transaction_id": result["transaction_id"]
        }
        
    except Exception as e:
        logger.error(f"Error creating credit topup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create top-up")

@router.post("/confirm-payment")
async def confirm_payment(
    payment_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Confirm payment and add credits
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        payment_intent_id = payment_data.get("payment_intent_id")
        if not payment_intent_id:
            raise HTTPException(status_code=400, detail="Payment intent ID required")
        
        billing_service = BillingService(db)
        result = billing_service.confirm_payment(payment_intent_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to confirm payment")

@router.post("/subscription/create")
async def create_subscription(
    subscription_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Create a subscription for a brand
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        brand_id = current_user.brand_id
        if not brand_id:
            raise HTTPException(status_code=400, detail="User not associated with a brand")
        
        plan_type = subscription_data.get("plan_type")
        payment_method_id = subscription_data.get("payment_method_id")
        
        if not plan_type or not payment_method_id:
            raise HTTPException(status_code=400, detail="Plan type and payment method required")
        
        billing_service = BillingService(db)
        result = billing_service.create_subscription(brand_id, plan_type, payment_method_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@router.get("/summary")
async def get_billing_summary(
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Get billing summary for the current brand
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        brand_id = current_user.brand_id
        if not brand_id:
            raise HTTPException(status_code=400, detail="User not associated with a brand")
        
        billing_service = BillingService(db)
        result = billing_service.get_brand_billing_summary(brand_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result["data"]
        
    except Exception as e:
        logger.error(f"Error getting billing summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing summary")

@router.get("/transactions")
async def get_transaction_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Get transaction history for the current brand
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        brand_id = current_user.brand_id
        if not brand_id:
            raise HTTPException(status_code=400, detail="User not associated with a brand")
        
        billing_service = BillingService(db)
        result = billing_service.get_transaction_history(brand_id, limit, offset)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result["data"]
        
    except Exception as e:
        logger.error(f"Error getting transaction history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get transaction history")

@router.post("/refund/{transaction_id}")
async def create_refund(
    transaction_id: int,
    refund_data: dict,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Create a refund for a transaction
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can create refunds")
        
        reason = refund_data.get("reason", "Customer request")
        
        billing_service = BillingService(db)
        result = billing_service.create_refund(transaction_id, reason)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating refund: {e}")
        raise HTTPException(status_code=500, detail="Failed to create refund")

@router.get("/invoice/{transaction_id}")
async def generate_invoice(
    transaction_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Generate invoice for a transaction
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        billing_service = BillingService(db)
        result = billing_service.generate_invoice(transaction_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result["invoice"]
        
    except Exception as e:
        logger.error(f"Error generating invoice: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate invoice")

@router.get("/analytics")
async def get_billing_analytics(
    date_range: str = "30d",
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Get billing analytics for the current brand
    """
    try:
        if current_user.role != "brand_user" and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        brand_id = current_user.brand_id
        if not brand_id:
            raise HTTPException(status_code=400, detail="User not associated with a brand")
        
        billing_service = BillingService(db)
        result = billing_service.get_billing_analytics(brand_id, date_range)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result["data"]
        
    except Exception as e:
        logger.error(f"Error getting billing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing analytics")

@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(deps.get_db)
):
    """
    Handle Stripe webhooks
    """
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        billing_service = BillingService(db)
        
        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            result = billing_service.confirm_payment(payment_intent["id"])
            if not result["success"]:
                logger.error(f"Failed to confirm payment: {result['error']}")
        
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            if invoice.get("subscription"):
                # Handle subscription payment
                result = billing_service.process_subscription_payment(invoice["subscription"])
                if not result["success"]:
                    logger.error(f"Failed to process subscription payment: {result['error']}")
        
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            # Handle subscription updates
            logger.info(f"Subscription updated: {subscription['id']}")
        
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            # Handle subscription cancellation
            logger.info(f"Subscription cancelled: {subscription['id']}")
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/process-complaint-charge/{ticket_id}")
async def process_complaint_charge(
    ticket_id: int,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Process complaint charge for a ticket (admin only)
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can process complaint charges")
        
        # Get ticket to find brand_id
        ticket = crud.get_ticket(db, ticket_id=ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        billing_service = BillingService(db)
        result = billing_service.process_complaint_charge(ticket_id, ticket.brand_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing complaint charge: {e}")
        raise HTTPException(status_code=500, detail="Failed to process complaint charge")

@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans
    """
    plans = {
        "basic": {
            "name": "Basic Plan",
            "price": 1000,
            "credits_per_month": 1000,
            "features": [
                "Up to 1000 credits per month",
                "Basic support",
                "Standard response time"
            ]
        },
        "professional": {
            "name": "Professional Plan",
            "price": 2000,
            "credits_per_month": 2500,
            "features": [
                "Up to 2500 credits per month",
                "Priority support",
                "Faster response time",
                "Advanced analytics"
            ]
        },
        "enterprise": {
            "name": "Enterprise Plan",
            "price": 3500,
            "credits_per_month": 5000,
            "features": [
                "Up to 5000 credits per month",
                "24/7 support",
                "Instant response time",
                "Advanced analytics",
                "Custom integrations",
                "Dedicated account manager"
            ]
        }
    }
    
    return {"plans": plans}

@router.get("/admin/billing-logs")
async def get_admin_billing_logs(
    brand_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(deps.get_db),
    current_user: schemas.User = Depends(deps.get_current_user)
):
    """
    Get billing logs for admin (admin only)
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can access billing logs")
        
        # This would be implemented in the billing service
        # For now, return a placeholder
        return {
            "message": "Admin billing logs endpoint - to be implemented",
            "brand_id": brand_id,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting admin billing logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing logs") 