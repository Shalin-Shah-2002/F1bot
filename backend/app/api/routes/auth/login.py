import logging

from fastapi import APIRouter, HTTPException, Request, Response

from app.api.routes.auth.dependencies import get_auth_controller
from app.core.auth_cookies import clear_auth_cookies, set_auth_cookies
from app.core.client_ip import resolve_client_ip
from app.core.config import get_settings
from app.core.scan_limits import enforce_auth_limits, register_auth_failure, register_auth_success
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request, response: Response) -> LoginResponse:
    controller = get_auth_controller()
    identity = payload.email.strip().lower()
    client_ip = resolve_client_ip(request)

    enforce_auth_limits(remote_ip=client_ip, identity=identity)

    try:
        login_response = controller.login(payload)
        settings = get_settings()
        if login_response.access_token.strip():
            set_auth_cookies(
                response,
                access_token=login_response.access_token,
                email=login_response.email,
                settings=settings,
            )
        else:
            clear_auth_cookies(response, settings=settings)

        register_auth_success(identity=identity)
        return login_response
    except HTTPException as error:
        if error.status_code in (400, 401, 403):
            register_auth_failure(remote_ip=client_ip, identity=identity)
            logger.warning("Login failed status=%s ip=%s", error.status_code, client_ip)
        raise
