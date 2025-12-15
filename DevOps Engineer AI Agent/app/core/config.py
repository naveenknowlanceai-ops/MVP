from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Core Identity
    PROJECT_NAME: str = "DevOps Engineer AI Agent"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"

    # Cloud Credentials (The Keys to the Kingdom)
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_REGION: str = "us-central1"

    # Hardware & Logic
    USE_LOCAL_EMBEDDINGS: bool = True
    INTERCEPT_MODE: bool = True  # Coworking Mode Safety Gate
    
    # Pydantic V2 Configuration
    model_config = {
        "env_file": ".env",
        "extra": "ignore" # Creates resilience against undefined env vars
    }

settings = Settings()