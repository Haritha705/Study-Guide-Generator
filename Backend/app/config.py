
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (app/config.py → Backend/.env)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"



class Settings(BaseSettings):
    PROJECT_NAME: str = "Study Guide Generator"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017/"
    DB_NAME: str = "Study"

    # Gemini API
    GEMINI_API_KEY: str = ""

    # Mistral API
    MISTRAL_API_KEY: str = ""

    # LangSmith - Optional
    # LANGCHAIN_TRACING_V2: str = "false"
    # LANGCHAIN_API_KEY: str = ""

    # Vector Store
    VECTOR_STORE_PROVIDER: str = "memory"

    # Load variables from .env
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
