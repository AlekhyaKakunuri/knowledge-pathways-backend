from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    PROJECT_NAME: str = "Knowledge Pathways Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase Configuration
    SUPABASE_URL: str = "https://iifkfohsiprfkcupjtyh.supabase.co"
    SUPABASE_ANON_KEY: str = "your-supabase-anon-key-here"
    SUPABASE_SERVICE_ROLE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpZmtmb2hzaXByZmtjdXBqdHloIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjU1MjM2MywiZXhwIjoyMDcyMTI4MzYzfQ.dJW55DmmkF7UDXfpMlSoSkcC5qER6aK7AUjYvIUf_m0"
    SUPABASE_DB_PASSWORD: str = "Alekhya@123"
    
    # Database Configuration - Constructed from Supabase config
    def get_database_url(self) -> str:
        """Construct database URL from Supabase configuration"""
        # Extract host from SUPABASE_URL
        host = self.SUPABASE_URL.replace("https://", "").replace("http://", "")
        # Use asyncpg driver for async operations
        return f"postgresql+asyncpg://postgres:{self.SUPABASE_DB_PASSWORD}@db.{host}:5432/postgres"
    
    # Use Supabase instead of local database
    USE_SUPABASE: bool = True
    
    # Security Configuration
    SECRET_KEY: str = "your-super-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Email Configuration (Optional - not needed for Supabase connection test)
    SMTP_TLS: Optional[bool] = None
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_ATTEMPT_LIMIT: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15
    
    # Payment Integration
    STRIPE_SECRET_KEY: str = "sk_test_your_stripe_secret_key"
    STRIPE_PUBLISHABLE_KEY: str = "pk_test_your_stripe_publishable_key"
    STRIPE_WEBHOOK_SECRET: str = "whsec_your_webhook_secret"
    RAZORPAY_KEY_ID: str = "your_razorpay_key_id"
    RAZORPAY_KEY_SECRET: str = "your_razorpay_key_secret"
    
    # File Upload
    UPLOAD_DIR: str = "uploads/"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]
    ALLOWED_EXTENSIONS: str = '["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]'
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
