from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, case_sensitive=False)

    environment: str = "local"
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres_db:5432/yakhteh"

    # JWT validation for protected endpoints
    secret_key: str = "change_me_in_prod"
    algorithm: str = "HS256"
    
    my_domain: str = "localhost"  # Domain for CORS and routing


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

