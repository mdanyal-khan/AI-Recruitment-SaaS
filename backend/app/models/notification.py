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


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    type = Column(
        Text,
        nullable=True,
    )

    channel = Column(
        Text,
        nullable=True,
    )

    subject = Column(
        Text,
        nullable=True,
    )

    message = Column(
        Text,
        nullable=True,
    )

    status = Column(
        Text,
        nullable=True,
        default="PENDING",
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            """
            type IN (
                'INTERVIEW_INVITATION',
                'APPLICATION_UPDATE',
                'JOB_ALERT',
                'OFFER',
                'REJECTION',
                'GENERAL'
            )
            """,
            name="notifications_type_check",
        ),
        CheckConstraint(
            """
            channel IN (
                'EMAIL',
                'SMS',
                'IN_APP'
            )
            """,
            name="notifications_channel_check",
        ),
        CheckConstraint(
            """
            status IN (
                'PENDING',
                'SENT',
                'FAILED',
                'READ'
            )
            """,
            name="notifications_status_check",
        ),
    )