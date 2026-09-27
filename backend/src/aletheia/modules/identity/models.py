import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, func, true
from sqlalchemy.orm import Mapped, mapped_column

from aletheia.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="email_lowercase"),
        CheckConstraint("length(btrim(full_name)) > 0", name="full_name_not_blank"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())
    email_verified_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    access_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_expires_at: Mapped[datetime]
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    previous_refresh_token_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    expires_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_refreshed_at: Mapped[datetime | None]
    revoked_at: Mapped[datetime | None]
    revocation_reason: Mapped[str | None] = mapped_column(String(32))
