from functools import lru_cache
from typing import Any

from app.core.config import get_settings

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None


def _create_supabase_client(url: str | None, key: str | None) -> Any | None:
    if not url or not key:
        return None

    if create_client is None:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


@lru_cache
def get_supabase_client() -> Any | None:
    """Backward-compatible alias for admin/service-role client."""
    return get_supabase_admin_client()


@lru_cache
def get_supabase_admin_client() -> Any | None:
    settings = get_settings()
    return _create_supabase_client(settings.supabase_url, settings.supabase_service_role_key)


def get_supabase_auth_client() -> Any | None:
    """Creates a fresh anon-key client for auth/user-scoped operations."""
    settings = get_settings()
    return _create_supabase_client(settings.supabase_url, settings.supabase_anon_key)


def get_supabase_user_client(access_token: str) -> Any | None:
    """Creates a PostgREST client bound to an end-user JWT for RLS enforcement.

    Returns ``None`` immediately when Supabase auth is disabled – demo/dev
    tokens are not JWTs and must never reach PostgREST, which would cause a
    JWT-parse 500 error.
    """
    # Guard: skip all Supabase I/O when auth is running in local/demo mode.
    if not get_settings().use_supabase_auth():
        return None

    token = access_token.strip()
    if not token:
        return None

    client = get_supabase_auth_client()
    if client is None:
        return None

    postgrest_client = getattr(client, "postgrest", None)
    if postgrest_client is None or not hasattr(postgrest_client, "auth"):
        return None

    try:
        postgrest_client.auth(token)
        return client
    except Exception:
        return None
