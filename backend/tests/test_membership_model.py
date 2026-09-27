import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.core.security import hash_password
from aletheia.modules.identity.models import User
from aletheia.modules.organizations.models import Membership, MembershipRole, Organization

pytestmark = pytest.mark.integration


@pytest.fixture
def organization(db_session: Session) -> Organization:
    organization = Organization(name="Firma de prueba")
    db_session.add(organization)
    db_session.flush()
    return organization


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(
        email="abogada@example.com",
        full_name="Ana Pérez",
        password_hash=hash_password("correct horse battery staple"),
    )
    db_session.add(user)
    db_session.flush()
    return user


def test_membership_links_user_and_organization_with_a_role(
    db_session: Session, organization: Organization, user: User
) -> None:
    db_session.add(
        Membership(organization_id=organization.id, user_id=user.id, role=MembershipRole.OWNER)
    )
    db_session.commit()

    stored = db_session.get(Membership, (organization.id, user.id))

    assert stored is not None
    assert stored.role is MembershipRole.OWNER


def test_user_cannot_have_two_memberships_in_the_same_organization(
    db_session: Session, organization: Organization, user: User
) -> None:
    db_session.add(
        Membership(organization_id=organization.id, user_id=user.id, role=MembershipRole.OWNER)
    )
    db_session.flush()
    db_session.expunge_all()
    db_session.add(
        Membership(organization_id=organization.id, user_id=user.id, role=MembershipRole.LAWYER)
    )

    with pytest.raises(IntegrityError, match="pk_memberships"):
        db_session.flush()


def test_membership_requires_an_existing_organization(db_session: Session, user: User) -> None:
    db_session.add(
        Membership(organization_id=uuid.uuid4(), user_id=user.id, role=MembershipRole.OWNER)
    )

    with pytest.raises(IntegrityError, match="fk_memberships_organization_id_organizations"):
        db_session.flush()


def test_membership_role_is_restricted_at_database_level(
    db_session: Session, organization: Organization, user: User
) -> None:
    statement = text(
        "INSERT INTO memberships (organization_id, user_id, role) "
        "VALUES (:organization_id, :user_id, 'superuser')"
    )

    with pytest.raises(IntegrityError, match="ck_memberships_role_valid"):
        db_session.execute(statement, {"organization_id": organization.id, "user_id": user.id})
