from functools import lru_cache
from typing import Any

from app.core.config import get_settings

try:
    from supabase import Client, create_client
except Exception:  # pragma: no cover
    Client = Any  # type: ignore[misc,assignment]
    create_client = None


@lru_cache
def get_supabase_client() -> Client | None:
    settings = get_settings()

    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None

    if create_client is None:
        return None

    try:
        return create_client(settings.supabase_url, settings.supabase_service_role_key)
    except Exception:
        return None
