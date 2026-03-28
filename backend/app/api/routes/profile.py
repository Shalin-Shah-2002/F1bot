from fastapi import APIRouter, Depends

from app.api.dependencies import get_authenticated_user_id
from app.controllers.profile_controller import ProfileController
from app.core.supabase_client import get_supabase_client
from app.models.schemas import BusinessProfile, BusinessProfileUpsertRequest
from app.repositories.profile_repository import ProfileRepository

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _build_controller() -> ProfileController:
    repository = ProfileRepository(client=get_supabase_client())
    return ProfileController(repository=repository)


@router.get("", response_model=BusinessProfile)
async def get_profile(current_user_id: str = Depends(get_authenticated_user_id)) -> BusinessProfile:
    controller = _build_controller()
    return controller.get_or_create_profile(user_id=current_user_id)


@router.put("", response_model=BusinessProfile)
async def upsert_profile(
    payload: BusinessProfileUpsertRequest,
    current_user_id: str = Depends(get_authenticated_user_id),
) -> BusinessProfile:
    controller = _build_controller()
    return controller.upsert_profile(user_id=current_user_id, payload=payload)
