import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Software Developer Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Google Cloud Config
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    
    # Credentials (Using your .env setup)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Brain Config
    MODEL_NAME: str = "gemini-2.5-pro"
    
    # Developer Specific Config
    # This is where the agent "lives"
    SANDBOX_PATH: str = "./workspace_sandbox" 
    
    @property
    def ABS_SANDBOX_PATH(self) -> str:
        return os.path.abspath(self.SANDBOX_PATH)

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True

settings = Settings()

# Force load creds if present
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"[CONFIG] Loaded Credentials from: {settings.GOOGLE_APPLICATION_CREDENTIALS}")

# Create sandbox if missing
if not os.path.exists(settings.ABS_SANDBOX_PATH):
    os.makedirs(settings.ABS_SANDBOX_PATH)