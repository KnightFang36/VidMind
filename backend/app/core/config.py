import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent

# Prefer the backend-level .env, fall back to project root.
load_dotenv(PROJECT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)


class Settings:
    app_name: str = "VidMind API"
    api_prefix: str = "/api"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "llama-3.3-70b-versatile"

    @property
    def groq_api_key(self) -> str:
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. "
                "Copy backend/.env.example to backend/.env and fill in your key."
            )
        return key


@lru_cache
def get_settings() -> Settings:
    return Settings()