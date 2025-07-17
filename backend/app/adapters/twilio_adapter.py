# backend/app/adapters/twilio_adapter.py

import logging
import json
from typing import Dict, Any, Optional, List
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from app.core.ai_engine import AIEngine
from app.core.conversation_manager import ConversationManager
from app.services.speech.tts import TTSService
from app.config.settings import settings

logger = logging.getLogger(__name__)

class TwilioAdapter:
    def __init__(self):
        self.client = None
        self.ai_engine = AIEngine()
        self.tts_service = TTSService()
        
        # Initialize Twilio client if credentials are available
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and hasattr(settings, 'TWILIO_AUTH_TOKEN'):
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def handle_voice_call(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                         db_session, brand_id: int) -> str:
        """
        Handle incoming voice call and generate TwiML response
        """
        try:
            # Extract call data
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            call_sid = request_data.get('CallSid', '')
            call_status = request_data.get('CallStatus', '')
            
            # Check if this is a recording callback
            if 'RecordingUrl' in request_data:
                return self._handle_recording_callback(request_data, conversation_manager, db_session, brand_id)
            
            # Check if this is a transcription callback
            if 'TranscriptionText' in request_data:
                return self._handle_transcription_callback(request_data, conversation_manager, db_session, brand_id)
            
            # Create session ID
            session_id = f"voice_{from_number}_{call_sid}"
            
            # Generate initial TwiML response
            return self._generate_initial_voice_response(session_id, brand_id)
            
        except Exception as e:
            logger.error(f"Error handling voice call: {e}")
            return self._generate_error_response("Sorry, I encountered an error. Please try again later.")
    
    def handle_sms(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                   db_session, brand_id: int) -> str:
        """
        Handle incoming SMS and generate TwiML response
        """
        try:
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            message_body = request_data.get('Body', '')
            media_url = request_data.get('MediaUrl0')
            
            if not message_body.strip():
                return self._generate_sms_response("I didn't receive any message. Please try again.")
            
            # Create session ID
            session_id = f"sms_{from_number}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=message_body,
                brand_id=brand_id,
                channel="sms"
            )
            
            return self._generate_sms_response(bot_response)
            
        except Exception as e:
            logger.error(f"Error handling SMS: {e}")
            return self._generate_sms_response("Sorry, I encountered an error. Please try again later.")
    
    def handle_whatsapp(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                       db_session, brand_id: int) -> str:
        """
        Handle incoming WhatsApp message and generate TwiML response
        """
        try:
            from_number = request_data.get('From', '')
            to_number = request_data.get('To', '')
            message_body = request_data.get('Body', '')
            media_url = request_data.get('MediaUrl0')
            
            if not message_body.strip():
                return self._generate_whatsapp_response("I didn't receive any message. Please try again.")
            
            # Create session ID
            session_id = f"whatsapp_{from_number}"
            
            # Process message through conversation manager
            bot_response = conversation_manager.process_message(
                session_id=session_id,
                user_message=message_body,
                brand_id=brand_id,
                channel="whatsapp"
            )
            
            return self._generate_whatsapp_response(bot_response)
            
        except Exception as e:
            logger.error(f"Error handling WhatsApp: {e}")
            return self._generate_whatsapp_response("Sorry, I encountered an error. Please try again later.")
    
    def make_outbound_call(self, to_number: str, message: str, 
                          voice_id: Optional[str] = None) -> bool:
        """
        Make an outbound voice call using TTS
        """
        try:
            if not self.client:
                logger.error("Twilio client not initialized")
                return False
            
            # Generate TTS audio
            audio_url = self.tts_service.generate_speech_url(message, voice_id or "en-US-Standard-A")
            
            # Make the call
            call = self.client.calls.create(
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                twiml=f'<Response><Play>{audio_url}</Play></Response>'
            )
            
            logger.info(f"Outbound call initiated: {call.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error making outbound call: {e}")
            return False
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send an SMS message
        """
        try:
            if not self.client:
                logger.error("Twilio client not initialized")
                return False
            
            message_obj = self.client.messages.create(
                to=to_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                body=message
            )
            
            logger.info(f"SMS sent successfully: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def send_whatsapp(self, to_number: str, message: str, media_url: Optional[str] = None) -> bool:
        """
        Send a WhatsApp message
        """
        try:
            if not self.client:
                logger.error("Twilio client not initialized")
                return False
            
            # Format phone number for WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            if media_url:
                message_obj = self.client.messages.create(
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    body=message,
                    media_url=[media_url],
                    to=to_number
                )
            else:
                message_obj = self.client.messages.create(
                    from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                    body=message,
                    to=to_number
                )
            
            logger.info(f"WhatsApp message sent: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def _generate_initial_voice_response(self, session_id: str, brand_id: int) -> str:
        """
        Generate initial TwiML for voice call
        """
        resp = VoiceResponse()
        
        # Welcome message
        resp.say(
            "Welcome to our complaint management system. Please state your complaint clearly after the beep. "
            "You can speak for up to 60 seconds.",
            voice='alice',
            language='en-US'
        )
        
        # Record the complaint
        resp.record(
            timeout=60,
            transcribe=True,
            transcribe_callback=f'/api/v1/webhook/voice/transcription',
            recording_status_callback=f'/api/v1/webhook/voice/recording',
            max_length=60,
            play_beep=True,
            trim='trim-silence'
        )
        
        # Fallback if recording fails
        resp.say(
            "I didn't hear anything. Please call back and try again.",
            voice='alice',
            language='en-US'
        )
        
        return str(resp)
    
    def _handle_recording_callback(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                                 db_session, brand_id: int) -> str:
        """
        Handle recording completion callback
        """
        try:
            recording_url = request_data.get('RecordingUrl')
            recording_duration = request_data.get('RecordingDuration')
            call_sid = request_data.get('CallSid')
            
            resp = VoiceResponse()
            
            # Acknowledge recording
            resp.say(
                f"Thank you for your complaint. I've recorded your message for {recording_duration} seconds. "
                "Our team will review it and get back to you soon. Goodbye.",
                voice='alice',
                language='en-US'
            )
            
            # Store recording info for processing
            # This would typically be stored in a database
            logger.info(f"Recording completed: {recording_url}, Duration: {recording_duration}s")
            
            return str(resp)
            
        except Exception as e:
            logger.error(f"Error handling recording callback: {e}")
            return self._generate_error_response("Error processing recording.")
    
    def _handle_transcription_callback(self, request_data: Dict[str, Any], conversation_manager: ConversationManager, 
                                     db_session, brand_id: int) -> str:
        """
        Handle transcription completion callback
        """
        try:
            transcription_text = request_data.get('TranscriptionText', '')
            transcription_status = request_data.get('TranscriptionStatus')
            call_sid = request_data.get('CallSid')
            
            if transcription_status == 'completed' and transcription_text:
                # Process the transcribed text through conversation manager
                session_id = f"voice_transcription_{call_sid}"
                
                bot_response = conversation_manager.process_message(
                    session_id=session_id,
                    user_message=transcription_text,
                    brand_id=brand_id,
                    channel="voice"
                )
                
                # Generate TTS response
                audio_url = self.tts_service.generate_speech_url(bot_response)
                
                resp = VoiceResponse()
                resp.play(audio_url)
                resp.say("Thank you for your complaint. Goodbye.", voice='alice', language='en-US')
                
                return str(resp)
            else:
                return self._generate_error_response("Sorry, I couldn't understand your message. Please try again.")
                
        except Exception as e:
            logger.error(f"Error handling transcription callback: {e}")
            return self._generate_error_response("Error processing transcription.")
    
    def _generate_sms_response(self, message: str) -> str:
        """
        Generate TwiML response for SMS
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def _generate_whatsapp_response(self, message: str) -> str:
        """
        Generate TwiML response for WhatsApp
        """
        response = MessagingResponse()
        response.message(message)
        return str(response)
    
    def _generate_error_response(self, message: str) -> str:
        """
        Generate error TwiML response
        """
        resp = VoiceResponse()
        resp.say(message, voice='alice', language='en-US')
        return str(resp)
    
    def create_interactive_voice_response(self, options: List[Dict[str, str]]) -> str:
        """
        Create interactive voice response menu
        """
        resp = VoiceResponse()
        
        gather = Gather(
            input='dtmf',
            timeout=10,
            num_digits=1,
            action='/api/v1/webhook/voice/ivr',
            method='POST'
        )
        
        gather.say(
            "Please select an option: " + 
            " ".join([f"Press {opt['digit']} for {opt['description']}" for opt in options]),
            voice='alice',
            language='en-US'
        )
        
        resp.append(gather)
        
        # Fallback
        resp.say(
            "I didn't receive any input. Please call back and try again.",
            voice='alice',
            language='en-US'
        )
        
        return str(resp)

# Legacy class for backward compatibility
class TwilioVoiceAdapter:
    @staticmethod
    def handle_call(request_data):
        adapter = TwilioAdapter()
        return adapter.handle_voice_call(request_data, None, None, 1)
