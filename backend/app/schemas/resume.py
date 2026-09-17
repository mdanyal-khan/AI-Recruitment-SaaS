from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: UUID

    candidate_id: UUID

    file_name: str

    file_url: str

    file_type: str | None = None

    file_size: int | None = None

    version: int

    is_primary: bool

    uploaded_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )