import uuid
from datetime import datetime

from pydantic import BaseModel

from aletheia.modules.evidence.models import EvidenceStatus


class EvidenceSummary(BaseModel):
    id: uuid.UUID
    reference: str
    original_filename: str
    media_type: str
    size_bytes: int
    sha256: str
    status: EvidenceStatus
    created_at: datetime
    preserved_at: datetime | None


class EvidenceDetail(EvidenceSummary):
    uploaded_by: uuid.UUID
