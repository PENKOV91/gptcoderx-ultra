import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    GITHUB_API_KEY: str = os.getenv("GITHUB_API_KEY", "")
    WEBPILOT_API_KEY: str = os.getenv("WEBPILOT_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
