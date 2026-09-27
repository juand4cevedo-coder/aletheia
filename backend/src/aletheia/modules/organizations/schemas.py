import uuid
from datetime import datetime

from pydantic import BaseModel

from aletheia.modules.organizations.models import MembershipRole
from aletheia.modules.organizations.permissions import Permission
from aletheia.shared.types import DisplayName


class OrganizationSummary(BaseModel):
    id: uuid.UUID
    name: str
    role: MembershipRole


class OrganizationDetail(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    role: MembershipRole
    permissions: list[Permission]


class OrganizationUpdate(BaseModel):
    name: DisplayName


class MemberSummary(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: MembershipRole
    joined_at: datetime
