# backend/app/adapters/telegram_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List, Union
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.config.settings import settings

logger = logging.getLogger(__name__)

class TelegramAdapter:
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.ai_engine = AIEngine()
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming Telegram webhook
        """
        try:
            # Extract message data from Telegram webhook
            if 'message' not in request_data:
                return {"ok": False, "error": "No message in webhook"}
            
            message = request_data['message']
            chat_id = message.get('chat', {}).get('id')
            user_id = message.get('from', {}).get('id')
            username = message.get('from', {}).get('username', '')
            first_name = message.get('from', {}).get('first_name', '')
            
            # Handle different message types
            if 'text' in message:
                user_message = message['text']
                message_type = 'text'
            elif 'voice' in message:
                user_message = f"[Voice message] {message.get('caption', '')}"
                message_type = 'voice'
                # Download voice file if needed
                voice_info = self._process_voice(message['voice'])
                user_message += f" [Duration: {voice_info.get('duration', 0)}s]"
            elif 'photo' in message:
                user_message = f"[Photo] {message.get('caption', '')}"
                message_type = 'photo'
            elif 'document' in message:
                user_message = f"[Document: {message['document'].get('file_name', 'Unknown')}] {message.get('caption', '')}"
                message_type = 'document'
            elif 'audio' in message:
                user_message = f"[Audio: {message['audio'].get('title', 'Unknown')}] {message.get('caption', '')}"
                message_type = 'audio'
            else:
                user_message = "[Unsupported message type]"
                message_type = 'unknown'
            
            if not user_message.strip():
                return self._send_message(chat_id, "I didn't receive any message. Please try again.")
            
            # Create session ID from user info
            session_id = f"telegram_{user_id}_{chat_id}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=user_message,
                brand_id=brand_id,
                channel="telegram"
            )
            
            # Send response back to user
            return self._send_message(chat_id, bot_response)
            
        except Exception as e:
            logger.error(f"Error handling Telegram webhook: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_message(self, chat_id: Union[int, str], text: str, 
                    reply_markup: Optional[Dict] = None, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Send a message to a Telegram chat
        """
        try:
            url = f"{self.api_base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_photo(self, chat_id: Union[int, str], photo: str, 
                  caption: Optional[str] = None, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a photo to a Telegram chat
        """
        try:
            url = f"{self.api_base_url}/sendPhoto"
            payload = {
                "chat_id": chat_id,
                "photo": photo
            }
            
            if caption:
                payload["caption"] = caption
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_document(self, chat_id: Union[int, str], document: str, 
                     caption: Optional[str] = None, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a document to a Telegram chat
        """
        try:
            url = f"{self.api_base_url}/sendDocument"
            payload = {
                "chat_id": chat_id,
                "document": document
            }
            
            if caption:
                payload["caption"] = caption
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending Telegram document: {e}")
            return {"ok": False, "error": str(e)}
    
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> Dict[str, Any]:
        """
        Create an inline keyboard markup
        """
        return {
            "inline_keyboard": buttons
        }
    
    def create_reply_keyboard(self, buttons: List[List[str]], 
                            resize_keyboard: bool = True, 
                            one_time_keyboard: bool = False) -> Dict[str, Any]:
        """
        Create a reply keyboard markup
        """
        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button_text in row:
                keyboard_row.append({"text": button_text})
            keyboard.append(keyboard_row)
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard
        }
    
    def create_quick_replies(self, message: str, options: List[str]) -> Dict[str, Any]:
        """
        Create quick reply buttons for Telegram
        """
        keyboard = []
        for option in options:
            keyboard.append([{"text": option}])
        
        reply_markup = {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        
        return reply_markup
    
    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None, 
                            show_alert: bool = False) -> Dict[str, Any]:
        """
        Answer a callback query
        """
        try:
            url = f"{self.api_base_url}/answerCallbackQuery"
            payload = {
                "callback_query_id": callback_query_id,
                "show_alert": show_alert
            }
            
            if text:
                payload["text"] = text
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            return {"ok": False, "error": str(e)}
    
    def edit_message_text(self, chat_id: Union[int, str], message_id: int, text: str,
                         reply_markup: Optional[Dict] = None, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Edit an existing message
        """
        try:
            url = f"{self.api_base_url}/editMessageText"
            payload = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return {"ok": False, "error": str(e)}
    
    def delete_message(self, chat_id: Union[int, str], message_id: int) -> Dict[str, Any]:
        """
        Delete a message
        """
        try:
            url = f"{self.api_base_url}/deleteMessage"
            payload = {
                "chat_id": chat_id,
                "message_id": message_id
            }
            
            response = requests.post(url, json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return {"ok": False, "error": str(e)}
    
    def _send_message(self, chat_id: Union[int, str], text: str) -> Dict[str, Any]:
        """
        Internal method to send message
        """
        return self.send_message(chat_id, text)
    
    def _process_voice(self, voice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process voice message data
        """
        try:
            file_id = voice_data.get('file_id')
            duration = voice_data.get('duration', 0)
            file_size = voice_data.get('file_size')
            
            # Get file info
            if file_id:
                file_info = self._get_file(file_id)
                return {
                    'file_id': file_id,
                    'duration': duration,
                    'file_size': file_size,
                    'file_path': file_info.get('file_path')
                }
        except Exception as e:
            logger.error(f"Error processing voice: {e}")
        
        return {'duration': 0}
    
    def _get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get file information from Telegram
        """
        try:
            url = f"{self.api_base_url}/getFile"
            payload = {"file_id": file_id}
            
            response = requests.post(url, json=payload)
            return response.json().get('result', {})
            
        except Exception as e:
            logger.error(f"Error getting file: {e}")
            return {}

# Legacy function for backward compatibility
def handle_telegram(request_data):
    adapter = TelegramAdapter()
    return adapter.handle_webhook(request_data, None, None, 1)
