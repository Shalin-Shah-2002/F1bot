from fastapi import APIRouter

from app.api.routes.auth.dependencies import get_auth_controller
from app.models.schemas import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest) -> LoginResponse:
    controller = get_auth_controller()
    return controller.login(payload)
