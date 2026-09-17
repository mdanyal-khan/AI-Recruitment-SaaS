from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AddMemberRequest(BaseModel):
    user_id: UUID | None = None
    email: str | None = None
    role: Literal["HR", "RECRUITER"] = "RECRUITER"


class MemberResponse(BaseModel):
    id: UUID
    company_id: UUID
    user_id: UUID
    role: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )

class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    logo_url: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    website: str | None = None
    industry: str | None = None
    location: str | None = None
    logo_url: str | None = None


class CompanyResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    website: str | None
    industry: str | None
    location: str | None
    logo_url: str | None

    model_config = ConfigDict(
        from_attributes=True
    )