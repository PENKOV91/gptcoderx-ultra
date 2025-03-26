import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    GITHUB_API_KEY: str = os.getenv("GITHUB_API_KEY", "")
    WEBPILOT_API_KEY: str = os.getenv("WEBPILOT_API_KEY", "")
    DEFAULT_CONTENT_LIMIT: int = int(os.getenv("DEFAULT_CONTENT_LIMIT", 1000))

    class Config:
        env_file = ".env"

settings = Settings()
