import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from aletheia.core.database import Base, enum_values_check, string_enum


class EvidenceStatus(enum.StrEnum):
    PENDING = "pending"
    PRESERVED = "preserved"
    FAILED = "failed"


class EvidenceCounter(Base):
    """Last evidence number issued per organization and year."""

    __tablename__ = "evidence_counters"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), primary_key=True
    )
    year: Mapped[int] = mapped_column(primary_key=True)
    last_number: Mapped[int]


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["organization_id", "case_id"],
            ["cases.organization_id", "cases.id"],
            name="fk_evidence_case",
        ),
        UniqueConstraint("organization_id", "reference", name="uq_evidence_organization_reference"),
        Index(
            "uq_evidence_case_sha256_not_failed",
            "case_id",
            "sha256",
            unique=True,
            postgresql_where=text("status <> 'failed'"),
        ),
        CheckConstraint("sha256 ~ '^[0-9a-f]{64}$'", name="sha256_format"),
        CheckConstraint("size_bytes > 0", name="size_positive"),
        CheckConstraint(enum_values_check("status", EvidenceStatus), name="status_valid"),
        CheckConstraint(
            "(status = 'preserved') = (preserved_at IS NOT NULL)",
            name="preserved_at_matches_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID]
    case_id: Mapped[uuid.UUID] = mapped_column(index=True)
    reference: Mapped[str] = mapped_column(String(20))
    original_filename: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(String(127))
    size_bytes: Mapped[int] = mapped_column(BigInteger)
    sha256: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(String(512), unique=True)
    status: Mapped[EvidenceStatus] = mapped_column(string_enum(EvidenceStatus))
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    preserved_at: Mapped[datetime | None]
