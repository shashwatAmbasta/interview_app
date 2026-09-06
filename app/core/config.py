from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Sift AI Interview")
    environment: str = os.getenv("ENVIRONMENT", "development")
    jwt_secret: str = os.getenv("JWT_SECRET", "local-development-secret")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", str(60 * 60 * 8)))
    database_path: Path = Path(os.getenv("DATABASE_PATH", str(ROOT_DIR / "data" / "interview.db")))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    cookie_name: str = "sift_session"
    cookie_secure: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    max_upload_bytes: int = 12 * 1024 * 1024


settings = Settings()
