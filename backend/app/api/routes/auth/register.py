from fastapi import APIRouter

from app.api.routes.auth.dependencies import get_auth_controller
from app.models.schemas import RegisterRequest, RegisterResponse

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(payload: RegisterRequest) -> RegisterResponse:
    controller = get_auth_controller()
    return controller.register(payload)
