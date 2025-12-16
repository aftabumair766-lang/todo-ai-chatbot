"""
Application Configuration

Uses Pydantic Settings for environment variable management.
Constitution Compliance: Principle IV (Security - secrets in environment variables)
"""

import logging
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Constitution Compliance:
    - Principle IV: Security First (all secrets from env vars)
    - No hardcoded credentials or API keys
    """

    # Database Configuration
    DATABASE_URL: str

    # OpenAI API Configuration
    OPENAI_API_KEY: str
    CHATKIT_WORKFLOW_ID: str = ""  # Optional: Set this after creating workflow in OpenAI platform

    # Better Auth Configuration
    BETTER_AUTH_SECRET: str
    BETTER_AUTH_ISSUER: str

    # Redis Configuration (for rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Application Configuration
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into list"""
        return [origin.strip() for origin in v.split(",")]

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# ============================================================================
# Structured Logging Configuration
# ============================================================================

def setup_logging() -> None:
    """
    Configure structured logging for the application.

    Constitution Compliance:
    - Principle V: Observability (structured logs for debugging)
    - JSON format for production, human-readable for development
    """
    settings = get_settings()

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            if settings.ENVIRONMENT == "development"
            else '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set third-party library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING
    )


# Initialize logging on module import
setup_logging()
