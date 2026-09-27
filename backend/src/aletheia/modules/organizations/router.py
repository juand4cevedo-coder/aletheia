from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.modules.identity.dependencies import CurrentAuth
from aletheia.modules.organizations import service
from aletheia.modules.organizations.dependencies import OrganizationContext, require_permission
from aletheia.modules.organizations.permissions import Permission
from aletheia.modules.organizations.schemas import (
    MemberSummary,
    OrganizationDetail,
    OrganizationSummary,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])

DbSession = Annotated[Session, Depends(get_db_session)]
CanReadOrganization = Annotated[
    OrganizationContext, Depends(require_permission(Permission.ORGANIZATION_READ))
]
CanUpdateOrganization = Annotated[
    OrganizationContext, Depends(require_permission(Permission.ORGANIZATION_UPDATE))
]
CanReadMembers = Annotated[OrganizationContext, Depends(require_permission(Permission.MEMBER_READ))]

ERRORS: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_403_FORBIDDEN: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}


def _detail(context: OrganizationContext) -> OrganizationDetail:
    return OrganizationDetail(
        id=context.organization.id,
        name=context.organization.name,
        created_at=context.organization.created_at,
        role=context.membership.role,
        permissions=sorted(context.permissions),
    )


@router.get("", responses=ERRORS)
def list_organizations(auth: CurrentAuth, session: DbSession) -> list[OrganizationSummary]:
    return service.list_user_organizations(session, auth.user.id)


@router.get("/{organization_id}", responses=ERRORS)
def get_organization(context: CanReadOrganization) -> OrganizationDetail:
    return _detail(context)


@router.patch("/{organization_id}", responses=ERRORS)
def update_organization(
    payload: OrganizationUpdate, context: CanUpdateOrganization, session: DbSession
) -> OrganizationDetail:
    service.rename_organization(session, context.organization, payload.name)
    return _detail(context)


@router.get("/{organization_id}/members", responses=ERRORS)
def list_organization_members(context: CanReadMembers, session: DbSession) -> list[MemberSummary]:
    return service.list_members(session, context.organization.id)
