import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from aletheia.modules.cases.models import CaseRole, CaseStatus
from aletheia.modules.cases.permissions import CasePermission
from aletheia.shared.types import DisplayName

DESCRIPTION_MAX_LENGTH = 5000


class CaseCreate(BaseModel):
    title: DisplayName
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)


class CaseUpdate(BaseModel):
    """Partial update: only the fields present in the request are changed."""

    title: DisplayName | None = None
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)

    @field_validator("title")
    @classmethod
    def title_cannot_be_null(cls, title: str | None) -> str:
        if title is None:
            raise ValueError("title cannot be null")
        return title


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
    my_permissions: list[CasePermission]


class CaseMemberAdd(BaseModel):
    user_id: uuid.UUID
    role: CaseRole


class CaseMemberUpdate(BaseModel):
    role: CaseRole


class CaseMemberSummary(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: CaseRole
    added_at: datetime
