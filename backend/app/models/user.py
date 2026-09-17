import uuid
from datetime import datetime

from sqlalchemy.orm import relationship

from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    company_memberships = relationship(
    "CompanyMember",
    back_populates="user",
    cascade="all, delete-orphan"
)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    first_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    last_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("true"),
        nullable=False
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