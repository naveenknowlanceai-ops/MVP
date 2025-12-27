import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "QA Engineer Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google Cloud Config
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"

    # API Key mapping
    GOOGLE_API_KEY: str = Field(..., alias="GOOGLE_AI_STUDIO_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Model Config
    MODEL_NAME: str = "gemini-2.5-pro"
    EMBEDDING_MODEL_NAME: str = "text-embedding-004"

    # Persistence Paths
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # QA Specific Settings
    HEADLESS_MODE: bool = False
    SANDBOX_PATH: str = "./sandbox"
    
    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True

settings = Settings()

# Force Credentials
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"[CONFIG] Loaded Credentials: {settings.GOOGLE_APPLICATION_CREDENTIALS}")