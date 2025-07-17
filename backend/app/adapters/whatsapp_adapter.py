# backend/app/adapters/whatsapp_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppAdapter:
    def __init__(self):
        self.twilio_client = None
        self.ai_engine = AIEngine()
        
        # Initialize Twilio client if credentials are available
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and hasattr(settings, 'TWILIO_AUTH_TOKEN'):
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> str:
        """
        Handle incoming WhatsApp webhook from Twilio or Meta API
        """
        try:
            # Extract message data based on source
            if 'Body' in request_data:  # Twilio format
                session_id = request_data.get('From', '')
                user_message = request_data.get('Body', '')
                media_url = request_data.get('MediaUrl0')
                message_type = 'text'
                
                if media_url:
                    message_type = 'media'
                    # Download and process media if needed
                    media_info = self._process_media(media_url)
                    user_message = f"[Media: {media_info.get('type', 'unknown')}] {user_message}"
                
            elif 'entry' in request_data:  # Meta API format
                entry = request_data['entry'][0]
                changes = entry.get('changes', [])
                
                if changes and changes[0].get('value', {}).get('messages'):
                    message_data = changes[0]['value']['messages'][0]
                    session_id = message_data.get('from', '')
                    user_message = message_data.get('text', {}).get('body', '')
                    message_type = 'text'
                    
                    # Handle media messages
                    if 'image' in message_data:
                        user_message = f"[Image] {user_message}"
                        message_type = 'media'
                    elif 'audio' in message_data:
                        user_message = f"[Audio] {user_message}"
                        message_type = 'media'
                    elif 'document' in message_data:
                        user_message = f"[Document] {user_message}"
                        message_type = 'media'
            else:
                raise ValueError("Unsupported webhook format")
            
            if not user_message.strip():
                return self._generate_response("I didn't receive any message. Please try again.")
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=user_message,
                brand_id=brand_id,
                channel="whatsapp"
            )
            
            return self._generate_response(bot_response)
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp webhook: {e}")
            return self._generate_response("Sorry, I encountered an error. Please try again later.")
    
    def send_message(self, to_number: str, message: str, media_url: Optional[str] = None) -> bool:
        """
        Send a WhatsApp message using Twilio
        """
        try:
            if not self.twilio_client:
                logger.error("Twilio client not initialized")
                return False
            
            # Format phone number for WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            if media_url:
                # Send media message
                message_obj = self.twilio_client.messages.create(
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    body=message,
                    media_url=[media_url],
                    to=to_number
                )
            else:
                # Send text message
                message_obj = self.twilio_client.messages.create(
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    body=message,
                    to=to_number
                )
            
            logger.info(f"WhatsApp message sent successfully: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def send_template_message(self, to_number: str, template_name: str, 
                            language_code: str = "en", components: Optional[List[Dict]] = None) -> bool:
        """
        Send a WhatsApp template message
        """
        try:
            if not self.twilio_client:
                logger.error("Twilio client not initialized")
                return False
            
            # Format phone number
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            # Create template message
            message_obj = self.twilio_client.messages.create(
                from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                to=to_number,
                content_sid=f"HX{template_name}_{language_code}"  # Template SID format
            )
            
            logger.info(f"WhatsApp template message sent: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp template: {e}")
            return False
    
    def _generate_response(self, message: str) -> str:
        """
        Generate TwiML response for WhatsApp
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def _process_media(self, media_url: str) -> Dict[str, Any]:
        """
        Process media files from WhatsApp
        """
        try:
            # Download media file
            response = requests.get(media_url)
            if response.status_code == 200:
                # Determine media type from URL or content
                content_type = response.headers.get('content-type', '')
                
                if 'image' in content_type:
                    media_type = 'image'
                elif 'audio' in content_type:
                    media_type = 'audio'
                elif 'video' in content_type:
                    media_type = 'video'
                elif 'pdf' in content_type or 'document' in content_type:
                    media_type = 'document'
                else:
                    media_type = 'unknown'
                
                return {
                    'type': media_type,
                    'url': media_url,
                    'content_type': content_type,
                    'size': len(response.content)
                }
        except Exception as e:
            logger.error(f"Error processing media: {e}")
        
        return {'type': 'unknown', 'url': media_url}
    
    def create_quick_replies(self, message: str, options: List[str]) -> str:
        """
        Create quick reply buttons for WhatsApp
        """
        response = MessagingResponse()
        msg = response.message(message)
        
        for option in options:
            msg.body(option)
        
        return str(response)

# Legacy function for backward compatibility
def handle_whatsapp(request_data):
    adapter = WhatsAppAdapter()
    return adapter.handle_webhook(request_data, None, None, 1)
