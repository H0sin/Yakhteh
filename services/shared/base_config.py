"""Base configuration for all services."""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """Base settings class for all services."""
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True, 
        case_sensitive=False
    )

    # Environment
    environment: str = "local"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres_db:5432/yakhteh"
    
    # Redis
    redis_url: str = "redis://redis_cache:6379/0"
    
    # Domain configuration
    my_domain: str = "localhost"
    
    # CORS configuration
    cors_origins: List[str] = ["http://localhost:3000"]
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on domain configuration."""
        origins = self.cors_origins.copy()
        if self.my_domain != "localhost":
            origins.append(f"https://frontend.{self.my_domain}")
        return origins