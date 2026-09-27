import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.modules.cases import service
from aletheia.modules.cases.dependencies import CaseContext, require_case_permission
from aletheia.modules.cases.permissions import CasePermission
from aletheia.modules.cases.schemas import (
    CaseCreate,
    CaseDetail,
    CaseMemberAdd,
    CaseMemberSummary,
    CaseMemberUpdate,
    CaseSummary,
    CaseUpdate,
)
from aletheia.modules.organizations.dependencies import OrganizationContext, require_permission
from aletheia.modules.organizations.permissions import Permission

router = APIRouter(prefix="/organizations/{organization_id}/cases", tags=["cases"])

DbSession = Annotated[Session, Depends(get_db_session)]
CanCreateCases = Annotated[OrganizationContext, Depends(require_permission(Permission.CASE_CREATE))]
CanReadOrganization = Annotated[
    OrganizationContext, Depends(require_permission(Permission.ORGANIZATION_READ))
]
CanReadCase = Annotated[CaseContext, Depends(require_case_permission(CasePermission.READ))]
CanUpdateCase = Annotated[CaseContext, Depends(require_case_permission(CasePermission.UPDATE))]
CanManageCaseMembers = Annotated[
    CaseContext, Depends(require_case_permission(CasePermission.MANAGE_MEMBERS))
]

ERRORS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}
MEMBER_ERRORS: dict[int | str, dict[str, Any]] = {
    **ERRORS,
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
}


# --- cases -------------------------------------------------------------------


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
def get_case(context: CanReadCase) -> CaseDetail:
    return service.to_detail(context.case, context.case_member.role)


@router.patch("/{case_id}", responses=ERRORS)
def update_case(payload: CaseUpdate, context: CanUpdateCase, session: DbSession) -> CaseDetail:
    service.update_case(session, context.case, payload)
    return service.to_detail(context.case, context.case_member.role)


# --- case members ------------------------------------------------------------


@router.get("/{case_id}/members", responses=ERRORS)
def list_case_members(context: CanReadCase, session: DbSession) -> list[CaseMemberSummary]:
    return service.list_case_members(session, context.case.id)


@router.post("/{case_id}/members", status_code=status.HTTP_201_CREATED, responses=MEMBER_ERRORS)
def add_case_member(
    payload: CaseMemberAdd, context: CanManageCaseMembers, session: DbSession
) -> CaseMemberSummary:
    return service.add_case_member(session, context.case, payload)


@router.patch("/{case_id}/members/{user_id}", responses=MEMBER_ERRORS)
def change_case_member_role(
    user_id: uuid.UUID, payload: CaseMemberUpdate, context: CanManageCaseMembers, session: DbSession
) -> CaseMemberSummary:
    return service.change_case_member_role(session, context.case, user_id, payload.role)


@router.delete(
    "/{case_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses=MEMBER_ERRORS
)
def remove_case_member(
    user_id: uuid.UUID, context: CanManageCaseMembers, session: DbSession
) -> None:
    service.remove_case_member(session, context.case, user_id)
