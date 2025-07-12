# backend/app/adapters/exotel_adapter.py

import logging
import json
import requests
from typing import Dict, Any, Optional, List
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.services.speech.tts import TTSService
from app.config.settings import settings

logger = logging.getLogger(__name__)

class ExotelAdapter:
    def __init__(self):
        self.sid = getattr(settings, 'EXOTEL_SID', '')
        self.token = getattr(settings, 'EXOTEL_TOKEN', '')
        self.base_url = getattr(settings, 'EXOTEL_BASE_URL', 'https://api.exotel.com/v1')
        self.ai_engine = AIEngine()
        self.tts_service = TTSService()
        
        if not self.sid or not self.token:
            logger.warning("Exotel credentials not configured")
    
    def handle_voice_call(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                         db_session, brand_id: int) -> str:
        """
        Handle incoming voice call from Exotel and generate response
        """
        try:
            # Extract call data from Exotel webhook
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            call_sid = request_data.get('CallSid', '')
            call_status = request_data.get('CallStatus', '')
            recording_url = request_data.get('RecordingUrl', '')
            
            # Create session ID
            session_id = f"exotel_voice_{from_number}_{call_sid}"
            
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
            logger.error(f"Error handling Exotel voice call: {e}")
            return self._generate_error_response("Sorry, I encountered an error. Please try again later.")
    
    def handle_sms(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                   db_session, brand_id: int) -> Dict[str, Any]:
        """
        Handle incoming SMS from Exotel
        """
        try:
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            message_body = request_data.get('Body', '')
            message_sid = request_data.get('MessageSid', '')
            
            if not message_body.strip():
                return {
                    "success": False,
                    "error": "No message content received"
                }
            
            # Create session ID
            session_id = f"exotel_sms_{from_number}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=message_body,
                brand_id=brand_id,
                channel="sms"
            )
            
            # Send response back via Exotel SMS API
            success = self.send_sms(from_number, bot_response)
            
            return {
                "success": success,
                "response": bot_response,
                "message_sid": message_sid
            }
            
        except Exception as e:
            logger.error(f"Error handling Exotel SMS: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def make_outbound_call(self, to_number: str, message: str, 
                          voice_id: Optional[str] = None) -> bool:
        """
        Make an outbound voice call using Exotel API
        """
        try:
            if not self.sid or not self.token:
                logger.error("Exotel credentials not configured")
                return False
            
            # Generate TTS audio
            audio_url = self.tts_service.generate_speech_url(message, voice_id or "en-US-Standard-A")
            
            # Prepare call data for Exotel
            call_data = {
                "From": settings.EXOTEL_FROM_NUMBER,
                "To": to_number,
                "Url": f"{settings.BASE_URL}/api/v1/webhook/exotel/voice",
                "Record": True,
                "Transcribe": True,
                "TranscribeCallback": f"{settings.BASE_URL}/api/v1/webhook/exotel/transcribe"
            }
            
            # Make API call to Exotel
            response = requests.post(
                f"{self.base_url}/Accounts/{self.sid}/Calls.json",
                data=call_data,
                auth=(self.sid, self.token)
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Exotel outbound call initiated: {result.get('sid')}")
                return True
            else:
                logger.error(f"Failed to initiate Exotel call: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error making Exotel outbound call: {e}")
            return False
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send an SMS message via Exotel
        """
        try:
            if not self.sid or not self.token:
                logger.error("Exotel credentials not configured")
                return False
            
            # Prepare SMS data for Exotel
            sms_data = {
                "From": settings.EXOTEL_FROM_NUMBER,
                "To": to_number,
                "Body": message
            }
            
            # Send SMS via Exotel API
            response = requests.post(
                f"{self.base_url}/Accounts/{self.sid}/Messages.json",
                data=sms_data,
                auth=(self.sid, self.token)
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Exotel SMS sent successfully: {result.get('sid')}")
                return True
            else:
                logger.error(f"Failed to send Exotel SMS: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Exotel SMS: {e}")
            return False
    
    def _handle_answered_call(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                             db_session, brand_id: int) -> str:
        """
        Handle answered call and start conversation
        """
        try:
            from_number = request_data.get('From', '')
            call_sid = request_data.get('CallSid', '')
            session_id = f"exotel_voice_{from_number}_{call_sid}"
            
            # Generate welcome message
            welcome_message = "Welcome to our complaint management system. Please describe your issue and I'll help you create a ticket."
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(welcome_message, "en-US-Standard-A")
            
            # Return Exotel-compatible TwiML response
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Record action="{settings.BASE_URL}/api/v1/webhook/exotel/recording" 
            transcribe="true" 
            transcribeCallback="{settings.BASE_URL}/api/v1/webhook/exotel/transcribe"
            maxLength="60" 
            timeout="10" />
</Response>"""
            
            return twiml_response
            
        except Exception as e:
            logger.error(f"Error handling answered call: {e}")
            return self._generate_error_response("Error processing call")
    
    def _handle_recording_callback(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                                 db_session, brand_id: int) -> str:
        """
        Handle recording callback with transcription
        """
        try:
            recording_url = request_data.get('RecordingUrl', '')
            transcription_text = request_data.get('TranscriptionText', '')
            from_number = request_data.get('From', '')
            call_sid = request_data.get('CallSid', '')
            
            if not transcription_text:
                return self._generate_error_response("No transcription available")
            
            # Create session ID
            session_id = f"exotel_voice_{from_number}_{call_sid}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=transcription_text,
                brand_id=brand_id,
                channel="voice"
            )
            
            # Generate TTS response
            audio_url = self.tts_service.generate_speech_url(bot_response, "en-US-Standard-A")
            
            # Return TwiML response
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Record action="{settings.BASE_URL}/api/v1/webhook/exotel/recording" 
            transcribe="true" 
            transcribeCallback="{settings.BASE_URL}/api/v1/webhook/exotel/transcribe"
            maxLength="60" 
            timeout="10" />
</Response>"""
            
            return twiml_response
            
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
            
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Gather input="dtmf" timeout="10" numDigits="1" action="{settings.BASE_URL}/api/v1/webhook/exotel/menu">
        <Say>Press 1 to lodge a complaint. Press 2 to check complaint status. Press 3 to speak to an agent.</Say>
    </Gather>
</Response>"""
            
            return twiml_response
            
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
            
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Hangup />
</Response>"""
            
            return twiml_response
            
        except Exception as e:
            logger.error(f"Error generating error response: {e}")
            return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Hangup />
</Response>"""
    
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
            
            twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Gather input="dtmf" timeout="10" numDigits="1" action="{settings.BASE_URL}/api/v1/webhook/exotel/menu">
        <Say>Please press a number to continue.</Say>
    </Gather>
</Response>"""
            
            return twiml_response
            
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
                
                twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Record action="{settings.BASE_URL}/api/v1/webhook/exotel/recording" 
            transcribe="true" 
            transcribeCallback="{settings.BASE_URL}/api/v1/webhook/exotel/transcribe"
            maxLength="60" 
            timeout="10" />
</Response>"""
                
                return twiml_response
            else:
                return self._generate_error_response("Invalid selection")
                
        except Exception as e:
            logger.error(f"Error handling menu selection: {e}")
            return self._generate_error_response("Error processing selection")
    
    def handle_webhook_verification(self, request_data: Dict[str, Any]) -> str:
        """
        Handle webhook verification from Exotel
        """
        try:
            # Extract verification parameters
            challenge = request_data.get('challenge', '')
            
            if challenge:
                return challenge
            else:
                return "verified"
                
        except Exception as e:
            logger.error(f"Error handling webhook verification: {e}")
            return "error" 