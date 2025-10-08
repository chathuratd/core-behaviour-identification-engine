from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "behavior_db"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
