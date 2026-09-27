from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.modules.cases import service
from aletheia.modules.cases.dependencies import CurrentCase
from aletheia.modules.cases.schemas import CaseCreate, CaseDetail, CaseSummary
from aletheia.modules.organizations.dependencies import OrganizationContext, require_permission
from aletheia.modules.organizations.permissions import Permission

router = APIRouter(prefix="/organizations/{organization_id}/cases", tags=["cases"])

DbSession = Annotated[Session, Depends(get_db_session)]
CanCreateCases = Annotated[OrganizationContext, Depends(require_permission(Permission.CASE_CREATE))]
CanReadOrganization = Annotated[
    OrganizationContext, Depends(require_permission(Permission.ORGANIZATION_READ))
]

ERRORS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}


@router.post("", status_code=status.HTTP_201_CREATED, responses=ERRORS)
def create_case(payload: CaseCreate, context: CanCreateCases, session: DbSession) -> CaseDetail:
    return service.create_case(
        session, context.organization.id, context.membership.user_id, payload
    )


@router.get("", responses=ERRORS)
def list_cases(context: CanReadOrganization, session: DbSession) -> list[CaseSummary]:
    return service.list_cases_for_member(
        session, context.organization.id, context.membership.user_id
    )


@router.get("/{case_id}", responses=ERRORS)
def get_case(context: CurrentCase) -> CaseDetail:
    return service.to_detail(context.case, context.case_member.role)
