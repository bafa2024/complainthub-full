# backend/app/services/followup_service.py

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models import Ticket, User, Brand, FollowUpLog
from app.schemas import FollowUpLogCreate, FollowUpLogUpdate
from app.adapters.twilio_adapter import TwilioAdapter
from app.adapters.whatsapp_adapter import WhatsAppAdapter
from app.services.notifications import send_email
from app.core.ai_engine import AIEngine
from app.config.settings import settings
import json

logger = logging.getLogger(__name__)

class FollowUpService:
    def __init__(self, db: Session):
        self.db = db
        self.twilio_adapter = TwilioAdapter()
        self.whatsapp_adapter = WhatsAppAdapter()
        self.ai_engine = AIEngine()
    
    def schedule_follow_up(self, ticket_id: int, delay_hours: int = 24) -> Dict[str, Any]:
        """
        Schedule a follow-up for a resolved ticket
        """
        try:
            # Get ticket details
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Calculate follow-up time
            follow_up_time = datetime.utcnow() + timedelta(hours=delay_hours)
            
            # Create follow-up log entry
            follow_up = FollowUpLog(
                ticket_id=ticket_id,
                scheduled_time=follow_up_time,
                status="scheduled",
                follow_up_type="resolution_confirmation",
                channel=ticket.channel,
                user_phone=ticket.user_phone,
                user_email=ticket.user_email,
                brand_id=ticket.brand_id
            )
            
            self.db.add(follow_up)
            self.db.commit()
            
            # Schedule the actual follow-up task
            self._schedule_celery_task(follow_up.id, follow_up_time)
            
            logger.info(f"Follow-up scheduled for ticket {ticket_id} at {follow_up_time}")
            
            return {
                "success": True,
                "follow_up_id": follow_up.id,
                "scheduled_time": follow_up_time.isoformat(),
                "message": f"Follow-up scheduled for {delay_hours} hours from now"
            }
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _schedule_celery_task(self, follow_up_id: int, scheduled_time: datetime):
        """
        Schedule Celery task for follow-up execution
        """
        try:
            from app.celery_app import follow_up_task
            
            # Calculate delay in seconds
            delay_seconds = (scheduled_time - datetime.utcnow()).total_seconds()
            if delay_seconds > 0:
                follow_up_task.apply_async(
                    args=[follow_up_id],
                    countdown=int(delay_seconds)
                )
                logger.info(f"Celery task scheduled for follow-up {follow_up_id}")
            else:
                # Execute immediately if time has passed
                follow_up_task.delay(follow_up_id)
                
        except Exception as e:
            logger.error(f"Error scheduling Celery task: {e}")
    
    def execute_follow_up(self, follow_up_id: int) -> Dict[str, Any]:
        """
        Execute a scheduled follow-up
        """
        try:
            # Get follow-up details
            follow_up = self.db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
            if not follow_up:
                return {"success": False, "error": "Follow-up not found"}
            
            # Get ticket details
            ticket = self.db.query(Ticket).filter(Ticket.id == follow_up.ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Get brand details
            brand = self.db.query(Brand).filter(Brand.id == follow_up.brand_id).first()
            
            # Update follow-up status
            follow_up.status = "in_progress"
            follow_up.started_at = datetime.utcnow()
            self.db.commit()
            
            # Execute follow-up based on original channel
            result = self._execute_channel_follow_up(follow_up, ticket, brand)
            
            # Update follow-up status
            follow_up.status = "completed" if result["success"] else "failed"
            follow_up.completed_at = datetime.utcnow()
            follow_up.result = json.dumps(result)
            self.db.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing follow-up: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _execute_channel_follow_up(self, follow_up: FollowUpLog, ticket: Ticket, brand: Brand) -> Dict[str, Any]:
        """
        Execute follow-up based on original channel with comprehensive error handling
        """
        try:
            # Prepare follow-up message
            message = self._generate_follow_up_message(ticket, brand)
            
            # Execute based on channel
            if follow_up.channel == "voice":
                return self._execute_voice_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "whatsapp":
                return self._execute_whatsapp_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "email":
                return self._execute_email_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "telegram":
                return self._execute_telegram_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "webchat":
                return self._execute_webchat_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "instagram":
                return self._execute_instagram_follow_up_with_fallback(follow_up, message, ticket)
            elif follow_up.channel == "linkedin":
                return self._execute_linkedin_follow_up_with_fallback(follow_up, message, ticket)
            else:
                # Default to email for unknown channels
                return self._execute_email_follow_up_with_fallback(follow_up, message, ticket)
                
        except Exception as e:
            logger.error(f"Error executing channel follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_follow_up_message(self, ticket: Ticket, brand: Brand) -> str:
        """
        Generate personalized follow-up message
        """
        try:
            # Use AI to generate contextual message
            context = f"""
            Ticket ID: {ticket.id}
            Brand: {brand.name if brand else 'Unknown'}
            Issue: {ticket.title}
            Resolution Status: {ticket.status}
            """
            
            prompt = f"""
            Generate a friendly follow-up message for a customer whose complaint was marked as resolved.
            
            Context: {context}
            
            The message should:
            1. Be warm and professional
            2. Ask if their issue was resolved satisfactorily
            3. Provide options to confirm resolution or reopen if needed
            4. Ask for a satisfaction rating (0-5)
            5. Include the ticket reference
            
            Keep it concise and conversational.
            """
            
            if self.ai_engine.has_openai_key:
                message = self.ai_engine._get_chat_completion(
                    system_prompt="You are a customer service representative following up on resolved complaints.",
                    user_prompt=prompt
                )
            else:
                # Fallback message
                message = f"""
                Hello! We're following up on your complaint (Ticket #{ticket.id}) about {ticket.title}.
                
                According to {brand.name if brand else 'our team'}, your issue has been resolved. 
                
                If you're satisfied with the resolution, you can simply ignore this message or reply with "RESOLVED".
                
                If you're NOT satisfied, please reply with "NOT RESOLVED" and we'll reopen your case immediately.
                
                We'd also appreciate if you could rate your experience from 1-5 (where 5 is excellent).
                
                Thank you for your patience!
                """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Error generating follow-up message: {e}")
            return "Hello! We're following up on your recent complaint. Please let us know if your issue was resolved satisfactorily."
    
    def _execute_voice_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute voice follow-up call
        """
        try:
            if not follow_up.user_phone:
                return {"success": False, "error": "No phone number available"}
            
            # Generate TwiML for follow-up call
            twiml_response = self._generate_follow_up_twiml(message, ticket.id)
            
            # Make outbound call
            call_result = self.twilio_adapter.make_outbound_call(
                to_number=follow_up.user_phone,
                twiml=twiml_response,
                call_type="follow_up"
            )
            
            if call_result["success"]:
                # Schedule secondary follow-up if call fails
                self._schedule_secondary_follow_up(follow_up, "whatsapp", 2)  # 2 hours later
                
                return {
                    "success": True,
                    "channel": "voice",
                    "call_sid": call_result.get("call_sid"),
                    "message": "Voice follow-up call initiated"
                }
            else:
                # If voice call fails, try WhatsApp immediately
                return self._execute_whatsapp_follow_up(follow_up, message, ticket)
                
        except Exception as e:
            logger.error(f"Error executing voice follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_whatsapp_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute WhatsApp follow-up message
        """
        try:
            if not follow_up.user_phone:
                return {"success": False, "error": "No phone number available"}
            
            # Add quick reply buttons
            quick_replies = [
                {"text": "✅ RESOLVED", "callback_data": f"resolved_{ticket.id}"},
                {"text": "❌ NOT RESOLVED", "callback_data": f"not_resolved_{ticket.id}"},
                {"text": "⭐ Rate 5/5", "callback_data": f"rate_5_{ticket.id}"},
                {"text": "⭐ Rate 4/5", "callback_data": f"rate_4_{ticket.id}"},
                {"text": "⭐ Rate 3/5", "callback_data": f"rate_3_{ticket.id}"}
            ]
            
            # Send WhatsApp message
            success = self.whatsapp_adapter.send_message(
                to_number=follow_up.user_phone,
                message=message,
                quick_replies=quick_replies
            )
            
            if success:
                # Schedule email follow-up as backup
                self._schedule_secondary_follow_up(follow_up, "email", 4)  # 4 hours later
                
                return {
                    "success": True,
                    "channel": "whatsapp",
                    "message": "WhatsApp follow-up message sent"
                }
            else:
                # If WhatsApp fails, try email
                return self._execute_email_follow_up(follow_up, message, ticket)
                
        except Exception as e:
            logger.error(f"Error executing WhatsApp follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_email_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute email follow-up
        """
        try:
            if not follow_up.user_email:
                return {"success": False, "error": "No email address available"}
            
            # Create HTML email template
            html_content = self._generate_email_template(message, ticket)
            
            # Send email
            success = send_email(
                to_email=follow_up.user_email,
                subject=f"Follow-up: Your complaint (Ticket #{ticket.id})",
                html_content=html_content,
                text_content=message
            )
            
            return {
                "success": success,
                "channel": "email",
                "message": "Email follow-up sent" if success else "Failed to send email"
            }
            
        except Exception as e:
            logger.error(f"Error executing email follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_telegram_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute Telegram follow-up message
        """
        try:
            from app.adapters.telegram_adapter import TelegramAdapter
            telegram_adapter = TelegramAdapter()
            
            # Create inline keyboard
            keyboard = [
                [{"text": "✅ Resolved", "callback_data": f"resolved_{ticket.id}"}],
                [{"text": "❌ Not Resolved", "callback_data": f"not_resolved_{ticket.id}"}],
                [{"text": "⭐ Rate 5", "callback_data": f"rate_5_{ticket.id}"},
                 {"text": "⭐ Rate 4", "callback_data": f"rate_4_{ticket.id}"},
                 {"text": "⭐ Rate 3", "callback_data": f"rate_3_{ticket.id}"}]
            ]
            
            # Send Telegram message
            success = telegram_adapter.send_message(
                chat_id=follow_up.user_telegram_id,
                message=message,
                inline_keyboard=keyboard
            )
            
            return {
                "success": success,
                "channel": "telegram",
                "message": "Telegram follow-up sent" if success else "Failed to send Telegram message"
            }
            
        except Exception as e:
            logger.error(f"Error executing Telegram follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_webchat_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute WebChat follow-up message
        """
        try:
            # Send WebSocket message to user
            from app.websocket import websocket_manager
            
            success = websocket_manager.send_message_to_user(
                user_id=follow_up.user_id,
                message={
                    "type": "follow_up",
                    "ticket_id": ticket.id,
                    "message": message,
                    "actions": [
                        {"text": "Resolved", "action": "resolved"},
                        {"text": "Not Resolved", "action": "not_resolved"},
                        {"text": "Rate 5/5", "action": "rate_5"},
                        {"text": "Rate 4/5", "action": "rate_4"},
                        {"text": "Rate 3/5", "action": "rate_3"}
                    ]
                }
            )
            
            return {
                "success": success,
                "channel": "webchat",
                "message": "WebChat follow-up sent" if success else "Failed to send WebChat message"
            }
            
        except Exception as e:
            logger.error(f"Error executing WebChat follow-up: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_multi_channel_follow_up(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute follow-up across multiple channels
        """
        results = []
        
        # Try WhatsApp first
        if follow_up.user_phone:
            whatsapp_result = self._execute_whatsapp_follow_up(follow_up, message, ticket)
            results.append(("whatsapp", whatsapp_result))
            
            if whatsapp_result["success"]:
                return whatsapp_result
        
        # Try email
        if follow_up.user_email:
            email_result = self._execute_email_follow_up(follow_up, message, ticket)
            results.append(("email", email_result))
            
            if email_result["success"]:
                return email_result
        
        # If all failed, return the last result
        if results:
            return results[-1][1]
        else:
            return {"success": False, "error": "No contact methods available"}
    
    def _schedule_secondary_follow_up(self, primary_follow_up: FollowUpLog, channel: str, delay_hours: int):
        """
        Schedule a secondary follow-up if primary fails
        """
        try:
            secondary_time = datetime.utcnow() + timedelta(hours=delay_hours)
            
            secondary_follow_up = FollowUpLog(
                ticket_id=primary_follow_up.ticket_id,
                scheduled_time=secondary_time,
                status="scheduled",
                follow_up_type="secondary_follow_up",
                channel=channel,
                user_phone=primary_follow_up.user_phone,
                user_email=primary_follow_up.user_email,
                brand_id=primary_follow_up.brand_id,
                parent_follow_up_id=primary_follow_up.id
            )
            
            self.db.add(secondary_follow_up)
            self.db.commit()
            
            # Schedule secondary task
            self._schedule_celery_task(secondary_follow_up.id, secondary_time)
            
            logger.info(f"Secondary follow-up scheduled via {channel} for ticket {primary_follow_up.ticket_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling secondary follow-up: {e}")
    
    def _generate_follow_up_twiml(self, message: str, ticket_id: int) -> str:
        """
        Generate TwiML for follow-up voice call
        """
        return f"""
        <Response>
            <Say voice="alice">Hello! This is a follow-up call regarding your complaint ticket number {ticket_id}.</Say>
            <Say voice="alice">{message}</Say>
            <Gather numDigits="1" action="/api/v1/webhook/voice/follow-up-response" method="POST">
                <Say voice="alice">Press 1 if your issue was resolved satisfactorily. Press 2 if you need further assistance. Press 3 to rate your experience from 1 to 5.</Say>
            </Gather>
            <Say voice="alice">Thank you for your time. Goodbye!</Say>
        </Response>
        """
    
    def _generate_email_template(self, message: str, ticket: Ticket) -> str:
        """
        Generate HTML email template for follow-up
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Follow-up: Your Complaint</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .content {{ background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .button {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
                .button.success {{ background: #28a745; }}
                .button.danger {{ background: #dc3545; }}
                .footer {{ margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Follow-up: Your Complaint</h2>
                    <p><strong>Ticket ID:</strong> #{ticket.id}</p>
                </div>
                
                <div class="content">
                    <p>{message.replace(chr(10), '<br>')}</p>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="https://your-domain.com/confirm-resolution/{ticket.id}?status=resolved" class="button success">✅ Issue Resolved</a>
                        <a href="https://your-domain.com/confirm-resolution/{ticket.id}?status=not_resolved" class="button danger">❌ Issue Not Resolved</a>
                    </div>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <p><strong>Rate your experience:</strong></p>
                        <a href="https://your-domain.com/rate/{ticket.id}?rating=5" class="button">⭐ 5/5</a>
                        <a href="https://your-domain.com/rate/{ticket.id}?rating=4" class="button">⭐ 4/5</a>
                        <a href="https://your-domain.com/rate/{ticket.id}?rating=3" class="button">⭐ 3/5</a>
                        <a href="https://your-domain.com/rate/{ticket.id}?rating=2" class="button">⭐ 2/5</a>
                        <a href="https://your-domain.com/rate/{ticket.id}?rating=1" class="button">⭐ 1/5</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>This is an automated follow-up message. If you have any questions, please contact our support team.</p>
                    <p>Ticket ID: {ticket.id} | Sent: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def handle_follow_up_response(self, follow_up_id: int, response: str, rating: Optional[int] = None) -> Dict[str, Any]:
        """
        Handle user response to follow-up
        """
        try:
            follow_up = self.db.query(FollowUpLog).filter(FollowUpLog.id == follow_up_id).first()
            if not follow_up:
                return {"success": False, "error": "Follow-up not found"}
            
            ticket = self.db.query(Ticket).filter(Ticket.id == follow_up.ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Update follow-up with response
            follow_up.user_response = response
            follow_up.rating = rating
            follow_up.responded_at = datetime.utcnow()
            
            # Handle different response types
            if response.lower() in ["resolved", "1", "yes", "satisfied"]:
                # Mark ticket as confirmed resolved
                ticket.status = "confirmed_resolved"
                ticket.resolved_at = datetime.utcnow()
                
                # Schedule satisfaction rating request if not provided
                if not rating:
                    self._schedule_rating_request(follow_up, 1)  # 1 hour later
                
            elif response.lower() in ["not_resolved", "2", "no", "unsatisfied"]:
                # Reopen ticket
                ticket.status = "reopened"
                ticket.reopened_at = datetime.utcnow()
                
                # Notify brand about reopening
                self._notify_brand_reopening(ticket)
                
            elif response.startswith("rate_"):
                # Handle rating
                try:
                    rating_value = int(response.split("_")[1])
                    ticket.satisfaction_rating = rating_value
                    ticket.rated_at = datetime.utcnow()
                except (ValueError, IndexError):
                    pass
            
            self.db.commit()
            
            return {
                "success": True,
                "ticket_status": ticket.status,
                "message": "Response processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error handling follow-up response: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def _schedule_rating_request(self, follow_up: FollowUpLog, delay_hours: int):
        """
        Schedule a rating request if user confirmed resolution but didn't rate
        """
        try:
            rating_time = datetime.utcnow() + timedelta(hours=delay_hours)
            
            rating_follow_up = FollowUpLog(
                ticket_id=follow_up.ticket_id,
                scheduled_time=rating_time,
                status="scheduled",
                follow_up_type="rating_request",
                channel=follow_up.channel,
                user_phone=follow_up.user_phone,
                user_email=follow_up.user_email,
                brand_id=follow_up.brand_id
            )
            
            self.db.add(rating_follow_up)
            self.db.commit()
            
            self._schedule_celery_task(rating_follow_up.id, rating_time)
            
        except Exception as e:
            logger.error(f"Error scheduling rating request: {e}")
    
    def _notify_brand_reopening(self, ticket: Ticket):
        """
        Notify brand that ticket has been reopened
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == ticket.brand_id).first()
            if brand and brand.support_email:
                subject = f"URGENT: Ticket #{ticket.id} Reopened by Customer"
                message = f"""
                A customer has indicated that their issue (Ticket #{ticket.id}) was not resolved satisfactorily.
                
                Ticket Details:
                - Title: {ticket.title}
                - Description: {ticket.description}
                - Original Channel: {ticket.channel}
                
                Please review and take immediate action to resolve this issue.
                
                This is an automated notification.
                """
                
                send_email(
                    to_email=brand.support_email,
                    subject=subject,
                    html_content=message,
                    text_content=message
                )
                
        except Exception as e:
            logger.error(f"Error notifying brand about reopening: {e}")
    
    def auto_close_ticket(self, ticket_id: int) -> Dict[str, Any]:
        """
        Automatically close ticket after 48 hours of no response
        """
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Check if ticket was marked resolved but no follow-up response
            if ticket.status == "resolved" and not ticket.resolved_at:
                # Check if 48 hours have passed since resolution
                if ticket.updated_at and (datetime.utcnow() - ticket.updated_at).total_seconds() > 48 * 3600:
                    ticket.status = "auto_closed"
                    ticket.closed_at = datetime.utcnow()
                    ticket.auto_closed = True
                    
                    self.db.commit()
                    
                    logger.info(f"Ticket {ticket_id} auto-closed after 48 hours")
                    
                    return {
                        "success": True,
                        "message": "Ticket auto-closed after 48 hours of no response"
                    }
            
            return {"success": False, "message": "Ticket not eligible for auto-closure"}
            
        except Exception as e:
            logger.error(f"Error auto-closing ticket: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_follow_up_stats(self, brand_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get follow-up statistics
        """
        try:
            query = self.db.query(FollowUpLog)
            
            if brand_id:
                query = query.filter(FollowUpLog.brand_id == brand_id)
            
            # Filter by date range
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(FollowUpLog.created_at >= start_date)
            
            follow_ups = query.all()
            
            total = len(follow_ups)
            successful = len([f for f in follow_ups if f.status == "completed"])
            failed = len([f for f in follow_ups if f.status == "failed"])
            pending = len([f for f in follow_ups if f.status == "scheduled"])
            
            # Channel breakdown
            channels = {}
            for follow_up in follow_ups:
                channel = follow_up.channel
                if channel not in channels:
                    channels[channel] = {"total": 0, "successful": 0, "failed": 0}
                channels[channel]["total"] += 1
                if follow_up.status == "completed":
                    channels[channel]["successful"] += 1
                elif follow_up.status == "failed":
                    channels[channel]["failed"] += 1
            
            return {
                "total_follow_ups": total,
                "successful": successful,
                "failed": failed,
                "pending": pending,
                "success_rate": (successful / total * 100) if total > 0 else 0,
                "channels": channels,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting follow-up stats: {e}")
            return {"error": str(e)} 

    def _execute_voice_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute voice follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: Voice call
            voice_result = self._execute_voice_follow_up(follow_up, message, ticket)
            
            if voice_result["success"]:
                return voice_result
            
            # Secondary attempt: WhatsApp (if available)
            if follow_up.user_phone:
                whatsapp_result = self._execute_whatsapp_follow_up(follow_up, message, ticket)
                if whatsapp_result["success"]:
                    logger.info(f"Voice follow-up failed, WhatsApp fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "voice",
                        "fallback_channel": "whatsapp",
                        "message": "Follow-up sent via WhatsApp fallback"
                    }
            
            # Tertiary attempt: SMS (if available)
            if follow_up.user_phone:
                sms_result = self._execute_sms_follow_up(follow_up, message, ticket)
                if sms_result["success"]:
                    logger.info(f"Voice and WhatsApp failed, SMS fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "voice",
                        "fallback_channel": "sms",
                        "message": "Follow-up sent via SMS fallback"
                    }
            
            # Final attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"All voice channels failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "voice",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # All attempts failed
            logger.error(f"All follow-up channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["voice", "whatsapp", "sms", "email"]
            }
            
        except Exception as e:
            logger.error(f"Error in voice follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_whatsapp_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute WhatsApp follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: WhatsApp
            whatsapp_result = self._execute_whatsapp_follow_up(follow_up, message, ticket)
            
            if whatsapp_result["success"]:
                return whatsapp_result
            
            # Secondary attempt: SMS (if available)
            if follow_up.user_phone:
                sms_result = self._execute_sms_follow_up(follow_up, message, ticket)
                if sms_result["success"]:
                    logger.info(f"WhatsApp failed, SMS fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "whatsapp",
                        "fallback_channel": "sms",
                        "message": "Follow-up sent via SMS fallback"
                    }
            
            # Tertiary attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"WhatsApp and SMS failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "whatsapp",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # All attempts failed
            logger.error(f"All WhatsApp fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["whatsapp", "sms", "email"]
            }
            
        except Exception as e:
            logger.error(f"Error in WhatsApp follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_email_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute email follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: Email
            email_result = self._execute_email_follow_up(follow_up, message, ticket)
            
            if email_result["success"]:
                return email_result
            
            # Secondary attempt: SMS (if available)
            if follow_up.user_phone:
                sms_result = self._execute_sms_follow_up(follow_up, message, ticket)
                if sms_result["success"]:
                    logger.info(f"Email failed, SMS fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "email",
                        "fallback_channel": "sms",
                        "message": "Follow-up sent via SMS fallback"
                    }
            
            # Tertiary attempt: WebChat notification (if user is online)
            webchat_result = self._execute_webchat_follow_up(follow_up, message, ticket)
            if webchat_result["success"]:
                logger.info(f"Email and SMS failed, WebChat fallback successful for ticket {ticket.id}")
                return {
                    "success": True,
                    "primary_channel": "email",
                    "fallback_channel": "webchat",
                    "message": "Follow-up sent via WebChat fallback"
                }
            
            # All attempts failed
            logger.error(f"All email fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["email", "sms", "webchat"]
            }
            
        except Exception as e:
            logger.error(f"Error in email follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_telegram_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute Telegram follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: Telegram
            telegram_result = self._execute_telegram_follow_up(follow_up, message, ticket)
            
            if telegram_result["success"]:
                return telegram_result
            
            # Secondary attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"Telegram failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "telegram",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # Tertiary attempt: WebChat notification
            webchat_result = self._execute_webchat_follow_up(follow_up, message, ticket)
            if webchat_result["success"]:
                logger.info(f"Telegram and email failed, WebChat fallback successful for ticket {ticket.id}")
                return {
                    "success": True,
                    "primary_channel": "telegram",
                    "fallback_channel": "webchat",
                    "message": "Follow-up sent via WebChat fallback"
                }
            
            # All attempts failed
            logger.error(f"All Telegram fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["telegram", "email", "webchat"]
            }
            
        except Exception as e:
            logger.error(f"Error in Telegram follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_webchat_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute WebChat follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: WebChat
            webchat_result = self._execute_webchat_follow_up(follow_up, message, ticket)
            
            if webchat_result["success"]:
                return webchat_result
            
            # Secondary attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"WebChat failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "webchat",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # Tertiary attempt: SMS (if available)
            if follow_up.user_phone:
                sms_result = self._execute_sms_follow_up(follow_up, message, ticket)
                if sms_result["success"]:
                    logger.info(f"WebChat and email failed, SMS fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "webchat",
                        "fallback_channel": "sms",
                        "message": "Follow-up sent via SMS fallback"
                    }
            
            # All attempts failed
            logger.error(f"All WebChat fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["webchat", "email", "sms"]
            }
            
        except Exception as e:
            logger.error(f"Error in WebChat follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_instagram_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute Instagram follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: Instagram
            instagram_result = self._execute_instagram_follow_up(follow_up, message, ticket)
            
            if instagram_result["success"]:
                return instagram_result
            
            # Secondary attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"Instagram failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "instagram",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # Tertiary attempt: WebChat notification
            webchat_result = self._execute_webchat_follow_up(follow_up, message, ticket)
            if webchat_result["success"]:
                logger.info(f"Instagram and email failed, WebChat fallback successful for ticket {ticket.id}")
                return {
                    "success": True,
                    "primary_channel": "instagram",
                    "fallback_channel": "webchat",
                    "message": "Follow-up sent via WebChat fallback"
                }
            
            # All attempts failed
            logger.error(f"All Instagram fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["instagram", "email", "webchat"]
            }
            
        except Exception as e:
            logger.error(f"Error in Instagram follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_linkedin_follow_up_with_fallback(self, follow_up: FollowUpLog, message: str, ticket: Ticket) -> Dict[str, Any]:
        """
        Execute LinkedIn follow-up with comprehensive fallback handling
        """
        try:
            # Primary attempt: LinkedIn
            linkedin_result = self._execute_linkedin_follow_up(follow_up, message, ticket)
            
            if linkedin_result["success"]:
                return linkedin_result
            
            # Secondary attempt: Email (if available)
            if follow_up.user_email:
                email_result = self._execute_email_follow_up(follow_up, message, ticket)
                if email_result["success"]:
                    logger.info(f"LinkedIn failed, email fallback successful for ticket {ticket.id}")
                    return {
                        "success": True,
                        "primary_channel": "linkedin",
                        "fallback_channel": "email",
                        "message": "Follow-up sent via email fallback"
                    }
            
            # Tertiary attempt: WebChat notification
            webchat_result = self._execute_webchat_follow_up(follow_up, message, ticket)
            if webchat_result["success"]:
                logger.info(f"LinkedIn and email failed, WebChat fallback successful for ticket {ticket.id}")
                return {
                    "success": True,
                    "primary_channel": "linkedin",
                    "fallback_channel": "webchat",
                    "message": "Follow-up sent via WebChat fallback"
                }
            
            # All attempts failed
            logger.error(f"All LinkedIn fallback channels failed for ticket {ticket.id}")
            return {
                "success": False,
                "error": "All delivery channels failed",
                "attempts": ["linkedin", "email", "webchat"]
            }
            
        except Exception as e:
            logger.error(f"Error in LinkedIn follow-up with fallback: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_delivery_failure(self, follow_up: FollowUpLog, error: str, attempt_count: int = 0):
        """
        Handle delivery failures with intelligent retry logic
        """
        try:
            max_retries = 3
            retry_delays = [1, 4, 12]  # Hours between retries
            
            if attempt_count >= max_retries:
                # Mark as permanently failed
                follow_up.status = "failed"
                follow_up.error_message = f"Max retries exceeded: {error}"
                follow_up.completed_at = datetime.utcnow()
                self.db.commit()
                
                # Notify brand about failed follow-up
                self._notify_brand_of_failed_followup(follow_up, error)
                
                logger.error(f"Follow-up {follow_up.id} permanently failed after {max_retries} attempts")
                return
            
            # Schedule retry
            retry_delay = retry_delays[attempt_count] if attempt_count < len(retry_delays) else 24
            retry_time = datetime.utcnow() + timedelta(hours=retry_delay)
            
            # Create retry follow-up
            retry_follow_up = FollowUpLog(
                ticket_id=follow_up.ticket_id,
                scheduled_time=retry_time,
                status="scheduled",
                follow_up_type="retry",
                channel=follow_up.channel,
                user_phone=follow_up.user_phone,
                user_email=follow_up.user_email,
                brand_id=follow_up.brand_id,
                parent_follow_up_id=follow_up.id,
                retry_count=attempt_count + 1
            )
            
            self.db.add(retry_follow_up)
            self.db.commit()
            
            # Schedule retry task
            self._schedule_celery_task(retry_follow_up.id, retry_time)
            
            logger.info(f"Scheduled retry {attempt_count + 1} for follow-up {follow_up.id} in {retry_delay} hours")
            
        except Exception as e:
            logger.error(f"Error handling delivery failure: {e}")
    
    def _notify_brand_of_failed_followup(self, follow_up: FollowUpLog, error: str):
        """
        Notify brand about failed follow-up attempts
        """
        try:
            # Get brand details
            brand = self.db.query(Brand).filter(Brand.id == follow_up.brand_id).first()
            if not brand or not brand.support_email:
                return
            
            # Send notification email
            subject = f"Follow-up Failed - Ticket #{follow_up.ticket_id}"
            message = f"""
            A follow-up attempt for ticket #{follow_up.ticket_id} has failed after multiple retries.
            
            Error: {error}
            Channel: {follow_up.channel}
            User: {follow_up.user_phone or follow_up.user_email}
            
            Please review this ticket manually and contact the customer if necessary.
            
            Ticket details: {settings.FRONTEND_URL}/brand/tickets/{follow_up.ticket_id}
            """
            
            # Send email notification
            self._send_email_notification(brand.support_email, subject, message)
            
            logger.info(f"Sent failure notification to brand {follow_up.brand_id}")
            
        except Exception as e:
            logger.error(f"Error notifying brand of failed follow-up: {e}")
    
    def _send_email_notification(self, to_email: str, subject: str, message: str):
        """
        Send email notification
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = settings.FROM_EMAIL
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}") 