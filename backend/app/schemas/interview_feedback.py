from uuid import UUID
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict


class InterviewFeedbackCreate(BaseModel):
    rating: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    technical_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    communication_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    culture_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
    )

    comments: str | None = None

    recommendation: Literal[
        "STRONG_HIRE",
        "HIRE",
        "NEUTRAL",
        "NO_HIRE",
        "STRONG_NO_HIRE",
    ]


class InterviewFeedbackResponse(BaseModel):
    id: UUID
    interview_id: UUID
    reviewer_id: UUID | None

    rating: float | None
    technical_score: float | None
    communication_score: float | None
    culture_score: float | None

    comments: str | None
    recommendation: str | None

    model_config = ConfigDict(from_attributes=True)