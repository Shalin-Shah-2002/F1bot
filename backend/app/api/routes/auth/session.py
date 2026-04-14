from fastapi import APIRouter, Depends

from app.api.dependencies import AuthContext, get_authenticated_context
from app.models.schemas import SessionResponse

router = APIRouter()


@router.get("/session", response_model=SessionResponse)
async def get_session(auth_context: AuthContext = Depends(get_authenticated_context)) -> SessionResponse:
    return SessionResponse(user_id=auth_context.user_id, email=auth_context.email or "")
