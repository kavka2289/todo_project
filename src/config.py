from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://todo_user:todo_password@localhost:5432/todo_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_ttl: int = 3600  # TTL по умолчанию в секундах
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Todo App"
    project_version: str = "1.0.0"
    
    # CORS
    allowed_hosts: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Cache
    cache_enabled: bool = True
    cache_default_ttl: int = 300  # 5 минут
    
    # File upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["jpg", "jpeg", "png", "gif", "pdf"]
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


# Создаем экземпляр настроек
settings = Settings()

# Автоматическое определение окружения
if os.getenv("ENVIRONMENT"):
    settings.environment = os.getenv("ENVIRONMENT")
    settings.debug = settings.environment == "development"
