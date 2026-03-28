from app.models.schemas import BusinessProfile, BusinessProfileUpsertRequest
from app.repositories.profile_repository import ProfileRepository


class ProfileController:
    DEFAULT_BUSINESS_DESCRIPTION = "Describe your business, audience, and goals here."

    def __init__(self, repository: ProfileRepository) -> None:
        self.repository = repository

    def get_profile(self, user_id: str) -> BusinessProfile | None:
        return self.repository.get_profile(user_id)

    def get_or_create_profile(self, user_id: str) -> BusinessProfile:
        profile = self.repository.get_profile(user_id)
        if profile is not None:
            return profile

        default_profile = BusinessProfile(
            user_id=user_id,
            business_description=self.DEFAULT_BUSINESS_DESCRIPTION,
            keywords=[],
            subreddits=[],
        )
        return self.repository.upsert_profile(default_profile)

    def upsert_profile(self, user_id: str, payload: BusinessProfileUpsertRequest) -> BusinessProfile:
        profile = BusinessProfile(
            user_id=user_id,
            business_description=payload.business_description,
            keywords=payload.keywords,
            subreddits=payload.subreddits,
        )
        return self.repository.upsert_profile(profile)
