from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent

# Prefer the new backend location, while keeping existing root setups working.
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)


class Settings:
    app_name = "VidMind API"
    api_prefix = "/api"
    embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model = "llama-3.3-70b-versatile"


@lru_cache
def get_settings() -> Settings:
    return Settings()
