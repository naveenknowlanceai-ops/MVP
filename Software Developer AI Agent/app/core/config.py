import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # These match your .env file keys exactly
    PROJECT_NAME: str = "Software Developer AI Agent"
    ENV: str = "development"
    
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    
    # Sandbox Settings
    SANDBOX_PATH: str = "./workspace_sandbox"
    SAFE_MODE: bool = True
    
    # Internal Setting (Not in .env, but defaults to False)
    ALLOW_SHELL_EXECUTION: bool = False

    # This creates the absolute path for the OS to understand
    @property
    def ABS_SANDBOX_PATH(self) -> str:
        return os.path.abspath(self.SANDBOX_PATH)

    # Configuration to handle the .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Critical: Ignores unknown vars instead of crashing
    )

settings = Settings()

# Ensure sandbox exists on startup
os.makedirs(settings.ABS_SANDBOX_PATH, exist_ok=True)