from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.supabase_client import get_supabase_client


bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth", bearerFormat="JWT")


def _extract_local_user_id(token: str) -> str:
    prefix = "demo-token-"
    if not token.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid local access token")

    user_id = token[len(prefix):].strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid local access token")

    return user_id


async def get_authenticated_user_id(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(status_code=401, detail="Missing Authorization bearer token")

    token = credentials.credentials.strip()
    settings = get_settings()

    if not settings.use_supabase_auth():
        # Local/dev mode maps fallback token to a stable local user id.
        return _extract_local_user_id(token)

    has_supabase_config = bool(settings.supabase_url and settings.supabase_service_role_key)
    if not has_supabase_config:
        raise HTTPException(
            status_code=500,
            detail="Supabase auth is enabled but SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY are missing",
        )

    client = get_supabase_client()
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="Supabase auth client failed to initialize",
        )

    try:
        user_response = client.auth.get_user(token)
        user = getattr(user_response, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")

        user_id = str(getattr(user, "id", "")).strip()
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {error}") from error

    return user_id


async def require_authenticated_request(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    return await get_authenticated_user_id(credentials)