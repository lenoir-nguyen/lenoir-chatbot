"""
Configuration management for the Lenoir Chatbot API.

This module uses Pydantic Settings (v2) to manage environment variables
from the .env file. All sensitive configuration (API keys, URLs) should
be stored in .env and loaded at startup.

Environment Variables (from .env):
- OPENAI_API_KEY: Required. Secret key for OpenAI API access
- DEBUG: Optional. Enable debug mode (default: false)
- FRONTEND_URL: Optional. Frontend origin for CORS (default: http://localhost:3000)
- REDIS_URL: Optional. Redis connection URL (handled separately, not in Settings)

Note: .env is git-ignored and should never be committed.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from .env file.

    Uses Pydantic v2 ConfigDict for configuration (Pydantic v2 syntax, not v1).
    All fields are required unless a default value is provided.

    Attributes:
        OPENAI_API_KEY (str): Secret API key for OpenAI. Must be set in .env
        DEBUG (bool): Enable debug mode for development (default: False)
        FRONTEND_URL (str): Frontend origin for CORS policy (default: http://localhost:3000)
    """

    OPENAI_API_KEY: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    # Pydantic v2 configuration
    # env_file: Load variables from .env file in this directory
    # case_sensitive: Environment variable names are case-sensitive
    model_config = ConfigDict(env_file=".env", case_sensitive=True)


def get_settings():
    """
    Factory function to create and return Settings instance.

    This is called once at module startup to load configuration.
    The Settings object is then used throughout the application
    (e.g., settings.OPENAI_API_KEY for API initialization).

    Returns:
        Settings: Singleton configuration object with all env vars loaded

    Example:
        >>> settings = get_settings()
        >>> api_key = settings.OPENAI_API_KEY
    """
    return Settings()
