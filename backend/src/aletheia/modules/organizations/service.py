import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from aletheia.modules.identity.models import User
from aletheia.modules.organizations.models import Membership, Organization
from aletheia.modules.organizations.schemas import MemberSummary, OrganizationSummary


def list_user_organizations(session: Session, user_id: uuid.UUID) -> list[OrganizationSummary]:
    rows = session.execute(
        select(Organization, Membership.role)
        .join(Membership, Membership.organization_id == Organization.id)
        .where(Membership.user_id == user_id)
        .order_by(Organization.name, Organization.id)
    ).all()
    return [
        OrganizationSummary(id=organization.id, name=organization.name, role=role)
        for organization, role in rows
    ]


def rename_organization(session: Session, organization: Organization, name: str) -> None:
    organization.name = name
    session.commit()


def list_members(session: Session, organization_id: uuid.UUID) -> list[MemberSummary]:
    rows = session.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.organization_id == organization_id)
        .order_by(User.full_name, User.id)
    ).all()
    return [
        MemberSummary(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=membership.role,
            joined_at=membership.created_at,
        )
        for membership, user in rows
    ]
