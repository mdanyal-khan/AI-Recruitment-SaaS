from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


EmploymentType = Literal[
    "FULL_TIME",
    "PART_TIME",
    "CONTRACT",
    "INTERNSHIP",
    "REMOTE",
]


class JobCreate(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    employment_type: EmploymentType | None = None
    experience_min: Decimal | None = None
    experience_max: Decimal | None = None
    education_level: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    deadline: date | None = None


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    employment_type: EmploymentType | None = None
    experience_min: Decimal | None = None
    experience_max: Decimal | None = None
    education_level: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    deadline: date | None = None


class JobResponse(BaseModel):
    id: UUID
    company_id: UUID
    created_by: UUID | None = None

    title: str
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None

    experience_min: Decimal | None = None
    experience_max: Decimal | None = None

    education_level: str | None = None

    salary_min: Decimal | None = None
    salary_max: Decimal | None = None

    status: str
    deadline: date | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
