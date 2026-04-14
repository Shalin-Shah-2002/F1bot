from functools import lru_cache
from typing import Annotated, Literal

from app.core.constants import (
    DEFAULT_AUTH_LOCKOUT_BASE_SECONDS,
    DEFAULT_AUTH_LOCKOUT_MAX_SECONDS,
    DEFAULT_AUTH_LOCKOUT_THRESHOLD,
    DEFAULT_AUTH_RATE_LIMIT_PER_IDENTITY,
    DEFAULT_AUTH_RATE_LIMIT_PER_IP,
    DEFAULT_AUTH_RATE_LIMIT_WINDOW_SECONDS,
    DEFAULT_APP_ENV,
    DEFAULT_APP_NAME,
    DEFAULT_FRONTEND_ORIGIN,
    DEFAULT_GEMINI_MODEL_LITE,
    DEFAULT_RATE_LIMIT_STORE,
    DEFAULT_REDIS_KEY_PREFIX,
    DEFAULT_REDDIT_USER_AGENT,
    DEFAULT_SCAN_DAILY_QUOTA,
    DEFAULT_SCAN_RATE_LIMIT_PER_MINUTE,
    DEFAULT_SCAN_RATE_LIMIT_WINDOW_SECONDS,
    ENV_SCAN_DAILY_QUOTA,
    ENV_SCAN_RATE_LIMIT_PER_MINUTE,
    ENV_SCAN_RATE_LIMIT_WINDOW_SECONDS,
    ENV_AUTH_LOCKOUT_BASE_SECONDS,
    ENV_AUTH_LOCKOUT_MAX_SECONDS,
    ENV_AUTH_LOCKOUT_THRESHOLD,
    ENV_AUTH_RATE_LIMIT_PER_IDENTITY,
    ENV_AUTH_RATE_LIMIT_PER_IP,
    ENV_AUTH_RATE_LIMIT_WINDOW_SECONDS,
    ENV_RATE_LIMIT_STORE,
    ENV_REDIS_KEY_PREFIX,
    ENV_REDIS_URL,
    ENV_TRUSTED_PROXY_CIDRS,
    ENV_SUPABASE_ANON_KEY,
    ENV_SUPABASE_URL,
    ENV_SUPABASE_SERVICE_ROLE_KEY,
    ENV_APP_ENV,
    ENV_APP_NAME,
    ENV_FILE_PATH,
    ENV_FRONTEND_ORIGIN,
    ENV_GEMINI_API_KEY,
    ENV_GEMINI_MODEL_LITE,
    ENV_GEMINI_MODEL_MAIN,
    ENV_LOCAL_AUTH_FALLBACK_ENABLED,
    ENV_REDDIT_CLIENT_ID,
    ENV_REDDIT_CLIENT_SECRET,
    ENV_REDDIT_USER_AGENT,
    ENV_SUPABASE_AUTH_ENABLED,
    ERROR_AUTH_CONFIGURATION,
    SUPABASE_AUTH_DISABLED_ENVS,
)
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_env_string_list(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []

    raw_items = [value] if isinstance(value, str) else [str(item) for item in value]

    normalized: list[str] = []
    for raw in raw_items:
        for part in str(raw).split(","):
            item = part.strip()
            if item:
                normalized.append(item)

    return normalized


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
    supabase_anon_key: Annotated[str | None, Field(validation_alias=ENV_SUPABASE_ANON_KEY)] = None
    supabase_service_role_key: Annotated[str | None, Field(validation_alias=ENV_SUPABASE_SERVICE_ROLE_KEY)] = None
    supabase_auth_enabled: Annotated[bool | None, Field(validation_alias=ENV_SUPABASE_AUTH_ENABLED)] = None
    local_auth_fallback_enabled: Annotated[
        bool,
        Field(validation_alias=ENV_LOCAL_AUTH_FALLBACK_ENABLED),
    ] = False

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

    auth_rate_limit_per_ip: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_RATE_LIMIT_PER_IP, ge=1, le=1000),
    ] = DEFAULT_AUTH_RATE_LIMIT_PER_IP
    auth_rate_limit_per_identity: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_RATE_LIMIT_PER_IDENTITY, ge=1, le=500),
    ] = DEFAULT_AUTH_RATE_LIMIT_PER_IDENTITY
    auth_rate_limit_window_seconds: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_RATE_LIMIT_WINDOW_SECONDS, ge=1, le=3600),
    ] = DEFAULT_AUTH_RATE_LIMIT_WINDOW_SECONDS
    auth_lockout_threshold: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_LOCKOUT_THRESHOLD, ge=1, le=50),
    ] = DEFAULT_AUTH_LOCKOUT_THRESHOLD
    auth_lockout_base_seconds: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_LOCKOUT_BASE_SECONDS, ge=1, le=3600),
    ] = DEFAULT_AUTH_LOCKOUT_BASE_SECONDS
    auth_lockout_max_seconds: Annotated[
        int,
        Field(validation_alias=ENV_AUTH_LOCKOUT_MAX_SECONDS, ge=1, le=86400),
    ] = DEFAULT_AUTH_LOCKOUT_MAX_SECONDS
    rate_limit_store: Annotated[
        Literal["memory", "redis"],
        Field(validation_alias=ENV_RATE_LIMIT_STORE),
    ] = DEFAULT_RATE_LIMIT_STORE
    redis_url: Annotated[str | None, Field(validation_alias=ENV_REDIS_URL)] = None
    redis_key_prefix: Annotated[
        str,
        Field(validation_alias=ENV_REDIS_KEY_PREFIX, min_length=1),
    ] = DEFAULT_REDIS_KEY_PREFIX
    trusted_proxy_cidrs: Annotated[
        list[str],
        Field(validation_alias=ENV_TRUSTED_PROXY_CIDRS),
    ] = Field(default_factory=list)

    @field_validator("trusted_proxy_cidrs", mode="before")
    @classmethod
    def normalize_trusted_proxy_cidrs(cls, value: list[str] | str | None) -> list[str]:
        return _normalize_env_string_list(value)

    def is_local_environment(self) -> bool:
        return self.app_env.lower() in SUPABASE_AUTH_DISABLED_ENVS

    def use_supabase_auth(self) -> bool:
        if self.supabase_auth_enabled is not None:
            return self.supabase_auth_enabled

        # Fail closed by default. Local/demo fallback requires explicit opt-in.
        if self.local_auth_fallback_enabled and self.is_local_environment():
            return False

        return True

    def validate_auth_configuration(self) -> None:
        if self.use_supabase_auth():
            missing_keys: list[str] = []
            if not self.supabase_url:
                missing_keys.append(ENV_SUPABASE_URL)
            if not self.supabase_anon_key:
                missing_keys.append(ENV_SUPABASE_ANON_KEY)
            if missing_keys:
                missing = ", ".join(missing_keys)
                raise RuntimeError(f"{ERROR_AUTH_CONFIGURATION} Missing: {missing}")
            return

        if not self.is_local_environment():
            raise RuntimeError(
                "Supabase auth must be enabled outside local/dev/test environments. "
                "Set SUPABASE_AUTH_ENABLED=true."
            )

        if not self.local_auth_fallback_enabled:
            raise RuntimeError(
                "Local/demo auth fallback is disabled. "
                "Set LOCAL_AUTH_FALLBACK_ENABLED=true only for local/dev/test usage."
            )

    def validate_rate_limit_configuration(self) -> None:
        if self.rate_limit_store == "redis" and not self.redis_url:
            raise RuntimeError(
                "RATE_LIMIT_STORE is set to redis but REDIS_URL is missing. "
                "Set REDIS_URL or choose RATE_LIMIT_STORE=memory for local/dev/test only."
            )

        if self.rate_limit_store == "memory" and not self.is_local_environment():
            raise RuntimeError(
                "In-memory rate limiting is disabled outside local/dev/test environments. "
                "Set RATE_LIMIT_STORE=redis."
            )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
