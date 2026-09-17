from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OfferCreate(BaseModel):
    application_id: UUID

    salary: Decimal = Field(..., ge=0)

    currency: str = Field(
        default="USD",
        min_length=1,
        max_length=10,
    )

    start_date: date

    expiration_date: date

    offer_letter_url: str | None = None

    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expiration_date < date.today():
            raise ValueError(
                "Expiration date cannot be in the past."
            )

        if self.expiration_date > self.start_date:
            raise ValueError(
                "Expiration date must be before or equal to start date."
            )

        return self


class OfferStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        pattern="^(PENDING|SENT|ACCEPTED|DECLINED|EXPIRED|CANCELLED)$",
    )


class OfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    created_by: UUID | None

    job_title: str

    salary: Decimal

    currency: str

    employment_type: str | None

    start_date: date

    expiration_date: date

    status: str

    offer_letter_url: str | None

    notes: str | None

    created_at: datetime
    updated_at: datetime