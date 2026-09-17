from uuid import UUID

from pydantic import BaseModel


class HiringDecisionRequest(BaseModel):
    decision: str


class HiringDecisionResponse(BaseModel):
    application_id: UUID
    previous_status: str
    new_status: str
    decision: str
    message: str