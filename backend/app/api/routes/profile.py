from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import AuthContext, get_authenticated_context, require_csrf_for_cookie_auth
from app.controllers.profile_controller import ProfileController
from app.core.config import get_settings
from app.core.constants import ERROR_AUTH_CONFIGURATION
from app.core.supabase_client import get_supabase_user_client
from app.models.schemas import BusinessProfile, BusinessProfileUpsertRequest
from app.repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _build_controller(access_token: str) -> ProfileController:
    settings = get_settings()
    client = get_supabase_user_client(access_token)
    if settings.use_supabase_auth() and client is None:
        raise HTTPException(status_code=500, detail=ERROR_AUTH_CONFIGURATION)

    repository = ProfileRepository(client=client)
    return ProfileController(repository=repository)


@router.get("", response_model=BusinessProfile)
async def get_profile(auth_context: AuthContext = Depends(get_authenticated_context)) -> BusinessProfile:
    controller = _build_controller(auth_context.access_token)
    return controller.get_or_create_profile(user_id=auth_context.user_id)


@router.put("", response_model=BusinessProfile, dependencies=[Depends(require_csrf_for_cookie_auth)])
async def upsert_profile(
    payload: BusinessProfileUpsertRequest,
    auth_context: AuthContext = Depends(get_authenticated_context),
) -> BusinessProfile:
    controller = _build_controller(auth_context.access_token)
    return controller.upsert_profile(user_id=auth_context.user_id, payload=payload)
