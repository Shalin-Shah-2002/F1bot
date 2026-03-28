from datetime import datetime, timezone
from typing import Any

from app.models.schemas import BusinessProfile
from app.repositories.memory_store import MEMORY_PROFILES

SupabaseClient = Any


class ProfileRepository: 
    def __init__(self, client: SupabaseClient | None) -> None:
        self.client = client

    def get_profile(self, user_id: str) -> BusinessProfile | None:
        if self.client is None:
            return MEMORY_PROFILES.get(user_id)

        response = (
            self.client.table("profiles")
            .select("user_id,business_description,keywords,subreddits,updated_at")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        if not rows:
            return None

        return BusinessProfile(**rows[0])

    def upsert_profile(self, profile: BusinessProfile) -> BusinessProfile:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "user_id": profile.user_id,
            "business_description": profile.business_description,
            "keywords": profile.keywords,
            "subreddits": profile.subreddits,
            "updated_at": now.isoformat()
        }

        if self.client is None:
            updated = BusinessProfile(**payload)
            MEMORY_PROFILES[profile.user_id] = updated
            return updated

        (
            self.client.table("profiles")
            .upsert(payload, on_conflict="user_id")
            .execute()
        )

        return BusinessProfile(**payload)
