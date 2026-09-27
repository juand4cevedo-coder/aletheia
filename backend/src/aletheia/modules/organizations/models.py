import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from aletheia.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = (CheckConstraint("length(btrim(name)) > 0", name="name_not_blank"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class MembershipRole(enum.StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    LAWYER = "lawyer"
    COLLABORATOR = "collaborator"
    AUDITOR = "auditor"


_ROLE_VALUES = ", ".join(f"'{role.value}'" for role in MembershipRole)


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (CheckConstraint(f"role IN ({_ROLE_VALUES})", name="role_valid"),)

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True, index=True)
    role: Mapped[MembershipRole] = mapped_column(
        Enum(
            MembershipRole,
            native_enum=False,
            create_constraint=False,
            length=32,
            values_callable=lambda roles: [role.value for role in roles],
        )
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
