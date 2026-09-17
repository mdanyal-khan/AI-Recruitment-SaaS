from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AIAnalysisResponse(BaseModel):
    id: UUID

    entity_type: str
    entity_id: UUID

    analysis_type: str

    model: str | None = None
    prompt_version: str | None = None

    result_json: dict[str, Any]

    confidence: Decimal | None = None

    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )