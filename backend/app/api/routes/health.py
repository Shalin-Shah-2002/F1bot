from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check() -> dict[str, object]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.app_env,
        "gemini_configured": bool(settings.gemini_api_key),
        "reddit_configured": bool(settings.reddit_client_id and settings.reddit_client_secret)
    }
