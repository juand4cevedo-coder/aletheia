import logging
import uuid
from datetime import UTC, datetime
from typing import BinaryIO

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.core.database import violated_constraint
from aletheia.core.storage import ObjectStorage, StorageError
from aletheia.modules.cases.models import Case, CaseStatus
from aletheia.modules.evidence.errors import (
    CaseNotActiveError,
    EvidenceAlreadyExistsError,
    EvidenceNotFoundError,
    EvidenceStorageError,
)
from aletheia.modules.evidence.files import inspect_upload
from aletheia.modules.evidence.models import Evidence, EvidenceCounter, EvidenceStatus
from aletheia.modules.evidence.schemas import EvidenceDetail, EvidenceSummary

logger = logging.getLogger(__name__)


def format_reference(year: int, number: int) -> str:
    return f"EVD-{year}-{number:06d}"


def storage_key_for(evidence: Evidence) -> str:
    """Object key built only from identifiers: user-supplied names never reach the storage."""
    return (
        f"organizations/{evidence.organization_id}/cases/{evidence.case_id}"
        f"/evidence/{evidence.id}/original"
    )


def _next_evidence_number(session: Session, organization_id: uuid.UUID, year: int) -> int:
    statement = (
        insert(EvidenceCounter)
        .values(organization_id=organization_id, year=year, last_number=1)
        .on_conflict_do_update(
            index_elements=[EvidenceCounter.organization_id, EvidenceCounter.year],
            set_={"last_number": EvidenceCounter.last_number + 1},
        )
        .returning(EvidenceCounter.last_number)
    )
    return session.execute(statement).scalar_one()


def preserve_evidence(
    session: Session,
    storage: ObjectStorage,
    case: Case,
    uploader_id: uuid.UUID,
    file: BinaryIO,
    filename: str | None,
    *,
    max_bytes: int,
) -> EvidenceDetail:
    """Validate, fingerprint and store an uploaded file as evidence of a case.

    The database record is committed as PENDING before the upload, and only marked
    PRESERVED after the storage confirms the write. A record never claims a file is
    preserved unless the storage has accepted it with the recorded SHA-256.
    """
    if case.status is not CaseStatus.ACTIVE:
        raise CaseNotActiveError()

    inspected = inspect_upload(file, filename, max_bytes=max_bytes)

    duplicate = session.scalar(
        select(Evidence.id).where(
            Evidence.case_id == case.id,
            Evidence.sha256 == inspected.sha256,
            Evidence.status != EvidenceStatus.FAILED,
        )
    )
    if duplicate is not None:
        raise EvidenceAlreadyExistsError()

    year = datetime.now(UTC).year
    evidence = Evidence(
        id=uuid.uuid4(),
        organization_id=case.organization_id,
        case_id=case.id,
        reference=format_reference(
            year, _next_evidence_number(session, case.organization_id, year)
        ),
        original_filename=inspected.filename,
        media_type=inspected.media_type,
        size_bytes=inspected.size_bytes,
        sha256=inspected.sha256,
        status=EvidenceStatus.PENDING,
        uploaded_by=uploader_id,
    )
    evidence.storage_key = storage_key_for(evidence)
    try:
        session.add(evidence)
        session.commit()
    except IntegrityError as error:
        session.rollback()
        if violated_constraint(error) == "uq_evidence_case_sha256_not_failed":
            raise EvidenceAlreadyExistsError() from error
        raise

    try:
        storage.put_new_object(
            evidence.storage_key,
            file,
            sha256_hex=evidence.sha256,
            content_type=evidence.media_type,
        )
    except StorageError as error:
        logger.error("Evidence upload failed (evidence_id=%s)", evidence.id, exc_info=error)
        evidence.status = EvidenceStatus.FAILED
        session.commit()
        raise EvidenceStorageError() from error

    evidence.status = EvidenceStatus.PRESERVED
    evidence.preserved_at = datetime.now(UTC)
    session.commit()
    return to_detail(evidence)


def list_case_evidence(session: Session, case_id: uuid.UUID) -> list[EvidenceSummary]:
    rows = session.scalars(
        select(Evidence)
        .where(Evidence.case_id == case_id)
        .order_by(Evidence.created_at.desc(), Evidence.id)
    ).all()
    return [to_summary(evidence) for evidence in rows]


def get_case_evidence(session: Session, case_id: uuid.UUID, evidence_id: uuid.UUID) -> Evidence:
    evidence = session.scalar(
        select(Evidence).where(Evidence.id == evidence_id, Evidence.case_id == case_id)
    )
    if evidence is None:
        raise EvidenceNotFoundError()
    return evidence


def to_summary(evidence: Evidence) -> EvidenceSummary:
    return EvidenceSummary(
        id=evidence.id,
        reference=evidence.reference,
        original_filename=evidence.original_filename,
        media_type=evidence.media_type,
        size_bytes=evidence.size_bytes,
        sha256=evidence.sha256,
        status=evidence.status,
        created_at=evidence.created_at,
        preserved_at=evidence.preserved_at,
    )


def to_detail(evidence: Evidence) -> EvidenceDetail:
    return EvidenceDetail(
        **to_summary(evidence).model_dump(),
        uploaded_by=evidence.uploaded_by,
    )
