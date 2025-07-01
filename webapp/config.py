"""
Configuration settings for the voice cloning web application
"""

import os
from typing import Optional

def load_env_file(env_file: str = ".env"):
    """Load environment variables from .env file"""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env file if it exists
load_env_file()

class Config:
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "9080"))
    
    # CosyVoice API configuration
    COSYVOICE_API_URL: str = os.getenv("COSYVOICE_API_URL", "http://172.31.26.217:50000")
    
    # Audio configuration
    REFERENCE_AUDIO_DIR: str = os.path.join(os.path.dirname(__file__), "static", "assets", "reference_audios")
    MAX_AUDIO_FILE_SIZE: int = int(os.getenv("MAX_AUDIO_FILE_SIZE", str(50 * 1024 * 1024)))  # 50MB
    SUPPORTED_AUDIO_FORMATS: list = os.getenv("SUPPORTED_AUDIO_FORMATS", ".wav,.mp3,.flac,.m4a").split(",")
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def get_cosyvoice_url(cls) -> str:
        """Get the CosyVoice API URL"""
        return cls.COSYVOICE_API_URL
    
    @classmethod
    def set_cosyvoice_url(cls, url: str) -> None:
        """Set the CosyVoice API URL"""
        cls.COSYVOICE_API_URL = url
        os.environ["COSYVOICE_API_URL"] = url

# Create a global config instance
config = Config()
