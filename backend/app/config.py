"""Application configuration using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "AI Manufacturing Dashboard"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./manufacturing.db"

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("sqlite:///"):
            return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        if "postgresql+asyncpg://" in url:
            from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
            parsed = urlparse(url)
            if parsed.query:
                query_params = dict(parse_qsl(parsed.query))
                query_params.pop("sslmode", None)
                query_params.pop("channel_binding", None)
                new_query = urlencode(query_params)
                parsed = parsed._replace(query=new_query)
                return urlunparse(parsed)
        return url

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql://", 1)
        if url.startswith("sqlite+aiosqlite:///"):
            return url.replace("sqlite+aiosqlite:///", "sqlite:///", 1)
        return url

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,https://*.vercel.app"

    # Admin Auth
    ADMIN_SECRET: str = "admin123"
    ADMIN_TOKEN_EXPIRY_HOURS: int = 24

    # Groq API
    GROQ_API_KEY: str = ""

    # ML Model paths
    MODEL_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ml", "models")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
