from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CandidatePost(BaseModel):
    id: str
    title: str
    body: str
    subreddit: str
    url: str
    author: str
    created_utc: datetime
    score: int
    num_comments: int


class LeadInsight(BaseModel):
    post: CandidatePost
    lead_score: float = Field(ge=0, le=100)
    qualification_reason: str
    suggested_outreach: str


class LeadScanRequest(BaseModel):
    business_description: str = Field(min_length=10, max_length=2000)
    keywords: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=lambda: ["entrepreneur", "smallbusiness", "marketing"])
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("keywords", "subreddits", mode="before")
    @classmethod
    def normalize_list(cls, value: list[str] | str | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return [str(item).strip() for item in value if str(item).strip()]


class LeadScanResponse(BaseModel):
    leads: list[LeadInsight]
    total_candidates: int
    used_ai: bool
