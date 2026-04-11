import logging

from fastapi import HTTPException
from typing import Any

from app.core.config import get_settings
from app.core.constants import (
    DEMO_TOKEN_PREFIX,
    ERROR_AUTH_CONFIGURATION,
    ERROR_LOGIN_FAILED,
    ERROR_REGISTRATION_FAILED,
)
from app.models.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

SupabaseClient = Any
logger = logging.getLogger(__name__)


class AuthController:
    def __init__(self, client: SupabaseClient | None) -> None:
        self.client = client

    def _should_use_supabase(self) -> bool:
        settings = get_settings()
        if not settings.use_supabase_auth():
            return False

        has_supabase_config = bool(settings.supabase_url and settings.supabase_anon_key)
        if not has_supabase_config:
            raise HTTPException(status_code=500, detail=ERROR_AUTH_CONFIGURATION)

        if self.client is None:
            raise HTTPException(
                status_code=500,
                detail=ERROR_AUTH_CONFIGURATION,
            )

        return True

    def login(self, payload: LoginRequest) -> LoginResponse:
        sanitized_email = payload.email.strip().lower()

        if self._should_use_supabase():
            try:
                auth_result = self.client.auth.sign_in_with_password(
                    {"email": sanitized_email, "password": payload.password}
                )
                if not auth_result.user or not auth_result.session:
                    raise HTTPException(status_code=401, detail="Invalid login credentials")

                return LoginResponse(
                    user_id=str(auth_result.user.id),
                    email=sanitized_email,
                    access_token=str(auth_result.session.access_token),
                )
            except HTTPException:
                raise
            except Exception as error:
                status_code = int(getattr(error, "status", 401) or 401)
                logger.warning("Supabase login failed: %s", error)
                raise HTTPException(status_code=status_code, detail=ERROR_LOGIN_FAILED) from error

        # Fallback auth flow for local scaffolding when Supabase is not configured.
        user_id = sanitized_email.replace("@", "-").replace(".", "-")
        token = f"{DEMO_TOKEN_PREFIX}{user_id}"

        return LoginResponse(user_id=user_id, email=sanitized_email, access_token=token)

    def register(self, payload: RegisterRequest) -> RegisterResponse:
        sanitized_email = payload.email.strip().lower()

        if self._should_use_supabase():
            try:
                sign_up_result = self.client.auth.sign_up(
                    {
                        "email": sanitized_email,
                        "password": payload.password,
                        "options": {
                            "data": {"full_name": payload.full_name or ""},
                        },
                    }
                )

                if not sign_up_result.user:
                    raise HTTPException(status_code=400, detail="Unable to create account")

                session = sign_up_result.session
                token = str(session.access_token) if session else ""

                return RegisterResponse(
                    user_id=str(sign_up_result.user.id),
                    email=sanitized_email,
                    access_token=token,
                )
            except HTTPException:
                raise
            except Exception as error:
                status_code = int(getattr(error, "status", 400) or 400)
                logger.warning("Supabase registration failed: %s", error)
                raise HTTPException(status_code=status_code, detail=ERROR_REGISTRATION_FAILED) from error

        # Fallback auth flow for local scaffolding when Supabase is not configured.
        user_id = sanitized_email.replace("@", "-").replace(".", "-")
        token = f"{DEMO_TOKEN_PREFIX}{user_id}"

        return RegisterResponse(user_id=user_id, email=sanitized_email, access_token=token)