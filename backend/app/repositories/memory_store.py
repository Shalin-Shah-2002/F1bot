from app.models.schemas import BusinessProfile, LeadRecord

MEMORY_PROFILES: dict[str, BusinessProfile] = {}
MEMORY_LEADS: dict[str, LeadRecord] = {}

# Maps user_id -> set of Reddit post IDs the user has already seen.
# Used for deduplication so that repeated scans with the same query surface fresh leads.
MEMORY_SEEN_POSTS: dict[str, set[str]] = {}
