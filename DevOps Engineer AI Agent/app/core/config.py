import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "DevOps Engineer Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- Google Cloud Config ---
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # --- Auth ---
    # Adapts to both API Key or Service Account logic
    GOOGLE_API_KEY: Optional[str] = Field(None, alias="GOOGLE_AI_STUDIO_API_KEY")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # --- Models ---
    # Using the powerful reasoning model for Architecture
    MODEL_NAME: str = "gemini-2.5-pro"
    # Using cloud embeddings to match your stable PM setup
    EMBEDDING_MODEL_NAME: str = "text-embedding-004"

    # --- Persistence ---
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # --- Feature Flags ---
    COWORKING_MODE: bool = True # Intercept enabled

    class Config:
        env_file = ".env"
        extra = "ignore" 
        case_sensitive = True

settings = Settings()

# Force Credentials into OS Environment for the Google Libraries to find them automatically
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"[CONFIG] Loaded Service Account: {settings.GOOGLE_APPLICATION_CREDENTIALS}")