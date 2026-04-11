import logging

from fastapi import APIRouter, HTTPException, Request

from app.api.routes.auth.dependencies import get_auth_controller
from app.core.client_ip import resolve_client_ip
from app.core.scan_limits import enforce_auth_limits, register_auth_failure, register_auth_success
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, request: Request) -> LoginResponse:
    controller = get_auth_controller()
    identity = payload.email.strip().lower()
    client_ip = resolve_client_ip(request)

    enforce_auth_limits(remote_ip=client_ip, identity=identity)

    try:
        response = controller.login(payload)
        register_auth_success(identity=identity)
        return response
    except HTTPException as error:
        if error.status_code in (400, 401, 403):
            register_auth_failure(remote_ip=client_ip, identity=identity)
            logger.warning("Login failed status=%s ip=%s", error.status_code, client_ip)
        raise
