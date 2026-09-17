from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CandidateCreate(BaseModel):
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None

    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    years_experience: Decimal | None = None


class CandidateUpdate(BaseModel):
    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None

    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    years_experience: Decimal | None = None


class CandidateResponse(BaseModel):
    id: UUID
    user_id: UUID

    headline: str | None = None
    summary: str | None = None
    location: str | None = None
    phone: str | None = None

    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    years_experience: Decimal | None = None

    model_config = ConfigDict(
        from_attributes=True
    )