"""Feasify configuration management using environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./feasify.db")
    
    # MCGM/DP Scraper
    MCGM_BASE_URL: str = os.getenv("MCGM_BASE_URL", "https://ptaxportal.mcgm.gov.in")
    DP_BASE_URL: str = os.getenv("DP_BASE_URL", "https://udri.mcgm.gov.in")
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
    
    # PWD Rates
    PWD_RATES_URL: str = os.getenv("PWD_RATES_URL", "https://pwd.maharashtra.gov.in/rates")
    
    # Cache
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", "data/processed/cache"))
    
    # API
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "true").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = Path(os.getenv("LOG_FILE", "logs/feasify.log"))
    
    def __init__(self):
        # Ensure cache directory exists
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # Ensure log directory exists
        self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

settings = Settings()
