from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "F1bot API"
    app_env: str = "development"
    frontend_origin: str = "http://localhost:3000"

    gemini_api_key: str | None = None
    gemini_model_lite: str = "gemini-2.5-flash-lite"
    gemini_model_main: str = "gemini-2.5-flash"

    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "f1bot-local"

    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_auth_enabled: bool | None = None

    def use_supabase_auth(self) -> bool:
        if self.supabase_auth_enabled is not None:
            return self.supabase_auth_enabled

        return self.app_env.lower() not in {"development", "dev", "local", "test"}

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
