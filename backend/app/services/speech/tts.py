# backend/app/services/speech/tts.py

import asyncio
import logging
import os
import tempfile
from typing import Dict, Any, Optional, List
import requests
from ..config import settings
import json
import traceback
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY
        self.has_api_key = bool(self.google_api_key and self.google_api_key.strip())
        
        # Voice profiles for different users
        self.voice_profiles = {
            "male": [
                {"name": "en-US-Standard-A", "language": "en", "gender": "male"},
                {"name": "en-US-Standard-C", "language": "en", "gender": "male"},
                {"name": "en-US-Standard-E", "language": "en", "gender": "male"},
                {"name": "en-US-Wavenet-A", "language": "en", "gender": "male"},
                {"name": "en-US-Wavenet-C", "language": "en", "gender": "male"},
                {"name": "en-US-Wavenet-E", "language": "en", "gender": "male"},
            ],
            "female": [
                {"name": "en-US-Standard-B", "language": "en", "gender": "female"},
                {"name": "en-US-Standard-D", "language": "en", "gender": "female"},
                {"name": "en-US-Standard-F", "language": "en", "gender": "female"},
                {"name": "en-US-Wavenet-B", "language": "en", "gender": "female"},
                {"name": "en-US-Wavenet-D", "language": "en", "gender": "female"},
                {"name": "en-US-Wavenet-F", "language": "en", "gender": "female"},
            ]
        }
        
        # Hindi voices
        self.hindi_voices = {
            "male": [
                {"name": "hi-IN-Standard-A", "language": "hi", "gender": "male"},
                {"name": "hi-IN-Wavenet-A", "language": "hi", "gender": "male"},
            ],
            "female": [
                {"name": "hi-IN-Standard-B", "language": "hi", "gender": "female"},
                {"name": "hi-IN-Wavenet-B", "language": "hi", "gender": "female"},
            ]
        }
        
        # User voice assignments (in production, this should be stored in database)
        self.user_voice_assignments = {}
        
        if self.has_api_key:
            logger.info("TTS service initialized with Google Cloud API")
        else:
            logger.warning("Google Cloud API key not found. TTS features will be limited.")

    def assign_voice_to_user(self, user_id: str, gender: str = "female", language: str = "en") -> str:
        """
        Assign a unique voice to a user for consistent experience.
        
        Args:
            user_id: Unique identifier for the user
            gender: Preferred gender ("male" or "female")
            language: Language code ("en", "hi", etc.)
            
        Returns:
            Voice name assigned to the user
        """
        try:
            if user_id in self.user_voice_assignments:
                return self.user_voice_assignments[user_id]["voice_name"]
            
            # Select appropriate voice pool based on language
            if language == "hi":
                voice_pool = self.hindi_voices.get(gender, self.hindi_voices["female"])
            else:
                voice_pool = self.voice_profiles.get(gender, self.voice_profiles["female"])
            
            # Assign a voice (in production, this could be more sophisticated)
            import random
            selected_voice = random.choice(voice_pool)
            
            # Store the assignment
            self.user_voice_assignments[user_id] = {
                "voice_name": selected_voice["name"],
                "language": selected_voice["language"],
                "gender": selected_voice["gender"],
                "assigned_at": str(uuid.uuid4())  # Simple timestamp
            }
            
            logger.info(f"Assigned voice {selected_voice['name']} to user {user_id}")
            return selected_voice["name"]
            
        except Exception as e:
            logger.error(f"Error assigning voice to user: {e}")
            # Return default voice
            return "en-US-Standard-B"

    def get_user_voice(self, user_id: str) -> str:
        """
        Get the assigned voice for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Voice name assigned to the user
        """
        if user_id in self.user_voice_assignments:
            return self.user_voice_assignments[user_id]["voice_name"]
        else:
            # Assign a default voice if none exists
            return self.assign_voice_to_user(user_id)

    async def synthesize_speech(self, text: str, user_id: str = None, language: str = "en") -> Dict[str, Any]:
        """
        Convert text to speech using Google Cloud Text-to-Speech.
        
        Args:
            text: Text to convert to speech
            user_id: User identifier for voice assignment
            language: Language code
            
        Returns:
            Dictionary containing audio data and metadata
        """
        try:
            if not self.has_api_key:
                logger.warning("Google Cloud not available, returning mock audio")
                return {
                    "audio_data": b"mock_audio_data",
                    "audio_url": None,
                    "voice_name": "en-US-Standard-B",
                    "language": language,
                    "text_length": len(text),
                    "error": "TTS service not configured"
                }
            
            # Get or assign voice for user
            voice_name = self.get_user_voice(user_id) if user_id else "en-US-Standard-B"
            
            # Prepare the request
            url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.google_api_key}"
            
            # Configure voice parameters
            voice_config = {
                "languageCode": language,
                "name": voice_name,
                "ssmlGender": "FEMALE" if "female" in voice_name.lower() else "MALE"
            }
            
            # Configure audio parameters
            audio_config = {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0,
                "volumeGainDb": 0.0
            }
            
            # Prepare request body
            request_body = {
                "input": {"text": text},
                "voice": voice_config,
                "audioConfig": audio_config
            }
            
            # Make the API request
            response = requests.post(url, json=request_body)
            
            if response.status_code == 200:
                result = response.json()
                audio_content = result.get("audioContent", "")
                
                # Decode base64 audio content
                import base64
                audio_data = base64.b64decode(audio_content)
                
                # Save audio file (optional)
                audio_url = await self._save_audio_file(audio_data, user_id)
                
                return {
                    "audio_data": audio_data,
                    "audio_url": audio_url,
                    "voice_name": voice_name,
                    "language": language,
                    "text_length": len(text),
                    "success": True
                }
            else:
                logger.error(f"TTS API error: {response.status_code} - {response.text}")
                return {
                    "audio_data": b"",
                    "audio_url": None,
                    "voice_name": voice_name,
                    "language": language,
                    "text_length": len(text),
                    "error": f"TTS API error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "audio_data": b"",
                "audio_url": None,
                "voice_name": "en-US-Standard-B",
                "language": language,
                "text_length": len(text),
                "error": str(e)
            }

    async def _save_audio_file(self, audio_data: bytes, user_id: str = None) -> Optional[str]:
        """
        Save audio data to a file and return the URL.
        
        Args:
            audio_data: Audio data as bytes
            user_id: User identifier for file naming
            
        Returns:
            URL or path to the saved audio file
        """
        try:
            # Create uploads directory if it doesn't exist
            uploads_dir = Path("uploads/tts")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = str(uuid.uuid4())
            filename = f"tts_{user_id}_{timestamp}.mp3" if user_id else f"tts_{timestamp}.mp3"
            file_path = uploads_dir / filename
            
            # Save the audio file
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            # Return the file path (in production, this would be a URL)
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            return None

    def get_available_voices(self, language: str = "en") -> List[Dict[str, str]]:
        """
        Get list of available voices for a language.
        
        Args:
            language: Language code
            
        Returns:
            List of available voices
        """
        try:
            if not self.has_api_key:
                # Return mock voices
                if language == "hi":
                    return self.hindi_voices["female"] + self.hindi_voices["male"]
                else:
                    return self.voice_profiles["female"] + self.voice_profiles["male"]
            
            # In production, this would call the Google Cloud TTS API
            # to get the actual list of available voices
            url = f"https://texttospeech.googleapis.com/v1/voices?key={self.google_api_key}"
            response = requests.get(url)
            
            if response.status_code == 200:
                voices_data = response.json()
                available_voices = []
                
                for voice in voices_data.get("voices", []):
                    if voice.get("languageCodes", [""])[0].startswith(language):
                        available_voices.append({
                            "name": voice.get("name", ""),
                            "language": voice.get("languageCodes", [""])[0],
                            "gender": voice.get("ssmlGender", "NEUTRAL")
                        })
                
                return available_voices
            else:
                logger.error(f"Error fetching voices: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []

    def change_user_voice(self, user_id: str, voice_name: str) -> bool:
        """
        Change the voice assigned to a user.
        
        Args:
            user_id: User identifier
            voice_name: New voice name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if user_id in self.user_voice_assignments:
                self.user_voice_assignments[user_id]["voice_name"] = voice_name
                self.user_voice_assignments[user_id]["assigned_at"] = str(uuid.uuid4())
                logger.info(f"Changed voice for user {user_id} to {voice_name}")
                return True
            else:
                logger.warning(f"User {user_id} not found in voice assignments")
                return False
                
        except Exception as e:
            logger.error(f"Error changing user voice: {e}")
            return False

    def get_voice_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about voice usage.
        
        Returns:
            Dictionary containing voice usage statistics
        """
        try:
            voice_counts = {}
            gender_counts = {"male": 0, "female": 0}
            
            for user_id, assignment in self.user_voice_assignments.items():
                voice_name = assignment["voice_name"]
                gender = assignment["gender"]
                
                voice_counts[voice_name] = voice_counts.get(voice_name, 0) + 1
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            return {
                "total_users": len(self.user_voice_assignments),
                "voice_distribution": voice_counts,
                "gender_distribution": gender_counts,
                "most_popular_voice": max(voice_counts.items(), key=lambda x: x[1])[0] if voice_counts else None
            }
            
        except Exception as e:
            logger.error(f"Error getting voice statistics: {e}")
            return {
                "total_users": 0,
                "voice_distribution": {},
                "gender_distribution": {"male": 0, "female": 0},
                "most_popular_voice": None
            }

# Global instance
tts_service = TTSService()
