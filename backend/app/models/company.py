import uuid
from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy import DateTime, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    members = relationship(
    "CompanyMember",
    back_populates="company",
    cascade="all, delete-orphan"
)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    industry: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    logo_url: Mapped[str | None] = mapped_column(
        Text,
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