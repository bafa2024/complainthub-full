# backend/app/adapters/facebook_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List, Union
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class FacebookMessengerAdapter:
    def __init__(self):
        self.page_access_token = getattr(settings, 'FACEBOOK_PAGE_ACCESS_TOKEN', '')
        self.verify_token = getattr(settings, 'FACEBOOK_VERIFY_TOKEN', '')
        self.api_base_url = "https://graph.facebook.com/v18.0"
        self.ai_engine = AIEngine()
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming Facebook Messenger webhook
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
            logger.error(f"Error handling Facebook webhook: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_message(self, recipient_id: str, message: str, 
                    quick_replies: Optional[List[Dict]] = None) -> bool:
        """
        Send a text message to a Facebook user
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
                params={"access_token": self.page_access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Facebook message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Facebook message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Facebook message: {e}")
            return False
    
    def send_template_message(self, recipient_id: str, template_name: str, 
                            elements: List[Dict], buttons: Optional[List[Dict]] = None) -> bool:
        """
        Send a template message (generic template)
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
                        "type": "template",
                        "payload": {
                            "template_type": "generic",
                            "elements": elements
                        }
                    }
                }
            }
            
            if buttons:
                payload["message"]["attachment"]["payload"]["buttons"] = buttons
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.page_access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Facebook template message sent to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Facebook template: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Facebook template: {e}")
            return False
    
    def send_button_message(self, recipient_id: str, text: str, buttons: List[Dict]) -> bool:
        """
        Send a message with buttons
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
                        "type": "template",
                        "payload": {
                            "template_type": "button",
                            "text": text,
                            "buttons": buttons
                        }
                    }
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.page_access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Facebook button message sent to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Facebook button message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Facebook button message: {e}")
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
                params={"access_token": self.page_access_token},
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Facebook {media_type} message sent to {recipient_id}")
                return True
            else:
                logger.error(f"Error sending Facebook {media_type} message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Facebook {media_type} message: {e}")
            return False
    
    def send_typing_indicator(self, recipient_id: str, typing: bool = True) -> bool:
        """
        Send typing indicator
        """
        try:
            url = f"{self.api_base_url}/me/messages"
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipient": {"id": recipient_id},
                "sender_action": "typing_on" if typing else "typing_off"
            }
            
            response = requests.post(
                url,
                headers=headers,
                params={"access_token": self.page_access_token},
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error sending typing indicator: {e}")
            return False
    
    def create_quick_reply(self, content_type: str, title: str, payload: str, 
                          image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a quick reply button
        """
        quick_reply = {
            "content_type": content_type,
            "title": title,
            "payload": payload
        }
        
        if image_url:
            quick_reply["image_url"] = image_url
        
        return quick_reply
    
    def create_url_button(self, title: str, url: str, webview_height_ratio: str = "full") -> Dict[str, Any]:
        """
        Create a URL button
        """
        return {
            "type": "web_url",
            "title": title,
            "url": url,
            "webview_height_ratio": webview_height_ratio
        }
    
    def create_postback_button(self, title: str, payload: str) -> Dict[str, Any]:
        """
        Create a postback button
        """
        return {
            "type": "postback",
            "title": title,
            "payload": payload
        }
    
    def create_phone_button(self, title: str, phone_number: str) -> Dict[str, Any]:
        """
        Create a phone number button
        """
        return {
            "type": "phone_number",
            "title": title,
            "payload": phone_number
        }
    
    def _handle_webhook_verification(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook verification from Facebook
        """
        try:
            mode = request_data.get('hub.mode')
            token = request_data.get('hub.verify_token')
            challenge = request_data.get('hub.challenge')
            
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("Facebook webhook verified successfully")
                return {"status": "ok", "challenge": challenge}
            else:
                logger.error("Facebook webhook verification failed")
                return {"status": "error", "message": "Verification failed"}
                
        except Exception as e:
            logger.error(f"Error in webhook verification: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_messages(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                        db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming messages from Facebook
        """
        try:
            entries = request_data.get('entry', [])
            
            for entry in entries:
                messaging_events = entry.get('messaging', [])
                
                for event in messaging_events:
                    sender_id = event.get('sender', {}).get('id')
                    recipient_id = event.get('recipient', {}).get('id')
                    
                    # Handle different types of messages
                    if 'message' in event:
                        message_data = event['message']
                        message_type = message_data.get('type', 'text')
                        
                        if message_type == 'text':
                            user_message = message_data.get('text', '')
                        elif message_type == 'image':
                            user_message = f"[Image] {message_data.get('caption', '')}"
                        elif message_type == 'video':
                            user_message = f"[Video] {message_data.get('caption', '')}"
                        elif message_type == 'audio':
                            user_message = "[Audio message]"
                        elif message_type == 'file':
                            user_message = f"[File: {message_data.get('filename', 'Unknown')}]"
                        else:
                            user_message = f"[{message_type.title()} message]"
                        
                        # Process message through conversation manager
                        session_id = f"facebook_{sender_id}"
                        
                        bot_response = conversation_manager.process_message(
                            session_id=session_id,
                            user_message=user_message,
                            brand_id=brand_id,
                            channel="facebook"
                        )
                        
                        # Send response back to user
                        self.send_message(sender_id, bot_response)
                    
                    elif 'postback' in event:
                        # Handle postback from buttons
                        postback_data = event['postback']
                        payload = postback_data.get('payload', '')
                        title = postback_data.get('title', '')
                        
                        # Process postback as a message
                        session_id = f"facebook_{sender_id}"
                        user_message = f"[Button: {title}] {payload}"
                        
                        bot_response = conversation_manager.process_message(
                            session_id=session_id,
                            user_message=user_message,
                            brand_id=brand_id,
                            channel="facebook"
                        )
                        
                        self.send_message(sender_id, bot_response)
                    
                    elif 'quick_reply' in event:
                        # Handle quick reply
                        quick_reply_data = event['quick_reply']
                        payload = quick_reply_data.get('payload', '')
                        
                        session_id = f"facebook_{sender_id}"
                        user_message = f"[Quick Reply] {payload}"
                        
                        bot_response = conversation_manager.process_message(
                            session_id=session_id,
                            user_message=user_message,
                            brand_id=brand_id,
                            channel="facebook"
                        )
                        
                        self.send_message(sender_id, bot_response)
            
            return {"status": "ok"}
            
        except Exception as e:
            logger.error(f"Error handling Facebook messages: {e}")
            return {"status": "error", "message": str(e)}

# Legacy function for backward compatibility
def handle_facebook(request_data):
    adapter = FacebookMessengerAdapter()
    return adapter.handle_webhook(request_data, None, None, 1) 