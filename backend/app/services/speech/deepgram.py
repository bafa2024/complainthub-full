# backend/app/services/speech/deepgram.py

import asyncio
import logging
from typing import Dict, Any, Optional, Tuple
from deepgram import Deepgram
<<<<<<< HEAD
from ..config import settings
=======
from app.config.settings import settings
>>>>>>> e5492e4fab81295b23f8d228dd093188a2d6e925
import json
import traceback

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        self.deepgram_api_key = settings.DEEPGRAM_API_KEY
        self.has_api_key = bool(self.deepgram_api_key and self.deepgram_api_key.strip())
        
        if self.has_api_key:
            try:
                self.deepgram = Deepgram(self.deepgram_api_key)
                logger.info("Deepgram client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Deepgram client: {e}")
                self.has_api_key = False
        else:
            logger.warning("Deepgram API key not found. Speech-to-text features will be limited.")
            self.has_api_key = False

    async def transcribe_audio_file(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe an audio file using Deepgram with sentiment analysis.
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (e.g., "en", "hi", "es")
            
        Returns:
            Dictionary containing transcription and analysis results
        """
        try:
            if not self.has_api_key:
                logger.warning("Deepgram not available, returning mock transcription")
                return {
                    "transcript": "Mock transcription - Deepgram not configured",
                    "confidence": 0.8,
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "words": [],
                    "language": language,
                    "duration": 0.0
                }
            
            # Configure transcription options
            options = {
                "smart_format": True,
                "punctuate": True,
                "diarize": False,
                "utterances": True,
                "sentiment": True,  # Enable sentiment analysis
                "language": language,
                "model": "nova-2" if language == "en" else "nova-2-multilingual"
            }
            
            # Open and transcribe the audio file
            with open(audio_file_path, "rb") as audio:
                response = await self.deepgram.transcription.prerecorded(
                    {"buffer": audio, "mimetype": "audio/wav"},
                    options
                )
            
            # Extract transcription
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            confidence = response["results"]["channels"][0]["alternatives"][0]["confidence"]
            
            # Extract sentiment analysis
            sentiment_data = response.get("results", {}).get("sentiment", {})
            sentiment_score = sentiment_data.get("overall", 0.0)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # Extract word-level data
            words = []
            if "words" in response["results"]["channels"][0]["alternatives"][0]:
                words = response["results"]["channels"][0]["alternatives"][0]["words"]
            
            # Get duration
            duration = response.get("metadata", {}).get("duration", 0.0)
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "sentiment": sentiment_label,
                "sentiment_score": sentiment_score,
                "words": words,
                "language": language,
                "duration": duration,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "transcript": f"Error transcribing audio: {str(e)}",
                "confidence": 0.0,
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "words": [],
                "language": language,
                "duration": 0.0,
                "error": str(e)
            }

    async def transcribe_audio_bytes(self, audio_bytes: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio bytes using Deepgram.
        
        Args:
            audio_bytes: Audio data as bytes
            language: Language code
            
        Returns:
            Dictionary containing transcription and analysis results
        """
        try:
            if not self.has_api_key:
                logger.warning("Deepgram not available, returning mock transcription")
                return {
                    "transcript": "Mock transcription - Deepgram not configured",
                    "confidence": 0.8,
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "words": [],
                    "language": language,
                    "duration": 0.0
                }
            
            # Configure transcription options
            options = {
                "smart_format": True,
                "punctuate": True,
                "diarize": False,
                "utterances": True,
                "sentiment": True,
                "language": language,
                "model": "nova-2" if language == "en" else "nova-2-multilingual"
            }
            
            # Transcribe the audio bytes
            response = await self.deepgram.transcription.prerecorded(
                {"buffer": audio_bytes, "mimetype": "audio/wav"},
                options
            )
            
            # Extract transcription
            transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]
            confidence = response["results"]["channels"][0]["alternatives"][0]["confidence"]
            
            # Extract sentiment analysis
            sentiment_data = response.get("results", {}).get("sentiment", {})
            sentiment_score = sentiment_data.get("overall", 0.0)
            sentiment_label = self._get_sentiment_label(sentiment_score)
            
            # Extract word-level data
            words = []
            if "words" in response["results"]["channels"][0]["alternatives"][0]:
                words = response["results"]["channels"][0]["alternatives"][0]["words"]
            
            # Get duration
            duration = response.get("metadata", {}).get("duration", 0.0)
            
            return {
                "transcript": transcript,
                "confidence": confidence,
                "sentiment": sentiment_label,
                "sentiment_score": sentiment_score,
                "words": words,
                "language": language,
                "duration": duration,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio bytes: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "transcript": f"Error transcribing audio: {str(e)}",
                "confidence": 0.0,
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "words": [],
                "language": language,
                "duration": 0.0,
                "error": str(e)
            }

    def _get_sentiment_label(self, score: float) -> str:
        """
        Convert sentiment score to label.
        
        Args:
            score: Sentiment score between -1 and 1
            
        Returns:
            Sentiment label
        """
        if score >= 0.3:
            return "positive"
        elif score <= -0.3:
            return "negative"
        else:
            return "neutral"

    async def detect_language(self, audio_bytes: bytes) -> str:
        """
        Detect the language of audio content.
        
        Args:
            audio_bytes: Audio data as bytes
            
        Returns:
            Language code (e.g., "en", "hi", "es")
        """
        try:
            if not self.has_api_key:
                return "en"  # Default to English
            
            # Use Deepgram's language detection
            options = {
                "detect_language": True,
                "model": "nova-2-multilingual"
            }
            
            response = await self.deepgram.transcription.prerecorded(
                {"buffer": audio_bytes, "mimetype": "audio/wav"},
                options
            )
            
            # Extract detected language
            detected_language = response.get("metadata", {}).get("language", "en")
            return detected_language
            
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"  # Default to English

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for transcription.
        
        Returns:
            List of supported language codes
        """
        return [
            "en",  # English
            "hi",  # Hindi
            "es",  # Spanish
            "fr",  # French
            "de",  # German
            "it",  # Italian
            "pt",  # Portuguese
            "ru",  # Russian
            "ja",  # Japanese
            "ko",  # Korean
            "zh",  # Chinese
            "ar",  # Arabic
            "tr",  # Turkish
            "nl",  # Dutch
            "pl",  # Polish
            "sv",  # Swedish
            "da",  # Danish
            "no",  # Norwegian
            "fi",  # Finnish
            "cs",  # Czech
            "hu",  # Hungarian
            "ro",  # Romanian
            "bg",  # Bulgarian
            "hr",  # Croatian
            "sk",  # Slovak
            "sl",  # Slovenian
            "et",  # Estonian
            "lv",  # Latvian
            "lt"   # Lithuanian
        ]

# Global instance
deepgram_service = DeepgramService()
