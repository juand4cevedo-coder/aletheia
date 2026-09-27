import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.modules.cases.errors import CaseNotFoundError
from aletheia.modules.cases.models import Case, CaseMember
from aletheia.modules.organizations.dependencies import OrganizationContext, require_permission
from aletheia.modules.organizations.permissions import Permission


@dataclass(frozen=True)
class CaseContext:
    """A case the current user is an explicit member of, within the request's organization."""

    organization: OrganizationContext
    case: Case
    case_member: CaseMember


def get_case_context(
    case_id: uuid.UUID,
    organization: Annotated[
        OrganizationContext, Depends(require_permission(Permission.ORGANIZATION_READ))
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> CaseContext:
    row = session.execute(
        select(Case, CaseMember)
        .join(CaseMember, CaseMember.case_id == Case.id)
        .where(
            Case.id == case_id,
            Case.organization_id == organization.organization.id,
            CaseMember.user_id == organization.membership.user_id,
        )
    ).one_or_none()
    if row is None:
        raise CaseNotFoundError()
    case, case_member = row
    return CaseContext(organization=organization, case=case, case_member=case_member)


CurrentCase = Annotated[CaseContext, Depends(get_case_context)]
