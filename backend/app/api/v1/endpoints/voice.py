# backend/app/api/v1/endpoints/voice.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging
import tempfile
import os
import uuid

from app.api.v1.deps import get_db, get_current_user
from app.models import User
from app.services.speech.deepgram import deepgram_service
from app.services.speech.tts import tts_service
from app.core.ai_engine import AIEngine
from app.api.v1.endpoints.conversation import process_message_with_ai

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/speech-to-text")
async def process_voice_message(
    audio_file: UploadFile = File(...),
    brand_id: Optional[int] = Form(None),
    language: Optional[str] = Form("en"),
    brand_context: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process voice message through STT -> AI -> TTS pipeline.
    This is the main voice processing endpoint.
    """
    try:
        logger.info(f"Processing voice message from user {current_user.id}")
        
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Step 1: Speech-to-Text using Deepgram
            logger.info("Converting speech to text...")
            stt_result = await deepgram_service.transcribe_audio_file(
                temp_file.name, 
                language=language
            )
            
            if "error" in stt_result:
                raise HTTPException(status_code=500, detail=f"STT error: {stt_result['error']}")
            
            transcript = stt_result["transcript"]
            if not transcript or transcript.strip() == "":
                raise HTTPException(status_code=400, detail="No speech detected in audio")
            
            logger.info(f"Transcribed text: {transcript}")
            
            # Step 2: Process with AI Engine
            logger.info("Processing with AI engine...")
            ai_engine = AIEngine()
            
            # Build conversation history (simplified for now)
            conversation_history = []
            
            # Process the transcribed text with AI
            ai_response = await process_message_with_ai(
                message=transcript,
                conversation_history=conversation_history,
                brand_context=brand_context,
                language=language,
                user_id=current_user.id,
                ai_engine=ai_engine
            )
            
            if "error" in ai_response:
                raise HTTPException(status_code=500, detail=f"AI processing error: {ai_response['error']}")
            
            response_text = ai_response["response"]
            logger.info(f"AI response: {response_text}")
            
            # Step 3: Text-to-Speech for AI response
            logger.info("Converting AI response to speech...")
            tts_result = await tts_service.synthesize_speech(
                text=response_text,
                user_id=str(current_user.id),
                language=language
            )
            
            if "error" in tts_result:
                logger.warning(f"TTS error: {tts_result['error']}")
                # Continue without TTS if it fails
            
            # Prepare response
            response_data = {
                "success": True,
                "transcript": transcript,
                "transcript_confidence": stt_result.get("confidence", 0.0),
                "transcript_sentiment": stt_result.get("sentiment", "neutral"),
                "ai_response": response_text,
                "requires_followup": ai_response.get("requires_followup", False),
                "ticket_created": ai_response.get("create_ticket", False),
                "ticket_id": ai_response.get("ticket_id"),
                "metadata": {
                    "stt_analysis": {
                        "confidence": stt_result.get("confidence", 0.0),
                        "sentiment": stt_result.get("sentiment", "neutral"),
                        "sentiment_score": stt_result.get("sentiment_score", 0.0),
                        "duration": stt_result.get("duration", 0.0),
                        "language": stt_result.get("language", language)
                    },
                    "ai_analysis": ai_response.get("metadata", {}),
                    "tts_info": {
                        "voice_name": tts_result.get("voice_name", "unknown"),
                        "audio_available": "audio_data" in tts_result and len(tts_result["audio_data"]) > 0,
                        "audio_url": tts_result.get("audio_url")
                    }
                }
            }
            
            # Include TTS audio data if available
            if "audio_data" in tts_result and len(tts_result["audio_data"]) > 0:
                import base64
                response_data["audio_response"] = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
                response_data["audio_url"] = tts_result.get("audio_url")
            
            return response_data
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing voice message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in voice processing")

@router.post("/text-to-speech")
async def synthesize_text(
    text: str = Form(...),
    language: Optional[str] = Form("en"),
    voice_preference: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convert text to speech using TTS service.
    """
    try:
        logger.info(f"Converting text to speech for user {current_user.id}")
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text is required")
        
        if len(text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
        
        # Synthesize speech
        tts_result = await tts_service.synthesize_speech(
            text=text,
            user_id=str(current_user.id),
            language=language
        )
        
        if "error" in tts_result:
            raise HTTPException(status_code=500, detail=f"TTS error: {tts_result['error']}")
        
        # Prepare response
        response_data = {
            "success": True,
            "text": text,
            "voice_name": tts_result.get("voice_name", "unknown"),
            "language": language,
            "text_length": len(text),
            "audio_url": tts_result.get("audio_url")
        }
        
        # Include audio data
        if "audio_data" in tts_result and len(tts_result["audio_data"]) > 0:
            import base64
            response_data["audio_response"] = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text-to-speech: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in TTS")

@router.post("/transcribe-only")
async def transcribe_audio_only(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    detect_language: Optional[bool] = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transcribe audio without AI processing.
    """
    try:
        logger.info(f"Transcribing audio for user {current_user.id}")
        
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Detect language if requested
            if detect_language:
                detected_lang = await deepgram_service.detect_language(content)
                language = detected_lang
            
            # Transcribe audio
            stt_result = await deepgram_service.transcribe_audio_file(
                temp_file.name, 
                language=language
            )
            
            if "error" in stt_result:
                raise HTTPException(status_code=500, detail=f"STT error: {stt_result['error']}")
            
            return {
                "success": True,
                "transcript": stt_result["transcript"],
                "confidence": stt_result.get("confidence", 0.0),
                "sentiment": stt_result.get("sentiment", "neutral"),
                "sentiment_score": stt_result.get("sentiment_score", 0.0),
                "language": stt_result.get("language", language),
                "duration": stt_result.get("duration", 0.0),
                "word_count": len(stt_result["transcript"].split()) if stt_result["transcript"] else 0
            }
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in transcription")

@router.get("/supported-languages")
def get_supported_languages(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of supported languages for voice processing.
    """
    try:
        return {
            "success": True,
            "stt_languages": deepgram_service.get_supported_languages(),
            "tts_languages": ["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
            "common_languages": [
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
                {"code": "es", "name": "Spanish", "native_name": "Español"},
                {"code": "fr", "name": "French", "native_name": "Français"},
                {"code": "de", "name": "German", "native_name": "Deutsch"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/user-voice-profile")
def get_user_voice_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get voice profile for current user.
    """
    try:
        user_id = str(current_user.id)
        voice_name = tts_service.get_user_voice(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "assigned_voice": voice_name,
            "voice_assignment": tts_service.user_voice_assignments.get(user_id, {})
        }
        
    except Exception as e:
        logger.error(f"Error getting user voice profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/change-voice")
def change_user_voice(
    voice_name: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Change voice assigned to current user.
    """
    try:
        user_id = str(current_user.id)
        success = tts_service.change_user_voice(user_id, voice_name)
        
        if success:
            return {
                "success": True,
                "message": f"Voice changed to {voice_name}",
                "new_voice": voice_name
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to change voice")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing user voice: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/available-voices")
def get_available_voices(
    language: Optional[str] = "en",
    current_user: User = Depends(get_current_user)
):
    """
    Get available voices for a language.
    """
    try:
        voices = tts_service.get_available_voices(language)
        
        return {
            "success": True,
            "language": language,
            "voices": voices,
            "total_voices": len(voices)
        }
        
    except Exception as e:
        logger.error(f"Error getting available voices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/voice-statistics")
def get_voice_usage_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    Get voice usage statistics (admin only).
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        stats = tts_service.get_voice_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/voice-chat")
async def voice_chat_session(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    brand_id: Optional[int] = Form(None),
    language: Optional[str] = Form("en"),
    brand_context: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete voice chat session: STT -> AI -> TTS with conversation context.
    This endpoint maintains conversation state for voice interactions.
    """
    try:
        logger.info(f"Starting voice chat session for user {current_user.id}")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Validate audio file
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        try:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Step 1: Speech-to-Text
            stt_result = await deepgram_service.transcribe_audio_file(
                temp_file.name, 
                language=language
            )
            
            if "error" in stt_result:
                raise HTTPException(status_code=500, detail=f"STT error: {stt_result['error']}")
            
            transcript = stt_result["transcript"]
            if not transcript or transcript.strip() == "":
                raise HTTPException(status_code=400, detail="No speech detected in audio")
            
            # Step 2: AI Processing with conversation context
            ai_engine = AIEngine()
            
            # In a full implementation, this would load conversation history from database
            conversation_history = []
            
            ai_response = await process_message_with_ai(
                message=transcript,
                conversation_history=conversation_history,
                brand_context=brand_context,
                language=language,
                user_id=current_user.id,
                ai_engine=ai_engine
            )
            
            response_text = ai_response["response"]
            
            # Step 3: Text-to-Speech for response
            tts_result = await tts_service.synthesize_speech(
                text=response_text,
                user_id=str(current_user.id),
                language=language
            )
            
            # Prepare comprehensive response
            response_data = {
                "success": True,
                "session_id": session_id,
                "user_input": {
                    "transcript": transcript,
                    "confidence": stt_result.get("confidence", 0.0),
                    "sentiment": stt_result.get("sentiment", "neutral"),
                    "duration": stt_result.get("duration", 0.0)
                },
                "ai_response": {
                    "text": response_text,
                    "requires_followup": ai_response.get("requires_followup", False),
                    "ticket_created": ai_response.get("create_ticket", False),
                    "ticket_id": ai_response.get("ticket_id"),
                    "suggested_actions": ai_response.get("suggested_actions", [])
                },
                "voice_response": {
                    "voice_name": tts_result.get("voice_name", "unknown"),
                    "audio_url": tts_result.get("audio_url"),
                    "audio_available": "audio_data" in tts_result and len(tts_result["audio_data"]) > 0
                },
                "conversation_context": {
                    "language": language,
                    "brand_id": brand_id,
                    "turn_count": len(conversation_history) + 1
                }
            }
            
            # Include audio data if available
            if "audio_data" in tts_result and len(tts_result["audio_data"]) > 0:
                import base64
                response_data["voice_response"]["audio_data"] = base64.b64encode(tts_result["audio_data"]).decode('utf-8')
            
            return response_data
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice chat session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in voice chat")