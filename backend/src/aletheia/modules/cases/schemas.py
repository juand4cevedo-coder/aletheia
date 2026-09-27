import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from aletheia.modules.cases.models import CaseRole, CaseStatus
from aletheia.shared.types import DisplayName


class CaseCreate(BaseModel):
    title: DisplayName
    description: str | None = Field(default=None, max_length=5000)


class CaseSummary(BaseModel):
    id: uuid.UUID
    reference: str
    title: str
    status: CaseStatus
    my_role: CaseRole
    created_at: datetime


class CaseDetail(CaseSummary):
    description: str | None
    updated_at: datetime
