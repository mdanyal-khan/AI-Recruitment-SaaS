from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    job_id: UUID
    resume_id: UUID | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    candidate_id: UUID
    resume_id: UUID | None
    status: str
    applied_at: datetime
    updated_at: datetime


class ApplicationStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern="^(APPLIED|SHORTLISTED|INTERVIEWING|OFFERED|HIRED|REJECTED|WITHDRAWN)$",
    )