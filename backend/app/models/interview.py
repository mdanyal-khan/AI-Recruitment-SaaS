import uuid

from sqlalchemy import (
    Column,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "applications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    scheduled_by = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    timezone = Column(
        Text,
        nullable=True,
        default="UTC",
    )

    mode = Column(
        Text,
        nullable=True,
    )

    meeting_url = Column(
        Text,
        nullable=True,
    )

    location = Column(
        Text,
        nullable=True,
    )

    status = Column(
        Text,
        nullable=False,
        default="SCHEDULED",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            """
            mode IN (
                'ONLINE',
                'IN_PERSON',
                'PHONE'
            )
            """,
            name="interviews_mode_check",
        ),
        CheckConstraint(
            """
            status IN (
                'SCHEDULED',
                'CONFIRMED',
                'COMPLETED',
                'CANCELLED',
                'NO_SHOW'
            )
            """,
            name="interviews_status_check",
        ),
    )