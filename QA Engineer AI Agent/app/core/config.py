from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Basic Project Info
    PROJECT_NAME: str = "QA Engineer AI Agent"
    API_V1_STR: str = "/api/v1"
    
    # Google Cloud & Authentication (Fixed: Added these fields)
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    ENV: str = "development"
    
    # QA Specific
    HEADLESS_MODE: bool = False
    
    class Config:
        env_file = ".env"
        # This tells Pydantic to ignore any other unknown variables in .env
        # instead of crashing. Important for stability!
        extra = "ignore"

settings = Settings()