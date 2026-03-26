from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
