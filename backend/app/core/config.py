from functools import lru_cache
from typing import Annotated

from app.core.constants import (
    DEFAULT_APP_ENV,
    DEFAULT_APP_NAME,
    DEFAULT_FRONTEND_ORIGIN,
    DEFAULT_GEMINI_MODEL_LITE,
    DEFAULT_REDDIT_USER_AGENT,
    DEFAULT_SCAN_DAILY_QUOTA,
    DEFAULT_SCAN_RATE_LIMIT_PER_MINUTE,
    DEFAULT_SCAN_RATE_LIMIT_WINDOW_SECONDS,
    ENV_SCAN_DAILY_QUOTA,
    ENV_SCAN_RATE_LIMIT_PER_MINUTE,
    ENV_SCAN_RATE_LIMIT_WINDOW_SECONDS,
    ENV_SUPABASE_URL,
    ENV_SUPABASE_SERVICE_ROLE_KEY,
    ENV_APP_ENV,
    ENV_APP_NAME,
    ENV_FILE_PATH,
    ENV_FRONTEND_ORIGIN,
    ENV_GEMINI_API_KEY,
    ENV_GEMINI_MODEL_LITE,
    ENV_GEMINI_MODEL_MAIN,
    ENV_REDDIT_CLIENT_ID,
    ENV_REDDIT_CLIENT_SECRET,
    ENV_REDDIT_USER_AGENT,
    ENV_SUPABASE_AUTH_ENABLED,
    ERROR_AUTH_CONFIGURATION,
    SUPABASE_AUTH_DISABLED_ENVS,
)
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: Annotated[str, Field(validation_alias=ENV_APP_NAME)] = DEFAULT_APP_NAME
    app_env: Annotated[str, Field(validation_alias=ENV_APP_ENV)] = DEFAULT_APP_ENV
    frontend_origin: Annotated[str, Field(validation_alias=ENV_FRONTEND_ORIGIN)] = DEFAULT_FRONTEND_ORIGIN

    gemini_api_key: Annotated[str | None, Field(validation_alias=ENV_GEMINI_API_KEY)] = None
    gemini_model_lite: Annotated[str, Field(validation_alias=ENV_GEMINI_MODEL_LITE)] = DEFAULT_GEMINI_MODEL_LITE
    gemini_model_main: Annotated[str | None, Field(validation_alias=ENV_GEMINI_MODEL_MAIN)] = None

    reddit_client_id: Annotated[str | None, Field(validation_alias=ENV_REDDIT_CLIENT_ID)] = None
    reddit_client_secret: Annotated[str | None, Field(validation_alias=ENV_REDDIT_CLIENT_SECRET)] = None
    reddit_user_agent: Annotated[str, Field(validation_alias=ENV_REDDIT_USER_AGENT)] = DEFAULT_REDDIT_USER_AGENT

    supabase_url: Annotated[str | None, Field(validation_alias=ENV_SUPABASE_URL)] = None
    supabase_service_role_key: Annotated[str | None, Field(validation_alias=ENV_SUPABASE_SERVICE_ROLE_KEY)] = None
    supabase_auth_enabled: Annotated[bool | None, Field(validation_alias=ENV_SUPABASE_AUTH_ENABLED)] = None

    scan_rate_limit_per_minute: Annotated[
        int,
        Field(validation_alias=ENV_SCAN_RATE_LIMIT_PER_MINUTE, ge=1, le=200),
    ] = DEFAULT_SCAN_RATE_LIMIT_PER_MINUTE
    scan_rate_limit_window_seconds: Annotated[
        int,
        Field(validation_alias=ENV_SCAN_RATE_LIMIT_WINDOW_SECONDS, ge=1, le=3600),
    ] = DEFAULT_SCAN_RATE_LIMIT_WINDOW_SECONDS
    scan_daily_quota: Annotated[
        int,
        Field(validation_alias=ENV_SCAN_DAILY_QUOTA, ge=1, le=10000),
    ] = DEFAULT_SCAN_DAILY_QUOTA

    def use_supabase_auth(self) -> bool:
        if self.supabase_auth_enabled is not None:
            return self.supabase_auth_enabled

        return self.app_env.lower() not in SUPABASE_AUTH_DISABLED_ENVS

    def validate_auth_configuration(self) -> None:
        if self.use_supabase_auth():
            missing_keys: list[str] = []
            if not self.supabase_url:
                missing_keys.append(ENV_SUPABASE_URL)
            if not self.supabase_service_role_key:
                missing_keys.append(ENV_SUPABASE_SERVICE_ROLE_KEY)
            if missing_keys:
                missing = ", ".join(missing_keys)
                raise RuntimeError(f"{ERROR_AUTH_CONFIGURATION} Missing: {missing}")
            return

        if self.app_env.lower() not in SUPABASE_AUTH_DISABLED_ENVS:
            raise RuntimeError(
                "Supabase auth must be enabled outside local/dev/test environments. "
                "Set SUPABASE_AUTH_ENABLED=true."
            )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
