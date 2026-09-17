import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    file_url: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    file_type: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    file_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False
    )