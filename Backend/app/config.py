
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env files (app/config.py → Backend/.env and parent workspace .env)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
_ROOT_ENV = Path(__file__).resolve().parent.parent.parent / ".env"



class Settings(BaseSettings):
    PROJECT_NAME: str = "Study Guide Generator"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017/"
    DB_NAME: str = "Study"

    # Gemini API
    GEMINI_API_KEY: str = ""

    # Mistral API
    MISTRAL_API_KEY: str = ""

    # External Educational APIs
    YOUTUBE_API_KEY: str = ""
    GOOGLE_BOOKS_API_KEY: str = ""

    # Google Drive MCP Integration
    GOOGLE_DRIVE_MCP_URL: str = "https://drivemcp.googleapis.com/mcp/v1"
    GOOGLE_DRIVE_MCP_TOKEN: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URL: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"

    # LangSmith - Optional
    # LANGCHAIN_TRACING_V2: str = "false"
    # LANGCHAIN_API_KEY: str = ""

    # Vector Store
    VECTOR_STORE_PROVIDER: str = "memory"

    # Load variables from .env (root .env loaded first, Backend/.env overrides if present)
    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), str(_ENV_FILE)),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
