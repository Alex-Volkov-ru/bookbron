from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/booking_db"
    
    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Celery
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Media
    MEDIA_DIR: str = "/app/media"
    MAX_IMAGE_SIZE_MB: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

