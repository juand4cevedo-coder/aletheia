import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from aletheia.core.database import Base


class CaseStatus(enum.StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    ARCHIVED = "archived"
    UNDER_LEGAL_HOLD = "under_legal_hold"
    PENDING_DELETION = "pending_deletion"
    DELETED = "deleted"


class CaseRole(enum.StrEnum):
    LEAD = "lead"
    EDITOR = "editor"
    VIEWER = "viewer"


def _values_check(column: str, values: type[enum.StrEnum]) -> str:
    listed = ", ".join(f"'{member.value}'" for member in values)
    return f"{column} IN ({listed})"


def _string_enum(enum_class: type[enum.StrEnum]) -> Enum:
    return Enum(
        enum_class,
        native_enum=False,
        create_constraint=False,
        length=32,
        values_callable=lambda members: [member.value for member in members],
    )


class CaseCounter(Base):
    """Last case number issued per organization and year."""

    __tablename__ = "case_counters"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), primary_key=True
    )
    year: Mapped[int] = mapped_column(primary_key=True)
    last_number: Mapped[int]


class Case(Base):
    __tablename__ = "cases"
    __table_args__ = (
        UniqueConstraint("organization_id", "reference", name="uq_cases_organization_reference"),
        UniqueConstraint("organization_id", "id", name="uq_cases_organization_id_id"),
        CheckConstraint("length(btrim(title)) > 0", name="title_not_blank"),
        CheckConstraint(_values_check("status", CaseStatus), name="status_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"))
    reference: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[CaseStatus] = mapped_column(_string_enum(CaseStatus), default=CaseStatus.ACTIVE)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class CaseMember(Base):
    """Explicit access of an organization member to one case."""

    __tablename__ = "case_members"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "case_id"],
            ["cases.organization_id", "cases.id"],
            name="fk_case_members_case",
        ),
        ForeignKeyConstraint(
            ["organization_id", "user_id"],
            ["memberships.organization_id", "memberships.user_id"],
            name="fk_case_members_membership",
        ),
        CheckConstraint(_values_check("role", CaseRole), name="role_valid"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[uuid.UUID]
    role: Mapped[CaseRole] = mapped_column(_string_enum(CaseRole))
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())
