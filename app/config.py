"""Application configuration settings"""
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file


class Settings:
    """Application settings"""
    DB_URL = os.getenv(
        "DB_URL", "postgresql+asyncpg://user:password@db/trump_db")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    TOKEN_LIFETIME = int(os.getenv("TOKEN_LIFETIME", "3600"))  # 1 hour
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


settings = Settings()
