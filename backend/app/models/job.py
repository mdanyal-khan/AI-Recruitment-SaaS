import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    employment_type: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    experience_min: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True
    )

    experience_max: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True
    )

    education_level: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True
    )

    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'DRAFT'")
    )

    deadline: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False
    )