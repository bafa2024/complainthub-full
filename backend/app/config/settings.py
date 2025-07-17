import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import traceback
from typing import List

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
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_PROJECT_ID: str = ""
    
    # Translation Configuration
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar"]
    AUTO_TRANSLATE_ENABLED: bool = True
    TRANSLATION_CACHE_ENABLED: bool = True

    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    
    # Telephony Provider Configuration
    KNOWLARITY_API_KEY: str = ""
    KNOWLARITY_BASE_URL: str = "https://api.knowlarity.com/v1"
    KNOWLARITY_FROM_NUMBER: str = ""
    
    # Exotel Configuration
    EXOTEL_SID: str = ""
    EXOTEL_TOKEN: str = ""
    EXOTEL_BASE_URL: str = "https://api.exotel.com/v1"
    EXOTEL_FROM_NUMBER: str = ""
    
    # Base URL for webhooks
    BASE_URL: str = "http://localhost:8000"
    
    # Support phone number for voice call transfers
    SUPPORT_PHONE_NUMBER: str = "+1234567890"
    
    # Phone Number Configuration
    DEFAULT_COUNTRY_CODE: str = "IN"
    DEFAULT_NUMBER_TYPE: str = "toll-free"
    AUTO_APPROVE_NUMBER_REQUESTS: bool = False
    MAX_PHONE_NUMBERS_PER_BRAND: int = 10
    
    # WhatsApp Business API Configuration
    WHATSAPP_BUSINESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # Facebook Messenger Configuration
    FACEBOOK_PAGE_ACCESS_TOKEN: str = ""
    FACEBOOK_VERIFY_TOKEN: str = ""
    FACEBOOK_APP_SECRET: str = ""
    
    # Instagram Configuration
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_VERIFY_TOKEN: str = ""
    
    # LinkedIn Configuration
    LINKEDIN_ACCESS_TOKEN: str = ""
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@complainthubbot.com"
    
    # Frontend URL for invitation links
    FRONTEND_URL: str = "http://localhost:3000"
    
    # WebSocket Configuration
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_HOST: str = "0.0.0.0"
    WEBSOCKET_PORT: int = 8001
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list = ["image/*", "video/*", "audio/*", "application/pdf", "text/plain"]
    UPLOAD_DIR: str = "uploads"
    
    # Channel Configuration
    ENABLED_CHANNELS: list = ["whatsapp", "telegram", "facebook", "webchat", "voice", "sms", "instagram", "linkedin"]
    
    # Brand-specific phone number mappings
    BRAND_PHONE_MAPPINGS: dict = {
        "1": "+1234567890",  # Brand 1 phone number
        "2": "+0987654321",  # Brand 2 phone number
    }
    
    # Brand-specific bot token mappings
    BRAND_BOT_MAPPINGS: dict = {
        "1": "bot_token_1",
        "2": "bot_token_2",
    }
    
    # Stripe Payment Configuration
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_BASIC_PLAN_ID: str = ""
    STRIPE_PRO_PLAN_ID: str = ""
    STRIPE_ENTERPRISE_PLAN_ID: str = ""
    
    # Billing Configuration
    COMPLAINT_CHARGE_AMOUNT: float = 50.0
    FREE_RESOLUTION_WINDOW_HOURS: int = 24
    LOW_BALANCE_THRESHOLD: float = 100.0
    CURRENCY: str = "INR"
    
    # Security Configuration
    ALLOWED_HOSTS: list = ["*"]  # Configure for production
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
    IP_WHITELIST: list = ["127.0.0.1", "::1"]  # Admin IPs
    IP_BLACKLIST: list = []
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS: int = 100
    ADMIN_RATE_LIMIT_MAX_REQUESTS: int = 1000
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    CELERY_TASK_ALWAYS_EAGER: bool = False  # Set to True for testing without Redis
    
    # Follow-up Configuration
    FOLLOW_UP_DELAY_HOURS: int = 24
    SECONDARY_FOLLOW_UP_DELAY_HOURS: int = 4
    AUTO_CLOSE_HOURS: int = 48
    MAX_FOLLOW_UP_RETRIES: int = 3
    FOLLOW_UP_RETENTION_DAYS: int = 90

    # Threat Detection
    ENABLE_THREAT_DETECTION: bool = True
    SUSPICIOUS_PATHS: list = ["/admin", "/api/admin", "/wp-admin", "/phpmyadmin"]
    SUSPICIOUS_USER_AGENTS: list = ["sqlmap", "nikto", "nmap", "scanner"]
    MAX_REQUESTS_PER_MINUTE: int = 100
    BLOCK_SUSPICIOUS_IPS: bool = True

    # CRM Integration Configuration
    CRM_WEBHOOK_SECRET: str = ""
    CRM_SYNC_INTERVAL_MINUTES: int = 30
    CRM_MAX_RETRIES: int = 3
    CRM_TIMEOUT_SECONDS: int = 30
    
    # Supported CRM Systems
    SUPPORTED_CRM_SYSTEMS: list = [
        "salesforce", "zoho", "freshworks", "kapture", 
        "leadsquared", "hubspot", "pipedrive"
    ]

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
                self.GOOGLE_APPLICATION_CREDENTIALS = ""
                self.GOOGLE_PROJECT_ID = ""
                self.DEFAULT_LANGUAGE = "en"
                self.SUPPORTED_LANGUAGES = ["en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh", "ar"]
                self.AUTO_TRANSLATE_ENABLED = True
                self.TRANSLATION_CACHE_ENABLED = True

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

# Create settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate that required settings are configured"""
    required_settings = []
    
    # Check if any channels are enabled
    if not settings.ENABLED_CHANNELS:
        required_settings.append("At least one channel must be enabled")
    
    # Check channel-specific requirements
    if "whatsapp" in settings.ENABLED_CHANNELS:
        if not settings.TWILIO_ACCOUNT_SID and not settings.WHATSAPP_BUSINESS_TOKEN:
            required_settings.append("WhatsApp requires either Twilio credentials or WhatsApp Business API token")
    
    if "telegram" in settings.ENABLED_CHANNELS:
        if not settings.TELEGRAM_BOT_TOKEN:
            required_settings.append("Telegram requires bot token")
    
    if "facebook" in settings.ENABLED_CHANNELS:
        if not settings.FACEBOOK_PAGE_ACCESS_TOKEN:
            required_settings.append("Facebook requires page access token")
    
    if "voice" in settings.ENABLED_CHANNELS or "sms" in settings.ENABLED_CHANNELS:
        if not settings.TWILIO_ACCOUNT_SID:
            required_settings.append("Voice/SMS requires Twilio credentials")
    
    if required_settings:
        logger.warning("Configuration issues found:")
        for issue in required_settings:
            logger.warning(f"  - {issue}")
        logger.warning("Some features may not work properly without proper configuration")
    else:
        logger.info("All required settings are configured")

# Validate settings on import
validate_settings()