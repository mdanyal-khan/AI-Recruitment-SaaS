from datetime import datetime
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator


class InterviewCreate(BaseModel):
    application_id: UUID

    start_time: datetime
    end_time: datetime

    timezone: str = "UTC"

    mode: Literal[
        "ONLINE",
        "IN_PERSON",
        "PHONE",
    ]

    meeting_url: str | None = None
    location: str | None = None

    @model_validator(mode="after")
    def validate_interview(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "Interview end time must be after start time."
            )

        if self.mode == "ONLINE" and not self.meeting_url:
            raise ValueError(
                "Meeting URL is required for online interviews."
            )

        if self.mode == "IN_PERSON" and not self.location:
            raise ValueError(
                "Location is required for in-person interviews."
            )

        return self


class InterviewStatusUpdate(BaseModel):
    status: Literal[
        "SCHEDULED",
        "CONFIRMED",
        "COMPLETED",
        "CANCELLED",
        "NO_SHOW",
    ]


class InterviewResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    application_id: UUID

    scheduled_by: UUID | None

    start_time: datetime
    end_time: datetime

    timezone: str | None

    mode: str | None

    meeting_url: str | None
    location: str | None

    status: str

    created_at: datetime | None
    updated_at: datetime | None