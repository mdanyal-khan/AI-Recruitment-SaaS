import uuid

from sqlalchemy import (
    Column,
    Text,
    Numeric,
    DateTime,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id = Column(
        UUID(as_uuid=True),
        nullable=False,
    )

    candidate_id = Column(
        UUID(as_uuid=True),
        nullable=False,
    )

    application_id = Column(
        UUID(as_uuid=True),
        nullable=True,
    )

    overall_score = Column(
        Numeric(5, 2),
        nullable=True,
    )

    skill_score = Column(
        Numeric(5, 2),
        nullable=True,
    )

    experience_score = Column(
        Numeric(5, 2),
        nullable=True,
    )

    education_score = Column(
        Numeric(5, 2),
        nullable=True,
    )

    keyword_score = Column(
        Numeric(5, 2),
        nullable=True,
    )

    classification = Column(
        Text,
        nullable=True,
    )

    explanation = Column(
        JSONB,
        nullable=True,
    )

    missing_skills = Column(
        JSONB,
        nullable=True,
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
            classification IN (
                'STRONG_MATCH',
                'GOOD_MATCH',
                'PARTIAL_MATCH',
                'WEAK_MATCH',
                'NOT_A_MATCH'
            )
            """,
            name="match_results_classification_check",
        ),
    )