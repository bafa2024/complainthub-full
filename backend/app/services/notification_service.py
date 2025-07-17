# backend/app/services/notification_service.py

import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import User, Brand, Ticket, Notification, NotificationTemplate
from app.adapters.twilio_adapter import TwilioAdapter
from app.adapters.whatsapp_adapter import WhatsAppAdapter
from app.adapters.telegram_adapter import TelegramAdapter
from app.services.notifications import send_email
from app.core.ai_engine import AIEngine
from app.config.settings import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Comprehensive Notification Service
    
    Features:
    - Multi-channel notifications (Email, SMS, WhatsApp, Telegram, In-app)
    - Template-based messaging
    - Scheduled notifications
    - Alert management
    - Notification preferences
    - Delivery tracking
    - Retry mechanism
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.twilio_adapter = TwilioAdapter()
        self.whatsapp_adapter = WhatsAppAdapter()
        self.telegram_adapter = TelegramAdapter()
        self.ai_engine = AIEngine()
        
        # Notification channels
        self.channels = {
            'email': self._send_email_notification,
            'sms': self._send_sms_notification,
            'whatsapp': self._send_whatsapp_notification,
            'telegram': self._send_telegram_notification,
            'in_app': self._send_in_app_notification
        }
    
    def send_notification(
        self,
        user_id: int,
        notification_type: str,
        data: Dict[str, Any],
        channels: List[str] = None,
        priority: str = 'normal',
        scheduled_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Send notification to user through specified channels
        """
        try:
            # Get user and their notification preferences
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get notification template
            template = self._get_notification_template(notification_type)
            if not template:
                return {"success": False, "error": f"Template not found for type: {notification_type}"}
            
            # Determine channels to use
            if not channels:
                channels = self._get_user_preferred_channels(user, notification_type)
            
            # Create notification record
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=template.title,
                message=self._render_template(template.message, data),
                data=data,
                channels=channels,
                priority=priority,
                scheduled_at=scheduled_at,
                status='pending'
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            # Send immediately if not scheduled
            if not scheduled_at:
                return self._send_notification_immediately(notification, user)
            else:
                return {
                    "success": True,
                    "notification_id": notification.id,
                    "scheduled_at": scheduled_at.isoformat(),
                    "message": "Notification scheduled successfully"
                }
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def send_brand_notification(
        self,
        brand_id: int,
        notification_type: str,
        data: Dict[str, Any],
        channels: List[str] = None,
        priority: str = 'normal'
    ) -> Dict[str, Any]:
        """
        Send notification to all brand users
        """
        try:
            # Get all brand users
            brand_users = self.db.query(User).filter(
                and_(
                    User.brand_id == brand_id,
                    User.role == 'brand_user',
                    User.is_active == True
                )
            ).all()
            
            results = []
            for user in brand_users:
                result = self.send_notification(
                    user_id=user.id,
                    notification_type=notification_type,
                    data=data,
                    channels=channels,
                    priority=priority
                )
                results.append(result)
            
            success_count = sum(1 for r in results if r.get('success'))
            
            return {
                "success": success_count > 0,
                "total_users": len(brand_users),
                "successful_sends": success_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending brand notification: {e}")
            return {"success": False, "error": str(e)}
    
    def send_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = 'medium',
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send system-wide alert to administrators
        """
        try:
            # Get all admin users
            admin_users = self.db.query(User).filter(
                and_(
                    User.role == 'admin',
                    User.is_active == True
                )
            ).all()
            
            results = []
            for admin in admin_users:
                result = self.send_notification(
                    user_id=admin.id,
                    notification_type='system_alert',
                    data={
                        'alert_type': alert_type,
                        'message': message,
                        'severity': severity,
                        **data or {}
                    },
                    channels=['email', 'in_app'],
                    priority='high'
                )
                results.append(result)
            
            return {
                "success": True,
                "alert_type": alert_type,
                "severity": severity,
                "admin_count": len(admin_users),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending system alert: {e}")
            return {"success": False, "error": str(e)}
    
    def send_low_balance_alert(self, brand_id: int) -> Dict[str, Any]:
        """
        Send low balance alert to brand
        """
        try:
            brand = self.db.query(Brand).filter(Brand.id == brand_id).first()
            if not brand:
                return {"success": False, "error": "Brand not found"}
            
            return self.send_brand_notification(
                brand_id=brand_id,
                notification_type='low_balance',
                data={
                    'brand_name': brand.name,
                    'current_balance': brand.credit_balance,
                    'threshold': settings.LOW_BALANCE_THRESHOLD
                },
                channels=['email', 'sms'],
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Error sending low balance alert: {e}")
            return {"success": False, "error": str(e)}
    
    def send_ticket_alert(
        self,
        ticket_id: int,
        alert_type: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send ticket-related alerts
        """
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            # Get brand users for this ticket
            brand_users = self.db.query(User).filter(
                and_(
                    User.brand_id == ticket.brand_id,
                    User.role == 'brand_user',
                    User.is_active == True
                )
            ).all()
            
            results = []
            for user in brand_users:
                result = self.send_notification(
                    user_id=user.id,
                    notification_type=f'ticket_{alert_type}',
                    data={
                        'ticket_id': ticket.id,
                        'ticket_title': ticket.title,
                        'ticket_status': ticket.status,
                        'customer_name': ticket.owner.full_name if ticket.owner else 'Anonymous',
                        **data or {}
                    },
                    channels=['email', 'in_app'],
                    priority='medium'
                )
                results.append(result)
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "alert_type": alert_type,
                "brand_users_notified": len(brand_users),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error sending ticket alert: {e}")
            return {"success": False, "error": str(e)}
    
    def send_escalation_notification(self, ticket_id: int) -> Dict[str, Any]:
        """
        Send escalation notification to administrators
        """
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            return self.send_system_alert(
                alert_type='ticket_escalation',
                message=f'Ticket #{ticket.id} has been escalated',
                severity='high',
                data={
                    'ticket_id': ticket.id,
                    'ticket_title': ticket.title,
                    'brand_name': ticket.brand.name if ticket.brand else 'Unknown',
                    'escalation_reason': 'Manual escalation by brand user'
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending escalation notification: {e}")
            return {"success": False, "error": str(e)}
    
    def send_abuse_alert(
        self,
        ticket_id: int,
        abuse_level: int,
        toxicity_score: float
    ) -> Dict[str, Any]:
        """
        Send abuse detection alert
        """
        try:
            ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if not ticket:
                return {"success": False, "error": "Ticket not found"}
            
            severity = 'high' if abuse_level >= 4 else 'medium'
            
            return self.send_system_alert(
                alert_type='abuse_detection',
                message=f'Abuse detected in ticket #{ticket.id}',
                severity=severity,
                data={
                    'ticket_id': ticket.id,
                    'abuse_level': abuse_level,
                    'toxicity_score': toxicity_score,
                    'customer_name': ticket.owner.full_name if ticket.owner else 'Anonymous',
                    'brand_name': ticket.brand.name if ticket.brand else 'Unknown'
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending abuse alert: {e}")
            return {"success": False, "error": str(e)}
    
    def send_performance_alert(
        self,
        alert_type: str,
        metric: str,
        value: float,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Send performance-related alerts
        """
        try:
            return self.send_system_alert(
                alert_type=f'performance_{alert_type}',
                message=f'Performance alert: {metric} = {value} (threshold: {threshold})',
                severity='medium',
                data={
                    'metric': metric,
                    'value': value,
                    'threshold': threshold,
                    'alert_type': alert_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error sending performance alert: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get notifications for a user
        """
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.read_at.is_(None))
            
            notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
            
            return {
                "success": True,
                "notifications": [
                    {
                        "id": n.id,
                        "type": n.type,
                        "title": n.title,
                        "message": n.message,
                        "data": n.data,
                        "priority": n.priority,
                        "status": n.status,
                        "created_at": n.created_at.isoformat(),
                        "read_at": n.read_at.isoformat() if n.read_at else None
                    }
                    for n in notifications
                ],
                "total": len(notifications)
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return {"success": False, "error": str(e)}
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """
        Mark notification as read
        """
        try:
            notification = self.db.query(Notification).filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            ).first()
            
            if not notification:
                return {"success": False, "error": "Notification not found"}
            
            notification.read_at = datetime.utcnow()
            self.db.commit()
            
            return {"success": True, "message": "Notification marked as read"}
            
        except Exception as e:
            logger.error(f"Error marking notification read: {e}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get notification statistics for user
        """
        try:
            total_notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).count()
            
            unread_notifications = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None)
                )
            ).count()
            
            high_priority_unread = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.read_at.is_(None),
                    Notification.priority == 'high'
                )
            ).count()
            
            return {
                "success": True,
                "stats": {
                    "total": total_notifications,
                    "unread": unread_notifications,
                    "high_priority_unread": high_priority_unread,
                    "read_rate": (total_notifications - unread_notifications) / total_notifications if total_notifications > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_notification_immediately(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send notification immediately through all channels
        """
        results = {}
        
        for channel in notification.channels:
            if channel in self.channels:
                try:
                    result = self.channels[channel](notification, user)
                    results[channel] = result
                except Exception as e:
                    logger.error(f"Error sending {channel} notification: {e}")
                    results[channel] = {"success": False, "error": str(e)}
            else:
                results[channel] = {"success": False, "error": f"Channel {channel} not supported"}
        
        # Update notification status
        successful_channels = [ch for ch, res in results.items() if res.get('success')]
        notification.status = 'delivered' if successful_channels else 'failed'
        notification.delivered_at = datetime.utcnow() if successful_channels else None
        notification.delivery_data = results
        
        self.db.commit()
        
        return {
            "success": len(successful_channels) > 0,
            "notification_id": notification.id,
            "results": results,
            "successful_channels": successful_channels
        }
    
    def _send_email_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send email notification
        """
        try:
            subject = notification.title
            html_content = f"""
            <html>
            <body>
                <h2>{notification.title}</h2>
                <p>{notification.message}</p>
                <hr>
                <p><small>Sent at {notification.created_at.strftime('%Y-%m-%d %H:%M:%S')}</small></p>
            </body>
            </html>
            """
            
            success = send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_sms_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send SMS notification
        """
        try:
            if not user.phone:
                return {"success": False, "error": "No phone number available"}
            
            success = self.twilio_adapter.send_sms(
                to_number=user.phone,
                message=notification.message
            )
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_whatsapp_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send WhatsApp notification
        """
        try:
            if not user.phone:
                return {"success": False, "error": "No phone number available"}
            
            success = self.whatsapp_adapter.send_message(
                to_number=user.phone,
                message=notification.message
            )
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp notification: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_telegram_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send Telegram notification
        """
        try:
            if not user.telegram_id:
                return {"success": False, "error": "No Telegram ID available"}
            
            success = self.telegram_adapter.send_message(
                chat_id=user.telegram_id,
                message=notification.message
            )
            
            return {"success": success}
            
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_in_app_notification(self, notification: Notification, user: User) -> Dict[str, Any]:
        """
        Send in-app notification (stored in database)
        """
        try:
            # In-app notifications are already stored in the database
            # This method is called for consistency with other channels
            return {"success": True, "message": "In-app notification stored"}
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_notification_template(self, notification_type: str) -> Optional[NotificationTemplate]:
        """
        Get notification template by type
        """
        return self.db.query(NotificationTemplate).filter(
            NotificationTemplate.type == notification_type
        ).first()
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """
        Render template with data
        """
        try:
            return template.format(**data)
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template
    
    def _get_user_preferred_channels(self, user: User, notification_type: str) -> List[str]:
        """
        Get user's preferred notification channels
        """
        # Default channels based on notification type
        default_channels = {
            'system_alert': ['email', 'in_app'],
            'ticket_new': ['email', 'in_app'],
            'ticket_updated': ['email', 'in_app'],
            'ticket_resolved': ['email', 'in_app'],
            'ticket_escalation': ['email', 'sms', 'in_app'],
            'low_balance': ['email', 'sms'],
            'abuse_detection': ['email', 'in_app'],
            'performance_alert': ['email', 'in_app']
        }
        
        return default_channels.get(notification_type, ['email', 'in_app']) 