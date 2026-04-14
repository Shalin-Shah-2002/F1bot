import secrets

from fastapi import HTTPException, Request, Response

from app.core.config import Settings
from app.core.constants import ERROR_CSRF_TOKEN_INVALID

ACCESS_TOKEN_COOKIE_NAME = "f1bot_access_token"
CSRF_TOKEN_COOKIE_NAME = "f1bot_csrf_token"
USER_EMAIL_COOKIE_NAME = "f1bot_user_email"
CSRF_HEADER_NAME = "X-CSRF-Token"
AUTH_COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24


def _use_secure_cookies(app_env: str) -> bool:
    return app_env.lower() in {"production", "prod", "staging", "stage"}


def set_auth_cookies(response: Response, *, access_token: str, email: str, settings: Settings) -> None:
    secure = _use_secure_cookies(settings.app_env)
    csrf_token = secrets.token_urlsafe(32)

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE_NAME,
        value=csrf_token,
        max_age=AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=False,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        key=USER_EMAIL_COOKIE_NAME,
        value=email,
        max_age=AUTH_COOKIE_MAX_AGE_SECONDS,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )


def clear_auth_cookies(response: Response, *, settings: Settings) -> None:
    secure = _use_secure_cookies(settings.app_env)

    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME, path="/", secure=secure, samesite="lax")
    response.delete_cookie(key=CSRF_TOKEN_COOKIE_NAME, path="/", secure=secure, samesite="lax")
    response.delete_cookie(key=USER_EMAIL_COOKIE_NAME, path="/", secure=secure, samesite="lax")


def get_access_token_from_request(request: Request) -> str | None:
    token = (request.cookies.get(ACCESS_TOKEN_COOKIE_NAME) or "").strip()
    return token or None


def enforce_csrf_protection(request: Request) -> None:
    csrf_cookie = (request.cookies.get(CSRF_TOKEN_COOKIE_NAME) or "").strip()
    csrf_header = (request.headers.get(CSRF_HEADER_NAME) or "").strip()

    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(status_code=403, detail=ERROR_CSRF_TOKEN_INVALID)
