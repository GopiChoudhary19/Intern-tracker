from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OpportunitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    organization: str
    type: str
    domain: str
    mode: str
    location_text: str | None = None
    tags: list[str]
    deadline_at: datetime | None = None
    is_verified: bool
    status: str = "published"
    description: str


class OpportunityDetail(OpportunitySummary):
    application_url: str
    eligibility_text: str | None = None
    required_skills: list[str]
    stipend_min: float | None = None
    stipend_max: float | None = None
    currency: str | None = None


class PaginationMetadata(BaseModel):
    total: int
    page: int
    page_size: int
    has_next_page: bool


class OpportunityListResponse(BaseModel):
    items: list[OpportunitySummary]
    metadata: PaginationMetadata | None = None


class ApplicationRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    applied_at: datetime | None = None
    next_follow_up_at: datetime | None = None
    note: str | None = None
    opportunity: OpportunitySummary


class ApplicationsResponse(BaseModel):
    items: list[ApplicationRecord]


class CreateApplicationRequest(BaseModel):
    opportunity_id: UUID
    status: str = Field(default="saved")
    note: str | None = Field(default=None, max_length=5000)


class UpdateApplicationRequest(BaseModel):
    status: str = Field(default=None)
    note: str | None = Field(default=None, max_length=5000)
    next_follow_up_at: datetime | None = None

    @field_validator("status", mode="before")
    @classmethod
    def status_cannot_be_cleared(cls, value):
        # status is NOT NULL; an explicit null used to reach the database and fail with a 500
        if value is None:
            raise ValueError("status cannot be null")
        return value


class UserProfileResponse(BaseModel):
    id: UUID
    email: str | None = None
    phone: str | None = None
    full_name: str
    college_name: str | None = None
    degree: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    city: str | None = None
    country: str | None = None
    bio: str | None = None
    goals: str | None = None
    preferred_domains: list[str]
    preferred_locations: list[str]
    preferred_opportunity_types: list[str]
    skills: list[str]
    github_url: str | None = None
    linkedin_url: str | None = None
    resume_url: str | None = None
    onboarding_completed: bool


ShortText = Annotated[str, Field(max_length=100)]


class UpdateProfileRequest(BaseModel):
    # limits follow the database columns, so bad input is a 422 instead of a failed write
    full_name: str = Field(default=None, min_length=1, max_length=255)
    college_name: str | None = Field(default=None, max_length=255)
    degree: str | None = Field(default=None, max_length=100)
    branch: str | None = Field(default=None, max_length=100)
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)
    city: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=2000)
    goals: str | None = Field(default=None, max_length=2000)
    preferred_domains: list[ShortText] | None = Field(default=None, max_length=50)
    preferred_locations: list[ShortText] | None = Field(default=None, max_length=50)
    preferred_opportunity_types: list[ShortText] | None = Field(default=None, max_length=50)
    skills: list[ShortText] | None = Field(default=None, max_length=50)
    github_url: str | None = Field(default=None, max_length=2000)
    linkedin_url: str | None = Field(default=None, max_length=2000)
    resume_url: str | None = Field(default=None, max_length=2000)
    onboarding_completed: bool | None = None

    @field_validator("full_name", mode="before")
    @classmethod
    def full_name_is_required_once_sent(cls, value):
        # the column is NOT NULL; sending null used to fail the write with a 500
        if value is None:
            raise ValueError("full_name cannot be null")
        return value.strip() if isinstance(value, str) else value

    @field_validator("preferred_domains", "preferred_locations", "preferred_opportunity_types", "skills", mode="before")
    @classmethod
    def null_list_means_empty(cls, value):
        # storing NULL in these array columns made every later GET /me fail, so null clears the list instead
        return [] if value is None else value


class RequestOtpRequest(BaseModel):
    email: str | None = None
    phone: str | None = None


class RequestOtpResponse(BaseModel):
    challenge_id: UUID
    message: str
    channel: str
    target_hint: str
    development_code: str | None = None


class VerifyOtpRequest(BaseModel):
    challenge_id: UUID
    email: str | None = None
    phone: str | None = None
    otp: str = "000000"
    full_name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserProfileResponse


class LogoutResponse(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


class AuthProvider(BaseModel):
    id: str
    label: str
    auth_url: str | None = None
    configured: bool


class AuthProvidersResponse(BaseModel):
    items: list[AuthProvider]


class NotificationItem(BaseModel):
    id: str
    title: str
    detail: str


class NotificationsResponse(BaseModel):
    items: list[NotificationItem]


class ThreadItem(BaseModel):
    id: str
    title: str
    category: str
    author_name: str


class ThreadsResponse(BaseModel):
    items: list[ThreadItem]


class AnalyticsOverviewResponse(BaseModel):
    active_users: int
    new_opportunities: int
    saved_applications: int
    applied_applications: int


class AdminUserSummary(BaseModel):
    id: UUID
    email: str | None = None
    phone: str | None = None
    full_name: str
    college_name: str | None = None
    degree: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    city: str | None = None
    country: str | None = None
    onboarding_completed: bool
    applications_count: int
    created_at: datetime
    updated_at: datetime | None = None


class AdminUsersResponse(BaseModel):
    items: list[AdminUserSummary]


class CreateFeedbackRequest(BaseModel):
    category: str
    message: str = Field(min_length=5, max_length=4000)
    name: str | None = None
    email: str | None = None


class FeedbackSubmissionResponse(BaseModel):
    id: UUID
    category: str
    message: str
    name: str | None = None
    email: str | None = None
    status: str
    created_at: datetime


class AdminFeedbackItem(BaseModel):
    id: UUID
    category: str
    message: str
    name: str | None = None
    email: str | None = None
    status: str
    created_at: datetime
    user_id: UUID | None = None
    user_name: str | None = None


class AdminFeedbackResponse(BaseModel):
    items: list[AdminFeedbackItem]


class AdminOpportunityPayload(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    organization: str = Field(min_length=2, max_length=255)
    type: str = Field(min_length=3, max_length=50)
    domain: str = Field(min_length=2, max_length=100)
    mode: str = Field(min_length=3, max_length=30)
    location_text: str | None = None
    description: str = Field(min_length=10, max_length=5000)
    application_url: str = Field(min_length=8, max_length=2000)
    eligibility_text: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    stipend_min: float | None = None
    stipend_max: float | None = None
    currency: str | None = None
    deadline_at: datetime | None = None
    is_verified: bool = False
    status: str = "published"


class UpdateFeedbackStatusRequest(BaseModel):
    status: str = Field(min_length=2, max_length=30)


class SavedSearchResponse(BaseModel):
    id: UUID
    label: str
    search: str | None = None
    type: str | None = None
    mode: str | None = None
    verified: bool = False
    deadline_days: int | None = None
    paid_only: bool = False
    min_stipend: float | None = None
    created_at: datetime


class SavedSearchListResponse(BaseModel):
    items: list[SavedSearchResponse]


class CreateSavedSearchRequest(BaseModel):
    # limits follow the saved_searches columns, so bad input is a 422 instead of a failed write
    label: str = Field(min_length=2, max_length=255)
    search: str | None = Field(default=None, max_length=255)
    type: str | None = Field(default=None, max_length=50)
    mode: str | None = Field(default=None, max_length=30)
    verified: bool = False
    deadline_days: int | None = Field(default=None, ge=0, le=365)
    paid_only: bool = False
    min_stipend: float | None = Field(default=None, ge=0, lt=100_000_000)


class ResumeAnalyzeRequest(BaseModel):
    opportunity_slug: str | None = None
    resume_text: str | None = None


class ResumeAnalyzeResponse(BaseModel):
    summary: str
    highlights: list[str]


class CoverLetterRequest(BaseModel):
    opportunity_slug: str


class CoverLetterResponse(BaseModel):
    content: str
