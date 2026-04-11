from fastapi import APIRouter, Depends

from app.api.dependencies import get_authenticated_user_id
from app.core.config import get_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_runtime_settings(_: str = Depends(get_authenticated_user_id)) -> dict[str, bool | str | int]:
    settings = get_settings()
    supabase_configured = bool(settings.supabase_url and settings.supabase_anon_key)
    return {
        "environment": settings.app_env,
        "gemini_configured": bool(settings.gemini_api_key),
        "reddit_configured": bool(settings.reddit_client_id and settings.reddit_client_secret),
        "supabase_configured": supabase_configured,
        "supabase_auth_enabled": settings.use_supabase_auth(),
        "scan_rate_limit_per_minute": settings.scan_rate_limit_per_minute,
        "scan_rate_limit_window_seconds": settings.scan_rate_limit_window_seconds,
        "scan_daily_quota": settings.scan_daily_quota,
    }
