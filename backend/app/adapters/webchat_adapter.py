# backend/app/adapters/webchat_adapter.py

import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

class WebChatAdapter:
    def __init__(self):
        self.ai_engine = AIEngine()
        # Store active chat sessions (in production, use Redis or database)
        self.active_sessions = {}
    
    def handle_webhook(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                      db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming webchat message
        """
        try:
            session_id = request_data.get('session_id')
            user_message = request_data.get('message', '')
            user_id = request_data.get('user_id')
            user_name = request_data.get('user_name', 'Anonymous')
            file_upload = request_data.get('file_upload')
            
            if not session_id:
                session_id = str(uuid.uuid4())
            
            if not user_message.strip() and not file_upload:
                return {
                    "status": "error",
                    "message": "No message or file provided",
                    "session_id": session_id
                }
            
            # Handle file uploads
            if file_upload:
                user_message = self._process_file_upload(file_upload, user_message)
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=user_message,
                brand_id=brand_id,
                channel="webchat"
            )
            
            # Store session info
            self._update_session(session_id, user_id, user_name, brand_id)
            
            return {
                "status": "success",
                "session_id": session_id,
                "reply": bot_response,
                "timestamp": datetime.utcnow().isoformat(),
                "user_info": {
                    "id": user_id,
                    "name": user_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling webchat: {e}")
            return {
                "status": "error",
                "message": "Sorry, I encountered an error. Please try again.",
                "session_id": session_id if 'session_id' in locals() else None
            }
    
    def create_chat_session(self, user_id: Optional[str] = None, user_name: str = "Anonymous", 
                           brand_id: int = 1) -> Dict[str, Any]:
        """
        Create a new chat session
        """
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "user_name": user_name,
                "brand_id": brand_id,
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "message_count": 0,
                "status": "active"
            }
            
            self.active_sessions[session_id] = session_data
            
            return {
                "status": "success",
                "session": session_data
            }
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            return {
                "status": "error",
                "message": "Failed to create chat session"
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        Get information about a chat session
        """
        try:
            session_data = self.active_sessions.get(session_id)
            
            if not session_data:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
            
            return {
                "status": "success",
                "session": session_data
            }
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {
                "status": "error",
                "message": "Failed to get session info"
            }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End a chat session
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["status"] = "ended"
                self.active_sessions[session_id]["ended_at"] = datetime.utcnow().isoformat()
                
                return {
                    "status": "success",
                    "message": "Session ended successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {
                "status": "error",
                "message": "Failed to end session"
            }
    
    def send_typing_indicator(self, session_id: str, is_typing: bool = True) -> Dict[str, Any]:
        """
        Send typing indicator for a session
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["is_typing"] = is_typing
                self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
                
                return {
                    "status": "success",
                    "typing": is_typing
                }
            else:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
                
        except Exception as e:
            logger.error(f"Error sending typing indicator: {e}")
            return {
                "status": "error",
                "message": "Failed to send typing indicator"
            }
    
    def get_active_sessions(self, brand_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get all active chat sessions
        """
        try:
            sessions = []
            
            for session_id, session_data in self.active_sessions.items():
                if session_data["status"] == "active":
                    if brand_id is None or session_data["brand_id"] == brand_id:
                        sessions.append(session_data)
            
            return {
                "status": "success",
                "sessions": sessions,
                "count": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return {
                "status": "error",
                "message": "Failed to get active sessions"
            }
    
    def send_system_message(self, session_id: str, message: str, message_type: str = "info") -> Dict[str, Any]:
        """
        Send a system message to a chat session
        """
        try:
            if session_id in self.active_sessions:
                system_message = {
                    "type": "system",
                    "message_type": message_type,
                    "content": message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "session_id": session_id
                }
                
                # In a real implementation, this would be sent via WebSocket
                # For now, we'll just return the message structure
                return {
                    "status": "success",
                    "message": system_message
                }
            else:
                return {
                    "status": "error",
                    "message": "Session not found"
                }
                
        except Exception as e:
            logger.error(f"Error sending system message: {e}")
            return {
                "status": "error",
                "message": "Failed to send system message"
            }
    
    def create_quick_replies(self, options: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Create quick reply buttons for webchat
        """
        try:
            quick_replies = []
            
            for option in options:
                quick_reply = {
                    "type": "quick_reply",
                    "title": option.get("title", ""),
                    "payload": option.get("payload", ""),
                    "action": option.get("action", "send")
                }
                quick_replies.append(quick_reply)
            
            return quick_replies
            
        except Exception as e:
            logger.error(f"Error creating quick replies: {e}")
            return []
    
    def create_carousel(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a carousel/multi-card message
        """
        try:
            carousel = {
                "type": "carousel",
                "items": []
            }
            
            for item in items:
                carousel_item = {
                    "title": item.get("title", ""),
                    "subtitle": item.get("subtitle", ""),
                    "image_url": item.get("image_url"),
                    "buttons": item.get("buttons", [])
                }
                carousel["items"].append(carousel_item)
            
            return carousel
            
        except Exception as e:
            logger.error(f"Error creating carousel: {e}")
            return {"type": "carousel", "items": []}
    
    def _process_file_upload(self, file_upload: Dict[str, Any], user_message: str) -> str:
        """
        Process file upload and return enhanced message
        """
        try:
            file_name = file_upload.get("name", "Unknown file")
            file_type = file_upload.get("type", "unknown")
            file_size = file_upload.get("size", 0)
            file_url = file_upload.get("url", "")
            
            # Determine file category
            if file_type.startswith("image/"):
                file_category = "image"
            elif file_type.startswith("video/"):
                file_category = "video"
            elif file_type.startswith("audio/"):
                file_category = "audio"
            elif file_type in ["application/pdf", "text/plain", "application/msword"]:
                file_category = "document"
            else:
                file_category = "file"
            
            # Create enhanced message
            enhanced_message = f"[{file_category.title()}: {file_name}]"
            if user_message:
                enhanced_message += f" {user_message}"
            
            return enhanced_message
            
        except Exception as e:
            logger.error(f"Error processing file upload: {e}")
            return user_message or "[File upload]"
    
    def _update_session(self, session_id: str, user_id: Optional[str], user_name: str, brand_id: int):
        """
        Update session information
        """
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
                self.active_sessions[session_id]["message_count"] += 1
            else:
                self.active_sessions[session_id] = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "user_name": user_name,
                    "brand_id": brand_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "last_activity": datetime.utcnow().isoformat(),
                    "message_count": 1,
                    "status": "active"
                }
                
        except Exception as e:
            logger.error(f"Error updating session: {e}")

# Legacy function for backward compatibility
def handle_webchat(request_data):
    adapter = WebChatAdapter()
    return adapter.handle_webhook(request_data, None, None, 1)
