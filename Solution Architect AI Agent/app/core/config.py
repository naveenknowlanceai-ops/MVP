import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Solution Architect AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Google Cloud Config
    GOOGLE_CLOUD_PROJECT: str = "knowlance-ai"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # Credentials (Optional if using ADC, but good to have)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Model Config
    MODEL_NAME: str = "gemini-2.5-pro"
    EMBEDDING_MODEL_NAME: str = "text-embedding-004"

    # Persistence Paths
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    class Config:
        env_file = ".env"
        extra = "ignore" 
        case_sensitive = True

settings = Settings()

# Force Credentials into Environment for Google Library
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"[CONFIG] Loaded Credentials: {settings.GOOGLE_APPLICATION_CREDENTIALS}")