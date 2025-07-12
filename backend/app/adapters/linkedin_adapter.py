# backend/app/adapters/linkedin_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List, Union
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class LinkedInAdapter:
    def __init__(self):
        self.access_token = getattr(settings, 'LINKEDIN_ACCESS_TOKEN', '')
        self.api_base_url = "https://api.linkedin.com/v2"
        self.ai_engine = AIEngine()
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming LinkedIn Messaging webhook
        """
        try:
            # Handle webhook verification (if any)
            if 'eventType' in request_data and request_data['eventType'] == 'verification':
                return self._handle_webhook_verification(request_data)
            
            # Handle incoming messages
            if 'eventType' in request_data and request_data['eventType'] == 'message':
                return self._handle_messages(request_data, conversation_manager, db_session, brand_id)
            
            return {"status": "ok"}
            
        except Exception as e:
            logger.error(f"Error handling LinkedIn webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_message(self, recipient_urn: str, message: str) -> bool:
        """
        Send a text message to a LinkedIn user
        """
        try:
            url = f"{self.api_base_url}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipients": [recipient_urn],
                "subject": "",
                "body": message
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload
            )
            
            if response.status_code in (200, 201):
                logger.info(f"LinkedIn message sent successfully to {recipient_urn}")
                return True
            else:
                logger.error(f"Error sending LinkedIn message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending LinkedIn message: {e}")
            return False
    
    def _handle_webhook_verification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook verification (if required)"""
        # LinkedIn may not require explicit webhook verification
        return {"status": "ok"}
    
    def _handle_messages(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                        db_session, brand_id: int) -> Dict[str, Any]:
        """Handle incoming LinkedIn messages"""
        try:
            sender_urn = request_data.get('from', '')
            message_data = request_data.get('message', {})
            user_message = message_data.get('text', '')
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=sender_urn,
                user_message=user_message,
                brand_id=brand_id,
                channel="linkedin"
            )
            
            # Send response
            success = self.send_message(sender_urn, bot_response)
            
            return {
                "status": "ok",
                "sender_urn": sender_urn,
                "user_message": user_message,
                "bot_response": bot_response,
                "sent": success
            }
            
        except Exception as e:
            logger.error(f"Error handling LinkedIn messages: {e}")
            return {"status": "error", "message": str(e)} 