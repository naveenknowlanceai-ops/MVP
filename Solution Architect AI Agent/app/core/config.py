import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Solution Architect AI Agent"
    API_V1_STR: str = "/api/v1"
    GOOGLE_CLOUD_PROJECT: str
    LOCATION: str = "us-central1"

    # Explicitly define the fields that were causing errors
    GOOGLE_APPLICATION_CREDENTIALS: str
    ENV: str = "development"
    
    # Optional fields (These might exist in your .env, so we define them to avoid errors)
    GOOGLE_API_KEY: Optional[str] = None
    MODEL: Optional[str] = None

    # Configuration to handle .env file and ignore other random variables
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",       # Critical: Ignores unknown vars instead of crashing
        case_sensitive=False  # Handles 'env' vs 'ENV'
    )

settings = Settings()

# SYSTEM HOOK: 
# The Google Auth library looks for 'GOOGLE_APPLICATION_CREDENTIALS' in the OS Environment.
# We manually inject it here to ensure the library picks up your specific JSON key.
if settings.GOOGLE_APPLICATION_CREDENTIALS:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"🔑 Loaded Credentials: {settings.GOOGLE_APPLICATION_CREDENTIALS}")