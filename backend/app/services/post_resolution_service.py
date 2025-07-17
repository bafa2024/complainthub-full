# backend/app/services/post_resolution_service.py

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models import Ticket, User, Brand, FollowUpLog
from app.core.ai_engine import AIEngine
from app.adapters.twilio_adapter import TwilioAdapter
from app.adapters.whatsapp_adapter import WhatsAppAdapter
from app.adapters.telegram_adapter import TelegramAdapter
from app.services.notifications import NotificationService
from app.tasks.followup_tasks import execute_follow_up
import asyncio

logger = logging.getLogger(__name__)

class PostResolutionService:
    """
    Comprehensive Post-Resolution Verification Service
    
    Handles:
    - Automated follow-up scheduling
    - Multi-channel verification (voice, WhatsApp, email)
    - Satisfaction rating collection
    - Ticket reopening based on user feedback
    - Brand notifications
    - Analytics and reporting
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_engine = AIEngine()
        self.twilio_adapter = TwilioAdapter()
        self.whatsapp_adapter = WhatsAppAdapter()
        self.telegram_adapter = TelegramAdapter()
        self.notification_service = NotificationService()
        
    def schedule_post_resolution_verification(self, ticket_id: int, delay_hours: int = 24) -> Dict[str, Any]:
        """
        Schedule comprehensive post-resolution verification workflow
        """
        try:
            # Get ticket details
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Get user details
            user = self.db.query(User).filter(User.id == ticket.owner_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get brand details
            brand = self.db.query(Brand).filter(Brand.id == ticket.brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            # Calculate verification time
            verification_time = datetime.utcnow() + timedelta(hours=delay_hours)
            
            # Create primary follow-up (voice call)
            primary_followup = FollowUpLog(
                ticket_id=ticket_id,
                scheduled_time=verification_time,
                status="scheduled",
                follow_up_type="resolution_verification",
                channel=ticket.channel,
                user_phone=user.phone_number,
                user_email=user.email,
                brand_id=ticket.brand_id
            )
            
            self.db.add(primary_followup)
            self.db.commit()
            
            # Schedule secondary follow-ups
            secondary_followups = self._schedule_secondary_followups(ticket, user, brand, verification_time)
            
            # Schedule Celery task
            execute_follow_up.apply_async(
                args=[primary_followup.id],
                countdown=delay_hours * 3600
            )
            
            logger.info(f"Post-resolution verification scheduled for ticket {ticket_id}")
            
            return {
                "success": True,
                "primary_followup_id": primary_followup.id,
                "secondary_followup_ids": [f.id for f in secondary_followups],
                "scheduled_time": verification_time.isoformat(),
                "channels": [ticket.channel] + [f.channel for f in secondary_followups]
            }
            
        except Exception as e:
            logger.error(f"Error scheduling post-resolution verification: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _schedule_secondary_followups(self, ticket: Ticket, user: User, brand: Brand, 
                                    primary_time: datetime) -> List[FollowUpLog]:
        """
        Schedule secondary follow-up channels as backup
        """
        secondary_followups = []
        
        # WhatsApp follow-up (4 hours after primary)
        if user.phone_number:
            whatsapp_time = primary_time + timedelta(hours=4)
            whatsapp_followup = FollowUpLog(
                ticket_id=ticket.id,
                scheduled_time=whatsapp_time,
                status="scheduled",
                follow_up_type="secondary_verification",
                channel="whatsapp",
                user_phone=user.phone_number,
                user_email=user.email,
                brand_id=ticket.brand_id,
                parent_follow_up_id=primary_time  # Link to primary follow-up
            )
            self.db.add(whatsapp_followup)
            secondary_followups.append(whatsapp_followup)
            
            # Schedule WhatsApp task
            execute_follow_up.apply_async(
                args=[whatsapp_followup.id],
                countdown=4 * 3600
            )
        
        # Email follow-up (8 hours after primary)
        if user.email:
            email_time = primary_time + timedelta(hours=8)
            email_followup = FollowUpLog(
                ticket_id=ticket.id,
                scheduled_time=email_time,
                status="scheduled",
                follow_up_type="secondary_verification",
                channel="email",
                user_phone=user.phone_number,
                user_email=user.email,
                brand_id=ticket.brand_id,
                parent_follow_up_id=primary_time
            )
            self.db.add(email_followup)
            secondary_followups.append(email_followup)
            
            # Schedule email task
            execute_follow_up.apply_async(
                args=[email_followup.id],
                countdown=8 * 3600
            )
        
        return secondary_followups
    
    def execute_verification_call(self, followup_id: int) -> Dict[str, Any]:
        """
        Execute automated verification call
        """
        try:
            followup = self.db.query(FollowUpLog).filter(FollowUpLog.id == followup_id).first()
            if not followup:
                return {"success": False, "error": "Follow-up not found"}
            
            ticket = self.db.query(Ticket).filter(Ticket.id == followup.ticket_id).first()
            user = self.db.query(User).filter(User.id == ticket.owner_id).first()
            brand = self.db.query(Brand).filter(Brand.id == ticket.brand_id).first()
            
            # Update follow-up status
            followup.status = "in_progress"
            followup.started_at = datetime.utcnow()
            self.db.commit()
            
            # Generate verification message
            verification_message = self._generate_verification_message(ticket, brand)
            
            # Execute call based on channel
            if followup.channel == "voice":
                result = self._execute_voice_verification(followup, verification_message, user, brand)
            elif followup.channel == "whatsapp":
                result = self._execute_whatsapp_verification(followup, verification_message, user)
            elif followup.channel == "email":
                result = self._execute_email_verification(followup, verification_message, user, brand)
            else:
                result = {"success": False, "error": f"Unsupported channel: {followup.channel}"}
            
            # Update follow-up status
            followup.status = "completed" if result["success"] else "failed"
            followup.completed_at = datetime.utcnow()
            followup.result = json.dumps(result)
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing verification call: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _generate_verification_message(self, ticket: Ticket, brand: Brand) -> str:
        """
        Generate personalized verification message
        """
        base_message = f"""
        Hello! This is a follow-up call from {brand.name} regarding your recent complaint (Ticket #{ticket.id}).
        
        We want to ensure that your issue has been resolved to your satisfaction. 
        
        Please press:
        1 - If your issue has been resolved and you're satisfied
        2 - If your issue has NOT been resolved or you're not satisfied
        3 - To speak with a customer service representative
        
        Thank you for your time!
        """
        
        return base_message.strip()
    
    def _execute_voice_verification(self, followup: FollowUpLog, message: str, 
                                  user: User, brand: Brand) -> Dict[str, Any]:
        """
        Execute voice verification call
        """
        try:
            if not user.phone_number:
                return {"success": False, "error": "No phone number available"}
            
            # Create interactive voice response
            ivr_options = [
                {"digit": "1", "description": "Issue resolved and satisfied"},
                {"digit": "2", "description": "Issue not resolved or not satisfied"},
                {"digit": "3", "description": "Speak with customer service"}
            ]
            
            # Generate TwiML for voice call
            twiml_response = self.twilio_adapter.create_interactive_voice_response(ivr_options)
            
            # In a real implementation, this would initiate the actual call
            # For now, we'll simulate the call
            logger.info(f"Voice verification call initiated to {user.phone_number}")
            
            return {
                "success": True,
                "channel": "voice",
                "phone_number": user.phone_number,
                "twiml_response": twiml_response,
                "message": "Voice verification call initiated"
            }
            
        except Exception as e:
            logger.error(f"Error executing voice verification: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_whatsapp_verification(self, followup: FollowUpLog, message: str, 
                                     user: User) -> Dict[str, Any]:
        """
        Execute WhatsApp verification message
        """
        try:
            if not user.phone_number:
                return {"success": False, "error": "No phone number available"}
            
            # Add quick reply buttons
            quick_replies = [
                {"text": "✅ RESOLVED", "callback_data": f"resolved_{followup.ticket_id}"},
                {"text": "❌ NOT RESOLVED", "callback_data": f"not_resolved_{followup.ticket_id}"},
                {"text": "📞 SPEAK TO AGENT", "callback_data": f"speak_agent_{followup.ticket_id}"}
            ]
            
            # Send WhatsApp message
            success = self.whatsapp_adapter.send_message(
                to_number=user.phone_number,
                message=message,
                quick_replies=quick_replies
            )
            
            return {
                "success": success,
                "channel": "whatsapp",
                "phone_number": user.phone_number,
                "message": "WhatsApp verification message sent" if success else "Failed to send WhatsApp message"
            }
            
        except Exception as e:
            logger.error(f"Error executing WhatsApp verification: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_email_verification(self, followup: FollowUpLog, message: str, 
                                  user: User, brand: Brand) -> Dict[str, Any]:
        """
        Execute email verification
        """
        try:
            if not user.email:
                return {"success": False, "error": "No email available"}
            
            # Send email notification
            email_sent = self.notification_service.send_email(
                to_email=user.email,
                subject=f"Follow-up: Your complaint with {brand.name}",
                template="verification_email",
                context={
                    "user_name": user.full_name,
                    "brand_name": brand.name,
                    "ticket_id": followup.ticket_id,
                    "verification_message": message
                }
            )
            
            return {
                "success": email_sent,
                "channel": "email",
                "email": user.email,
                "message": "Email verification sent" if email_sent else "Failed to send email"
            }
            
        except Exception as e:
            logger.error(f"Error executing email verification: {e}")
            return {"success": False, "error": str(e)}
    
    def handle_verification_response(self, followup_id: int, response: str, 
                                   rating: Optional[int] = None) -> Dict[str, Any]:
        """
        Handle user response to verification
        """
        try:
            followup = self.db.query(FollowUpLog).filter(FollowUpLog.id == followup_id).first()
            if not followup:
                return {"success": False, "error": "Follow-up not found"}
            
            ticket = self.db.query(Ticket).filter(Ticket.id == followup.ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Update follow-up with response
            followup.user_response = response
            followup.rating = rating
            followup.responded_at = datetime.utcnow()
            
            # Process response
            if response.lower() in ["resolved", "1", "yes", "satisfied"]:
                # Mark as verified resolved
                ticket.status = "verified_resolved"
                ticket.satisfaction_rating = rating or 5
                ticket.resolved_at = datetime.utcnow()
                
                # Send satisfaction survey if rating not provided
                if not rating:
                    self._schedule_satisfaction_survey(followup, 1)  # 1 hour later
                
            elif response.lower() in ["not_resolved", "2", "no", "unsatisfied"]:
                # Reopen ticket
                ticket.status = "reopened"
                ticket.reopened_at = datetime.utcnow()
                
                # Notify brand about reopening
                self._notify_brand_reopening(ticket)
                
            elif response.lower() in ["speak_agent", "3"]:
                # Schedule callback
                self._schedule_customer_service_callback(followup, 30)  # 30 minutes later
            
            self.db.commit()
            
            return {
                "success": True,
                "ticket_status": ticket.status,
                "message": "Response processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error handling verification response: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _schedule_satisfaction_survey(self, followup: FollowUpLog, delay_hours: int):
        """
        Schedule satisfaction survey
        """
        try:
            survey_time = datetime.utcnow() + timedelta(hours=delay_hours)
            
            survey_followup = FollowUpLog(
                ticket_id=followup.ticket_id,
                scheduled_time=survey_time,
                status="scheduled",
                follow_up_type="satisfaction_survey",
                channel=followup.channel,
                user_phone=followup.user_phone,
                user_email=followup.user_email,
                brand_id=followup.brand_id,
                parent_follow_up_id=followup.id
            )
            
            self.db.add(survey_followup)
            self.db.commit()
            
            # Schedule task
            execute_follow_up.apply_async(
                args=[survey_followup.id],
                countdown=delay_hours * 3600
            )
            
        except Exception as e:
            logger.error(f"Error scheduling satisfaction survey: {e}")
    
    def _notify_brand_reopening(self, ticket: Ticket):
        """
        Notify brand about ticket reopening
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == ticket.brand_id).first()
            if not brand:
                return
            
            # Send notification to brand
            self.notification_service.send_email(
                to_email=brand.support_email,
                subject=f"Ticket #{ticket.id} Reopened - Action Required",
                template="ticket_reopened",
                context={
                    "ticket_id": ticket.id,
                    "ticket_title": ticket.title,
                    "user_name": ticket.owner.full_name if ticket.owner else "Unknown",
                    "reopened_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Brand notified about ticket {ticket.id} reopening")
            
        except Exception as e:
            logger.error(f"Error notifying brand about reopening: {e}")
    
    def _schedule_customer_service_callback(self, followup: FollowUpLog, delay_minutes: int):
        """
        Schedule customer service callback
        """
        try:
            callback_time = datetime.utcnow() + timedelta(minutes=delay_minutes)
            
            callback_followup = FollowUpLog(
                ticket_id=followup.ticket_id,
                scheduled_time=callback_time,
                status="scheduled",
                follow_up_type="customer_service_callback",
                channel="voice",
                user_phone=followup.user_phone,
                user_email=followup.user_email,
                brand_id=followup.brand_id,
                parent_follow_up_id=followup.id
            )
            
            self.db.add(callback_followup)
            self.db.commit()
            
            # Schedule task
            execute_follow_up.apply_async(
                args=[callback_followup.id],
                countdown=delay_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"Error scheduling customer service callback: {e}")
    
    def get_verification_analytics(self, brand_id: Optional[int] = None, 
                                 days: int = 30) -> Dict[str, Any]:
        """
        Get verification analytics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            query = self.db.query(FollowUpLog).filter(
                FollowUpLog.follow_up_type == "resolution_verification",
                FollowUpLog.created_at >= cutoff_date
            )
            
            if brand_id:
                query = query.filter(FollowUpLog.brand_id == brand_id)
            
            followups = query.all()
            
            # Calculate analytics
            total_followups = len(followups)
            successful_followups = len([f for f in followups if f.status == "completed"])
            response_rate = (len([f for f in followups if f.user_response]) / total_followups * 100) if total_followups > 0 else 0
            
            # Satisfaction ratings
            ratings = [f.rating for f in followups if f.rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Response analysis
            resolved_count = len([f for f in followups if f.user_response and "resolved" in f.user_response.lower()])
            reopened_count = len([f for f in followups if f.user_response and "not_resolved" in f.user_response.lower()])
            
            return {
                "success": True,
                "analytics": {
                    "total_followups": total_followups,
                    "successful_followups": successful_followups,
                    "response_rate": round(response_rate, 2),
                    "average_rating": round(avg_rating, 2),
                    "resolved_count": resolved_count,
                    "reopened_count": reopened_count,
                    "resolution_rate": round((resolved_count / total_followups * 100) if total_followups > 0 else 0, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting verification analytics: {e}")
            return {"success": False, "error": str(e)} 