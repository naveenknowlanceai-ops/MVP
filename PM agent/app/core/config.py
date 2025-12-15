import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "PM agent"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"

    # --- Google Cloud & AI ---
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1" # Required for Vertex AI
    GOOGLE_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # --- Models ---
    # We use Gemini 1.5 Pro for complex reasoning (The Manager)
    MODEL_NAME: str = "gemini-1.5-pro-preview-0409" 
    # We use Gecko or Text-Embedding-004 for efficient cloud embeddings
    EMBEDDING_MODEL_NAME: str = "text-embedding-004" 

    # --- Data Persistence ---
    # Path to where we store the RAG vectors (The Brain)
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    # Path to the SQL database (The Project Metadata)
    SQLITE_URL: str = "sqlite+aiosqlite:///./data/pm_agent.db"

    class Config:
        env_file = ".env"
        extra = "ignore" # Allows you to have extra keys in .env without crashing

settings = Settings()