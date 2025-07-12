# backend/app/adapters/knowlarity_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.services.speech.tts import TTSService
from app.config.settings import settings

logger = logging.getLogger(__name__)

class KnowlarityAdapter:
    def __init__(self):
        self.api_key = getattr(settings, 'KNOWLARITY_API_KEY', '')
        self.base_url = getattr(settings, 'KNOWLARITY_BASE_URL', 'https://api.knowlarity.com/v1')
        self.ai_engine = AIEngine()
        self.tts_service = TTSService()
        
        if not self.api_key:
            logger.warning("Knowlarity API key not configured")
    
    def handle_voice_call(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                         db_session, brand_id: int) -> str:
        """
        Handle incoming voice call from Knowlarity and generate response
        """
        try:
            # Extract call data from Knowlarity webhook
            from_number = request_data.get('from', '')
            to_number = request_data.get('to', '')
            call_id = request_data.get('call_id', '')
            call_status = request_data.get('status', '')
            recording_url = request_data.get('recording_url', '')
            
            # Create session ID
            session_id = f"knowlarity_voice_{from_number}_{call_id}"
            
            # Handle different call statuses
            if call_status == 'ringing':
                return self._generate_initial_voice_response(session_id, brand_id)
            elif call_status == 'answered':
                return self._handle_answered_call(request_data, conversation_manager, db_session, brand_id)
            elif call_status == 'completed' and recording_url:
                return self._handle_recording_callback(request_data, conversation_manager, db_session, brand_id)
            else:
                return self._generate_error_response("Call status not supported")
                
        except Exception as e:
            logger.error(f"Error handling Knowlarity voice call: {e}")
            return self._generate_error_response("Sorry, I encountered an error. Please try again later.")
    
    def handle_sms(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                   db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming SMS from Knowlarity
        """
        try:
            from_number = request_data.get('from', '')
            to_number = request_data.get('to', '')
            message_body = request_data.get('message', '')
            message_id = request_data.get('message_id', '')
            
            if not message_body.strip():
                return {
                    "success": False,
                    "error": "No message content received"
                }
            
            # Create session ID
            session_id = f"knowlarity_sms_{from_number}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=message_body,
                brand_id=brand_id,
                channel="sms"
            )
            
            # Send response back via Knowlarity SMS API
            success = self.send_sms(from_number, bot_response)
            
            return {
                "success": success,
                "response": bot_response,
                "message_id": message_id
            }
            
        except Exception as e:
            logger.error(f"Error handling Knowlarity SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def make_outbound_call(self, to_number: str, message: str, 
                          voice_id: Optional[str] = None) -> bool:
        """
        Make an outbound voice call using Knowlarity API
        """
        try:
            if not self.api_key:
                logger.error("Knowlarity API key not configured")
                return False
            
            # Generate TTS audio
            audio_url = self.tts_service.generate_speech_url(message, voice_id or "en-US-Standard-A")
            
            # Prepare call data
            call_data = {
                "api_key": self.api_key,
                "to": to_number,
                "from": settings.KNOWLARITY_FROM_NUMBER,
                "answer_url": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/voice",
                "record": True,
                "transcribe": True,
                "transcribe_callback": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/transcribe"
            }
            
            # Make API call to Knowlarity
            response = requests.post(
                f"{self.base_url}/call",
                json=call_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Knowlarity outbound call initiated: {result.get('call_id')}")
                return True
            else:
                logger.error(f"Failed to initiate Knowlarity call: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error making Knowlarity outbound call: {e}")
            return False
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send an SMS message via Knowlarity
        """
        try:
            if not self.api_key:
                logger.error("Knowlarity API key not configured")
                return False
            
            # Prepare SMS data
            sms_data = {
                "api_key": self.api_key,
                "to": to_number,
                "from": settings.KNOWLARITY_FROM_NUMBER,
                "message": message
            }
            
            # Send SMS via Knowlarity API
            response = requests.post(
                f"{self.base_url}/sms",
                json=sms_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Knowlarity SMS sent successfully: {result.get('message_id')}")
                return True
            else:
                logger.error(f"Failed to send Knowlarity SMS: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Knowlarity SMS: {e}")
            return False
    
    def _handle_answered_call(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                             db_session, brand_id: int) -> str:
        """
        Handle answered call and start conversation
        """
        try:
            from_number = request_data.get('from', '')
            call_id = request_data.get('call_id', '')
            session_id = f"knowlarity_voice_{from_number}_{call_id}"
            
            # Generate welcome message
            welcome_message = "Welcome to our complaint management system. Please describe your issue and I'll help you create a ticket."
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(welcome_message, "en-US-Standard-A")
            
            # Return Knowlarity-compatible response
            response = {
                "action": "play",
                "audio_url": audio_url,
                "record": True,
                "transcribe": True,
                "transcribe_callback": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/transcribe",
                "session_id": session_id
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Error handling answered call: {e}")
            return self._generate_error_response("Error processing call")
    
    def _handle_recording_callback(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                                 db_session, brand_id: int) -> str:
        """
        Handle recording callback with transcription
        """
        try:
            recording_url = request_data.get('recording_url', '')
            transcription_text = request_data.get('transcription_text', '')
            from_number = request_data.get('from', '')
            call_id = request_data.get('call_id', '')
            
            if not transcription_text:
                return self._generate_error_response("No transcription available")
            
            # Create session ID
            session_id = f"knowlarity_voice_{from_number}_{call_id}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=transcription_text,
                brand_id=brand_id,
                channel="voice"
            )
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(bot_response, "en-US-Standard-A")
            
            # Return response
            response = {
                "action": "play",
                "audio_url": audio_url,
                "record": True,
                "transcribe": True,
                "transcribe_callback": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/transcribe",
                "session_id": session_id
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Error handling recording callback: {e}")
            return self._generate_error_response("Error processing recording")
    
    def _generate_initial_voice_response(self, session_id: str, brand_id: int) -> str:
        """
        Generate initial voice response for incoming call
        """
        try:
            welcome_message = "Thank you for calling our complaint management system. Please wait while I connect you to our AI assistant."
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(welcome_message, "en-US-Standard-A")
            
            response = {
                "action": "play",
                "audio_url": audio_url,
                "record": True,
                "transcribe": True,
                "transcribe_callback": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/transcribe",
                "session_id": session_id
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Error generating initial voice response: {e}")
            return self._generate_error_response("Error generating response")
    
    def _generate_error_response(self, message: str) -> str:
        """
        Generate error response
        """
        try:
            error_message = "I'm sorry, but I encountered an error. Please try again later or contact support."
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(error_message, "en-US-Standard-A")
            
            response = {
                "action": "play",
                "audio_url": audio_url,
                "end_call": True
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Error generating error response: {e}")
            return json.dumps({"action": "end_call"})
    
    def create_interactive_voice_response(self, options: List[Dict[str, str]]) -> str:
        """
        Create interactive voice response menu
        """
        try:
            menu_text = "Please select an option: "
            for i, option in enumerate(options, 1):
                menu_text += f"Press {i} for {option['description']}. "
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(menu_text, "en-US-Standard-A")
            
            response = {
                "action": "play",
                "audio_url": audio_url,
                "gather": {
                    "input": "dtmf",
                    "timeout": 10,
                    "num_digits": 1,
                    "action": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/menu"
                }
            }
            
            return json.dumps(response)
            
        except Exception as e:
            logger.error(f"Error creating IVR menu: {e}")
            return self._generate_error_response("Error creating menu")
    
    def handle_menu_selection(self, digits: str, menu_options: List[Dict[str, str]]) -> str:
        """
        Handle menu selection from IVR
        """
        try:
            selection = int(digits) - 1
            
            if 0 <= selection < len(menu_options):
                selected_option = menu_options[selection]
                response_text = f"You selected {selected_option['description']}. {selected_option.get('response', '')}"
                
                # Generate TTS response
                audio_url = self.tts_service.generate_speech_url(response_text, "en-US-Standard-A")
                
                response = {
                    "action": "play",
                    "audio_url": audio_url,
                    "record": True,
                    "transcribe": True,
                    "transcribe_callback": f"{settings.BASE_URL}/api/v1/webhook/knowlarity/transcribe"
                }
                
                return json.dumps(response)
            else:
                return self._generate_error_response("Invalid selection")
                
        except Exception as e:
            logger.error(f"Error handling menu selection: {e}")
            return self._generate_error_response("Error processing selection") 