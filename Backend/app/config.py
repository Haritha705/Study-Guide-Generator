from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyPack AI"
    ANTHROPIC_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    VECTOR_STORE_PROVIDER: str = "memory"
    
    class Config:
        env_file = ".env"

settings = Settings()
