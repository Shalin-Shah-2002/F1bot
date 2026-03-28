from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


def _normalize_string_list(value: list[str] | str | None) -> list[str]:
    if value is None:
        return []

    raw_items = [value] if isinstance(value, str) else [str(item) for item in value]

    normalized: list[str] = []
    for raw in raw_items:
        for part in str(raw).split(","):
            item = part.strip()
            if item:
                normalized.append(item)

    return normalized


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
        return _normalize_string_list(value)


class LeadScanResponse(BaseModel):
    leads: list[LeadInsight]
    total_candidates: int
    used_ai: bool


LeadStatus = Literal["new", "contacted", "qualified", "ignored"]


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=3)


class LoginResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    full_name: str | None = Field(default=None, max_length=120)


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


class BusinessProfile(BaseModel):
    user_id: str
    business_description: str = Field(min_length=10, max_length=2000)
    keywords: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)
    updated_at: datetime | None = None

    @field_validator("keywords", "subreddits", mode="before")
    @classmethod
    def normalize_profile_list(cls, value: list[str] | str | None) -> list[str]:
        return _normalize_string_list(value)


class BusinessProfileUpsertRequest(BaseModel):
    business_description: str = Field(min_length=10, max_length=2000)
    keywords: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)

    @field_validator("keywords", "subreddits", mode="before")
    @classmethod
    def normalize_profile_list(cls, value: list[str] | str | None) -> list[str]:
        return _normalize_string_list(value)


class LeadRecord(BaseModel):
    id: str
    user_id: str
    status: LeadStatus = "new"
    post: CandidatePost
    lead_score: float = Field(ge=0, le=100)
    qualification_reason: str
    suggested_outreach: str
    scan_id: str
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    leads: list[LeadRecord]


class LeadStatusUpdateRequest(BaseModel):
    status: LeadStatus
