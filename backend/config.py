from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "Plum OPD Claim Adjudication"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # API Keys
    GEMINI_API_KEY: str = ""

    # LLM Configuration
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"  # Fast, 1M context, native vision/OCR
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 8192

    # Database - Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""  # For admin operations

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg"}
    UPLOAD_DIR: str = "./uploads"

    # Policy Configuration
    POLICY_FILE_PATH: str = "../assignment/policy_terms.json"

    # OCR Configuration
    TESSERACT_PATH: str = ""  # Set if tesseract not in PATH

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
