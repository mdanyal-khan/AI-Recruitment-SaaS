import uuid

from sqlalchemy import Column, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
    )

    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
    )

    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
    )

    status = Column(
        Text,
        nullable=False,
        default="APPLIED",
    )

    applied_at = Column(
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
            status IN (
                'APPLIED',
                'SHORTLISTED',
                'INTERVIEWING',
                'OFFERED',
                'HIRED',
                'REJECTED',
                'WITHDRAWN'
            )
            """,
            name="applications_status_check",
        ),
    )