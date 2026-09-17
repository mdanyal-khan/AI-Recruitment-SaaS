import uuid

from sqlalchemy import (
    Column,
    Text,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class InterviewFeedback(Base):
    __tablename__ = "interview_feedback"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "interviews.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    reviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    rating = Column(
        Numeric(3, 1),
        nullable=True,
    )

    technical_score = Column(
        Numeric(3, 1),
        nullable=True,
    )

    communication_score = Column(
        Numeric(3, 1),
        nullable=True,
    )

    culture_score = Column(
        Numeric(3, 1),
        nullable=True,
    )

    comments = Column(
        Text,
        nullable=True,
    )

    recommendation = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "rating >= 0 AND rating <= 10",
            name="interview_feedback_rating_check",
        ),
        CheckConstraint(
            """
            technical_score >= 0
            AND technical_score <= 10
            """,
            name="interview_feedback_technical_score_check",
        ),
        CheckConstraint(
            """
            communication_score >= 0
            AND communication_score <= 10
            """,
            name="interview_feedback_communication_score_check",
        ),
        CheckConstraint(
            """
            culture_score >= 0
            AND culture_score <= 10
            """,
            name="interview_feedback_culture_score_check",
        ),
        CheckConstraint(
            """
            recommendation IN (
                'STRONG_HIRE',
                'HIRE',
                'NEUTRAL',
                'NO_HIRE',
                'STRONG_NO_HIRE'
            )
            """,
            name="interview_feedback_recommendation_check",
        ),
    )