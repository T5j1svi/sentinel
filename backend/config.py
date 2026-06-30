"""
SENTINEL Intel — Configuration
Loads environment variables and provides typed settings.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Application settings loaded from environment."""

    # --- Server ---
    HOST: str = os.getenv("SENTINEL_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("SENTINEL_PORT", "8000"))
    DEBUG: bool = os.getenv("SENTINEL_DEBUG", "true").lower() == "true"
    CORS_ORIGINS: list[str] = os.getenv(
        "SENTINEL_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")

    # --- Database ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{PROJECT_ROOT / 'database' / 'sentinel_intel.db'}"
    )

    # --- API Keys (optional — modules degrade gracefully without them) ---
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROK_API_key", "")
    SHODAN_API_KEY: str = os.getenv("SHODAN_API_KEY", "")
    URLSCAN_API_KEY: str = os.getenv("URLSCAN_API_KEY", "")
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    TELEGRAM_API_ID: str = os.getenv("TELEGRAM_API_ID", "")
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")

    # --- Paths ---
    UPLOADS_DIR: Path = PROJECT_ROOT / "uploads"
    EXPORTS_DIR: Path = PROJECT_ROOT / "exports"
    EVIDENCE_DIR: Path = PROJECT_ROOT / "evidence"
    CASES_DIR: Path = PROJECT_ROOT / "cases"

    def __init__(self):
        (PROJECT_ROOT / 'database').mkdir(parents=True, exist_ok=True)
        for d in [self.UPLOADS_DIR, self.EXPORTS_DIR, self.EVIDENCE_DIR, self.CASES_DIR]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
