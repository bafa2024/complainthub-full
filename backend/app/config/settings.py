from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Complaint Management"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str = "sqlite:///./voicebot.db"

    SECRET_KEY: str = "a_very_secret_key_that_you_should_change"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    OPENAI_API_KEY: str = ""
    DEEPGRAM_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()