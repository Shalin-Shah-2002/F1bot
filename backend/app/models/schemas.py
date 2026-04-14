from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

AUTH_PASSWORD_MIN_LENGTH = 10
AUTH_PASSWORD_MAX_LENGTH = 128


def _validate_auth_password(value: str) -> str:
    if any(char.isspace() for char in value):
        raise ValueError("Password must not contain whitespace.")

    has_lower = any(char.islower() for char in value)
    has_upper = any(char.isupper() for char in value)
    has_digit = any(char.isdigit() for char in value)
    has_symbol = any(not char.isalnum() for char in value)

    if not all((has_lower, has_upper, has_digit, has_symbol)):
        raise ValueError(
            "Password must include at least one uppercase letter, one lowercase letter, one number, and one symbol."
        )

    return value


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
    email: EmailStr
    password: str = Field(min_length=AUTH_PASSWORD_MIN_LENGTH, max_length=AUTH_PASSWORD_MAX_LENGTH)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return _validate_auth_password(value)


class LoginResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(LoginRequest):
    full_name: str | None = Field(default=None, max_length=120)


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"


class SessionResponse(BaseModel):
    user_id: str
    email: str


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
