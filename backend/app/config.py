import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения
    Загружаются из переменных окружения или .env файла
    """
    # Database
    DATABASE_URL: str = "postgresql://sd_user:sd_pass@db:5432/servicedesk"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost,http://localhost:3000,http://localhost:5173"
    
    # App
    APP_NAME: str = "Service Desk API"
    DEBUG: bool = True
    
    # Omnichannel
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None # e.g. https://your-domain.com/api/webhooks/telegram
    
    # Email (IMAP) - Inbound email parsing
    IMAP_HOST: Optional[str] = None        # e.g. imap.gmail.com
    IMAP_PORT: int = 993
    IMAP_USER: Optional[str] = None        # e.g. support@novumtech.uz
    IMAP_PASSWORD: Optional[str] = None
    IMAP_FOLDER: str = "INBOX"
    IMAP_CHECK_INTERVAL: int = 60          # seconds between checks
    IMAP_USE_SSL: bool = True
    
    # SMTP - Outbound email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None  # e.g. support@novumtech.uz
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_allowed_origins(self) -> list:
        """Преобразовать строку CORS origins в список"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Кешированная функция для получения настроек
    Создаёт экземпляр только один раз
    """
    return Settings()


# Экспортируем для удобства
settings = get_settings()
