import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.orm import Session

from aletheia.core.config import get_settings
from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.core.storage import ObjectStorage, get_storage
from aletheia.modules.cases.dependencies import CaseContext, require_case_permission
from aletheia.modules.cases.permissions import CasePermission
from aletheia.modules.evidence import service
from aletheia.modules.evidence.schemas import EvidenceDetail, EvidenceSummary

router = APIRouter(
    prefix="/organizations/{organization_id}/cases/{case_id}/evidence", tags=["evidence"]
)

DbSession = Annotated[Session, Depends(get_db_session)]
Storage = Annotated[ObjectStorage, Depends(get_storage)]
CanReadEvidence = Annotated[
    CaseContext, Depends(require_case_permission(CasePermission.EVIDENCE_READ))
]
CanCreateEvidence = Annotated[
    CaseContext, Depends(require_case_permission(CasePermission.EVIDENCE_CREATE))
]

ERRORS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}
UPLOAD_ERRORS: dict[int | str, dict[str, Any]] = {
    **ERRORS,
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_413_CONTENT_TOO_LARGE: {"model": ErrorResponse},
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
}


@router.post("", status_code=status.HTTP_201_CREATED, responses=UPLOAD_ERRORS)
def upload_evidence(
    file: UploadFile, context: CanCreateEvidence, session: DbSession, storage: Storage
) -> EvidenceDetail:
    return service.preserve_evidence(
        session,
        storage,
        context.case,
        context.organization.membership.user_id,
        file.file,
        file.filename,
        max_bytes=get_settings().evidence_max_bytes,
    )


@router.get("", responses=ERRORS)
def list_evidence(context: CanReadEvidence, session: DbSession) -> list[EvidenceSummary]:
    return service.list_case_evidence(session, context.case.id)


@router.get("/{evidence_id}", responses=ERRORS)
def get_evidence(
    evidence_id: uuid.UUID, context: CanReadEvidence, session: DbSession
) -> EvidenceDetail:
    return service.to_detail(service.get_case_evidence(session, context.case.id, evidence_id))
