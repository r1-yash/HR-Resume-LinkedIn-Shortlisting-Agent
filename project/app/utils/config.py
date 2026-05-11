import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "HR Resume & LinkedIn Shortlisting Agent"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    SAMPLE_DATA_DIR: Path = BASE_DIR / "sample_data"
    OVERRIDES_FILE: Path = DATA_DIR / "overrides.json"
    
    # API Key for endpoints (simple auth)
    API_KEY: str = os.getenv("API_KEY", "default_dev_key")
    
    # Gemini API Key
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Initialize overrides file if it doesn't exist
if not settings.OVERRIDES_FILE.exists():
    import json
    with open(settings.OVERRIDES_FILE, "w") as f:
        json.dump([], f)
