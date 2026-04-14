import logging
from dataclasses import dataclass

from fastapi import HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth_cookies import (
    USER_EMAIL_COOKIE_NAME,
    enforce_csrf_protection,
    get_access_token_from_request,
)
from app.core.config import get_settings
from app.core.constants import DEMO_TOKEN_PREFIX, ERROR_AUTH_CONFIGURATION, ERROR_TOKEN_INVALID
from app.core.supabase_client import get_supabase_auth_client

logger = logging.getLogger(__name__)


bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuth", bearerFormat="JWT")


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    access_token: str
    email: str | None = None


def _extract_local_user_id(token: str) -> str:
    if not token.startswith(DEMO_TOKEN_PREFIX):
        raise HTTPException(status_code=401, detail="Invalid local access token")

    user_id = token[len(DEMO_TOKEN_PREFIX):].strip()
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid local access token")

    return user_id


async def get_authenticated_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> AuthContext:
    token = credentials.credentials.strip() if credentials and credentials.credentials else ""
    if not token:
        token = get_access_token_from_request(request) or ""

    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication credentials")

    settings = get_settings()

    if not settings.use_supabase_auth():
        # Local/dev mode maps fallback token to a stable local user id.
        email = (request.cookies.get(USER_EMAIL_COOKIE_NAME) or "").strip().lower() or None
        return AuthContext(user_id=_extract_local_user_id(token), access_token=token, email=email)

    has_supabase_config = bool(settings.supabase_url and settings.supabase_anon_key)
    if not has_supabase_config:
        raise HTTPException(status_code=500, detail=ERROR_AUTH_CONFIGURATION)

    client = get_supabase_auth_client()
    if client is None:
        raise HTTPException(status_code=500, detail=ERROR_AUTH_CONFIGURATION)

    try:
        user_response = client.auth.get_user(token)
        user = getattr(user_response, "user", None)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")

        user_id = str(getattr(user, "id", "")).strip()
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")

        email = str(getattr(user, "email", "")).strip().lower() or None
    except HTTPException:
        raise
    except Exception as error:
        logger.warning("Token validation failed: %s", error)
        raise HTTPException(status_code=401, detail=ERROR_TOKEN_INVALID) from error

    return AuthContext(user_id=user_id, access_token=token, email=email)


async def get_authenticated_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    auth_context = await get_authenticated_context(request, credentials)
    return auth_context.user_id


async def require_authenticated_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> str:
    return await get_authenticated_user_id(request, credentials)


async def require_csrf_for_cookie_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> None:
    if request.method.upper() not in {"POST", "PUT", "PATCH", "DELETE"}:
        return

    if credentials is not None and bool(credentials.credentials.strip()):
        return

    if get_access_token_from_request(request) is None:
        return

    enforce_csrf_protection(request)