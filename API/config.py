import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration"""

    # API Configuration
    ROBOFLOW_API_URL: str = "https://detect.roboflow.com"
    ROBOFLOW_API_KEY: str = os.getenv("ROBOFLOW_API_KEY")
    ROBOFLOW_MODEL_ID: str = "the-ultimate-bookshelf-fqvoz/3"

    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

    # Processing Configuration
    BATCH_SIZE: int = 5

    # Gemini Configuration
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TEMPERATURE: float = 0.2
    GEMINI_MAX_OUTPUT_TOKENS: int = 2000

    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Debug Configuration
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SAVE_DEBUG_IMAGES: bool = os.getenv("SAVE_DEBUG_IMAGES", "False").lower() == "true"

settings = Settings()
