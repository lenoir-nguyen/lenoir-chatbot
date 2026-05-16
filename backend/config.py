from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

def get_settings():
    return Settings()
