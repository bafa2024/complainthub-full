# backend/app/adapters/instagram_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List, Union
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class InstagramAdapter:
    def __init__(self):
        self.access_token = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', '')
        self.verify_token = getattr(settings, 'INSTAGRAM_VERIFY_TOKEN', '')
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.ai_engine = AIEngine()
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming Instagram Direct Message webhook
        """
        try:
            # Handle webhook verification
            if 'hub.mode' in request_data and request_data['hub.mode'] == 'subscribe':
                return self._handle_webhook_verification(request_data)
            
            # Handle incoming messages
            if 'entry' in request_data:
                return self._handle_messages(request_data, conversation_manager, db_session, brand_id)
            
            return {"status": "ok"}
            
        except Exception as e:
            logger.error(f"Error handling Instagram webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_message(self, recipient_id: str, message: str, 
                    quick_replies: Optional[List[Dict]] = None) -> bool:
        """
        Send a text message to an Instagram user
        """
        try:
            url = f"{self.api_base_url}/me/messages"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message}
            }
            
            if quick_replies:
                payload["message"]["quick_replies"] = quick_replies
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Instagram message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Instagram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Instagram message: {e}")
            return False
    
    def send_media_message(self, recipient_id: str, media_type: str, 
                          media_url: str, caption: Optional[str] = None) -> bool:
        """
        Send a media message (image, video, audio, file)
        """
        try:
            url = f"{self.api_base_url}/me/messages"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "attachment": {
                        "type": media_type,
                        "payload": {
                            "url": media_url
                        }
                    }
                }
            }
            
            if caption:
                payload["message"]["attachment"]["payload"]["caption"] = caption
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Instagram {media_type} message sent to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Instagram {media_type} message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Instagram {media_type} message: {e}")
            return False
    
    def send_quick_replies(self, recipient_id: str, message: str, 
                          quick_replies: List[Dict]) -> bool:
        """
        Send a message with quick reply buttons
        """
        try:
            url = f"{self.api_base_url}/me/messages"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "text": message,
                    "quick_replies": quick_replies
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Instagram quick replies sent to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Instagram quick replies: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Instagram quick replies: {e}")
            return False
    
    def _handle_webhook_verification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook verification"""
        try:
            mode = request_data.get('hub.mode')
            token = request_data.get('hub.verify_token')
            challenge = request_data.get('hub.challenge')
            
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("Instagram webhook verified successfully")
                return {"status": "ok", "challenge": challenge}
            else:
                logger.error("Instagram webhook verification failed")
                return {"status": "error", "message": "Verification failed"}
                
        except Exception as e:
            logger.error(f"Error in Instagram webhook verification: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_messages(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                        db_session, brand_id: int) -> Dict[str, Any]:
        """Handle incoming Instagram messages"""
        try:
            responses = []
            
            for entry in request_data['entry']:
                for messaging in entry.get('messaging', []):
                    sender_id = messaging['sender']['id']
                    message_data = messaging.get('message', {})
                    
                    if 'text' in message_data:
                        user_message = message_data['text']
                        message_type = 'text'
                    elif 'attachments' in message_data:
                        attachment = message_data['attachments'][0]
                        user_message = f"[{attachment['type'].title()}] {attachment.get('title', '')}"
                        message_type = 'media'
                    else:
                        continue
                    
                    # Process message through conversation manager
                    bot_response = conversation_manager.process_message(
                        session_id=sender_id,
                        user_message=user_message,
                        brand_id=brand_id,
                        channel="instagram"
                    )
                    
                    # Send response
                    success = self.send_message(sender_id, bot_response)
                    
                    responses.append({
                        "sender_id": sender_id,
                        "user_message": user_message,
                        "bot_response": bot_response,
                        "sent": success
                    })
            
            return {
                "status": "ok",
                "processed_messages": len(responses),
                "responses": responses
            }
            
        except Exception as e:
            logger.error(f"Error handling Instagram messages: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user profile information
        """
        try:
            url = f"{self.api_base_url}/{user_id}"
            params = {
                "fields": "id,username,profile_picture_url",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error getting Instagram user profile: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Instagram user profile: {e}")
            return None 