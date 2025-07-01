import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import traceback

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Complaint Management"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "postgresql://postgres:root@localhost:5432/complaintdb"

    SECRET_KEY: str = "a_very_secret_key_that_you_should_change"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # OpenAI API key with multiple possible field names
    OPENAI_API_KEY: str = Field(default="", alias="open_ai_openai_api_key")
    DEEPGRAM_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@complainthubbot.com"
    
    # Frontend URL for invitation links
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding='utf-8',
        extra='ignore',  # Allow extra fields from environment variables
        case_sensitive=False  # Make field matching case-insensitive
    )

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self._validate_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Use default values if settings fail to load
            try:
                super().__init__()
            except Exception as fallback_error:
                logger.error(f"Even fallback settings failed: {fallback_error}")
                # Create a minimal settings object
                self.PROJECT_NAME = "AI Complaint Management"
                self.API_V1_STR = "/api/v1"
                self.DATABASE_URL = "sqlite:///./voicebot.db"
                self.SECRET_KEY = "fallback_secret_key"
                self.ALGORITHM = "HS256"
                self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
                self.OPENAI_API_KEY = ""
                self.DEEPGRAM_API_KEY = ""
                self.GOOGLE_API_KEY = ""

    def _validate_settings(self):
        """Validate critical settings and log warnings for missing values."""
        try:
            if not self.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not set. AI features will be limited.")
            
            if not self.DEEPGRAM_API_KEY:
                logger.warning("DEEPGRAM_API_KEY not set. Voice features will be limited.")
            
            if not self.GOOGLE_API_KEY:
                logger.warning("GOOGLE_API_KEY not set. Some integrations may not work.")
            
            if self.SECRET_KEY == "a_very_secret_key_that_you_should_change":
                logger.warning("Using default SECRET_KEY. Please change this in production.")
                
        except Exception as e:
            logger.error(f"Error validating settings: {e}")

    def get_openai_api_key(self) -> str:
        """Get OpenAI API key with fallback to environment variable."""
        try:
            # Try multiple possible environment variable names
            openai_key = (
                self.OPENAI_API_KEY or 
                os.getenv('OPENAI_API_KEY') or 
                os.getenv('open_ai_openai_api_key') or  # Handle the underscore version
                os.getenv('OPEN_AI_OPENAI_API_KEY') or  # Handle uppercase version
                ''
            )
            return openai_key
        except Exception as e:
            logger.error(f"Error getting OpenAI API key: {e}")
            return ''

settings = Settings()