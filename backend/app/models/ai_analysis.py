import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    entity_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    analysis_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    prompt_version: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 3),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('RESUME', 'JOB', 'CANDIDATE')",
            name="ai_analyses_entity_type_check",
        ),
        CheckConstraint(
            "analysis_type IN "
            "('CV_ANALYSIS', 'JOB_ANALYSIS', 'CANDIDATE_SUMMARY')",
            name="ai_analyses_analysis_type_check",
        ),
    )