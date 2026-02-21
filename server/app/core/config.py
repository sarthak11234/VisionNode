"""
Centralized Configuration using Pydantic Settings.

How it works:
  Pydantic Settings reads values from environment variables (or a .env file)
  and validates them at startup. If a required var is missing, the app
  crashes immediately with a clear error — no silent failures at runtime.

Why Pydantic Settings over plain os.environ?
  1. Type validation  — DATABASE_URL must be a string, not missing.
  2. Defaults         — Sensible fallbacks for development.
  3. Autocomplete     — IDE knows every config key.
  Alternative: python-decouple or raw os.getenv() — less type-safe, no validation.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "SheetAgent"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sheetagent"
    )

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ─────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # ── LLM ──────────────────────────────────────────────
    OPENAI_API_KEY: str = ""

    # ── Communication ────────────────────────────────────
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = ""
    RESEND_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
