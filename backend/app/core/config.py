from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.
    Uses environment variables when available, with sensible defaults.
    """
    
    # Application
    APP_NAME: str = "ResumeForge"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Processing
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".txt"}
    UPLOAD_DIR: str = "temp_uploads"
    
    # ML Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    GENERATION_MODEL: str = "google/flan-t5-base"
    SPACY_MODEL: str = "en_core_web_sm"
    
    # Processing
    MAX_RESUME_LENGTH: int = 10000  # characters
    MIN_RESUME_LENGTH: int = 100
    
    # Privacy
    DATA_RETENTION_DAYS: int = 0  # 0 means no retention
    ENABLE_LOGGING: bool = False  # Privacy-first default
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()