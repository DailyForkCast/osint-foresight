"""Configuration loader for environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env.local if it exists
env_path = Path(__file__).resolve().parents[2] / ".env.local"
if env_path.exists():
    load_dotenv(env_path)

def get_env(key: str, default: str = None) -> str:
    """Get environment variable with optional default."""
    return os.environ.get(key, default)