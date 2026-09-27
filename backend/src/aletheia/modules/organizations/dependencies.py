import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.modules.identity.dependencies import CurrentAuth
from aletheia.modules.organizations.errors import (
    OrganizationNotFoundError,
    PermissionDeniedError,
)
from aletheia.modules.organizations.models import Membership, Organization
from aletheia.modules.organizations.permissions import Permission, permissions_for


@dataclass(frozen=True)
class OrganizationContext:
    """The organization a request acts on, and what the current user may do in it."""

    organization: Organization
    membership: Membership
    permissions: frozenset[Permission]


def get_organization_context(
    organization_id: uuid.UUID,
    auth: CurrentAuth,
    session: Annotated[Session, Depends(get_db_session)],
) -> OrganizationContext:
    row = session.execute(
        select(Organization, Membership)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Organization.id == organization_id, Membership.user_id == auth.user.id)
    ).one_or_none()
    if row is None:
        raise OrganizationNotFoundError()
    organization, membership = row
    return OrganizationContext(
        organization=organization,
        membership=membership,
        permissions=permissions_for(membership.role),
    )


def require_permission(permission: Permission) -> Callable[..., OrganizationContext]:
    """Build a dependency that resolves the organization and enforces one permission."""

    def dependency(
        context: Annotated[OrganizationContext, Depends(get_organization_context)],
    ) -> OrganizationContext:
        if permission not in context.permissions:
            raise PermissionDeniedError()
        return context

    return dependency
