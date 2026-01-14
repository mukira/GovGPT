"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = ""
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    YOUTUBE_API_KEY: str = ""
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Upload
    MAX_UPLOAD_SIZE: int = 52428800
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: str = "pdf,xlsx,xls,csv,docx,doc"
    TEMP_DIR: str = "./temp"
    
    # AI/ML
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "llama3-70b-8192"
    LLM_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 8192
    
    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 5
    HYBRID_SEARCH_ALPHA: float = 0.5
    
    # Database
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # News
    NEWS_LOOKBACK_DAYS: int = 30
    NEWS_MAX_RESULTS: int = 100
    GDELT_ENABLED: bool = True
    GDELT_LOOKBACK_DAYS: int = 1000
    
    # Sentiment
    SENTIMENT_BATCH_SIZE: int = 32
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Google Drive
    GOOGLE_DRIVE_CREDENTIALS_PATH: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = "11wQnLCSqcS9SoVri5tqTTY6tA45JvDt3"  # User's folder
    
    # Security
    SECRET_KEY: str = "change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore any extra env variables

settings = Settings()

