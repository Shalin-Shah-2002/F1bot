from fastapi import APIRouter, Depends

from app.api.dependencies import get_authenticated_user_id
from app.core.config import get_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("")
async def get_runtime_settings(_: str = Depends(get_authenticated_user_id)) -> dict[str, bool | str]:
    settings = get_settings()
    supabase_configured = bool(settings.supabase_url and settings.supabase_service_role_key)
    return {
        "environment": settings.app_env,
        "gemini_configured": bool(settings.gemini_api_key),
        "reddit_configured": bool(settings.reddit_client_id and settings.reddit_client_secret),
        "supabase_configured": supabase_configured,
        "supabase_auth_enabled": settings.use_supabase_auth() and supabase_configured,
    }
