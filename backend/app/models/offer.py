import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    job_title = Column(
        String(255),
        nullable=False,
    )

    salary = Column(
        Numeric(12, 2),
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="USD",
    )

    employment_type = Column(
        String(50),
        nullable=True,
    )

    start_date = Column(
        Date,
        nullable=False,
    )

    expiration_date = Column(
        Date,
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    offer_letter_url = Column(
        Text,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )