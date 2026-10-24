import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root if it exists
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LUNA_CEO_MODEL: str = os.getenv("LUNA_CEO_MODEL", "gpt-4o")
    LUNA_WORKER_MODEL: str = os.getenv("LUNA_WORKER_MODEL", "gpt-4o-mini")
    
    # Integrations
    HOME_ASSISTANT_URL: str = os.getenv("HOME_ASSISTANT_URL", "http://homeassistant.local:8123")
    HOME_ASSISTANT_TOKEN: str = os.getenv("HOME_ASSISTANT_TOKEN", "")
    
    GITHUB_ACCESS_TOKEN: str = os.getenv("GITHUB_ACCESS_TOKEN", "")
    LINEAR_API_KEY: str = os.getenv("LINEAR_API_KEY", "")
    
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")

settings = Settings()
