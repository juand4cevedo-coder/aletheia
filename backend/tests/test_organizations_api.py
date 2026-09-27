import uuid
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aletheia.modules.organizations.models import Membership, MembershipRole, Organization
from aletheia.modules.organizations.permissions import Permission
from tests.factories import Account

pytestmark = pytest.mark.integration

AccountFactory = Callable[[], Account]


def organization_url(organization_id: uuid.UUID, suffix: str = "") -> str:
    return f"/api/v1/organizations/{organization_id}{suffix}"


def add_member(
    session: Session, organization_id: uuid.UUID, user_id: uuid.UUID, role: MembershipRole
) -> None:
    session.add(Membership(organization_id=organization_id, user_id=user_id, role=role))
    session.commit()


# --- own organization --------------------------------------------------------


def test_owner_sees_their_organization_with_all_permissions(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()

    response = api_client.get(organization_url(owner.organization_id), headers=owner.headers)

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "owner"
    assert set(body["permissions"]) == {permission.value for permission in Permission}


def test_list_returns_only_the_users_organizations(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    alice, bob = make_account(), make_account()

    response = api_client.get("/api/v1/organizations", headers=alice.headers)

    assert response.status_code == 200
    ids = {organization["id"] for organization in response.json()}
    assert ids == {str(alice.organization_id)}
    assert str(bob.organization_id) not in ids


def test_owner_can_rename_their_organization(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()

    response = api_client.patch(
        organization_url(owner.organization_id),
        json={"name": "  Nuevo nombre  "},
        headers=owner.headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Nuevo nombre"


def test_organization_endpoints_require_authentication(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()

    response = api_client.get(organization_url(owner.organization_id))

    assert response.status_code == 401


# --- tenant isolation --------------------------------------------------------


@pytest.mark.parametrize(("method", "suffix"), [("GET", ""), ("PATCH", ""), ("GET", "/members")])
def test_other_tenants_organization_is_indistinguishable_from_a_missing_one(
    api_client: TestClient, make_account: AccountFactory, method: str, suffix: str
) -> None:
    alice, bob = make_account(), make_account()
    body = {"name": "Hijacked"} if method == "PATCH" else None

    other_tenant = api_client.request(
        method, organization_url(bob.organization_id, suffix), headers=alice.headers, json=body
    )
    missing = api_client.request(
        method, organization_url(uuid.uuid4(), suffix), headers=alice.headers, json=body
    )

    for response in (other_tenant, missing):
        assert response.status_code == 404
        assert response.json()["code"] == "ORGANIZATION_NOT_FOUND"
    assert other_tenant.json()["message"] == missing.json()["message"]


def test_failed_cross_tenant_update_does_not_modify_the_organization(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> None:
    alice, bob = make_account(), make_account()
    organization = db_session.get(Organization, bob.organization_id)
    assert organization is not None
    original_name = organization.name

    api_client.patch(
        organization_url(bob.organization_id), json={"name": "Hijacked"}, headers=alice.headers
    )

    db_session.refresh(organization)
    assert organization.name == original_name


# --- role-based access -------------------------------------------------------

ROLE_MATRIX = [
    # role, can update organization, can read members
    (MembershipRole.ADMIN, True, True),
    (MembershipRole.LAWYER, False, True),
    (MembershipRole.COLLABORATOR, False, False),
    (MembershipRole.AUDITOR, False, True),
]


@pytest.mark.parametrize(("role", "can_update", "can_read_members"), ROLE_MATRIX)
def test_permissions_are_enforced_per_role(
    api_client: TestClient,
    db_session: Session,
    make_account: AccountFactory,
    role: MembershipRole,
    can_update: bool,
    can_read_members: bool,
) -> None:
    owner, member = make_account(), make_account()
    add_member(db_session, owner.organization_id, member.user_id, role)
    url = organization_url(owner.organization_id)

    read = api_client.get(url, headers=member.headers)
    update = api_client.patch(url, json={"name": "Renamed"}, headers=member.headers)
    members = api_client.get(
        organization_url(owner.organization_id, "/members"), headers=member.headers
    )

    assert read.status_code == 200
    assert read.json()["role"] == role.value
    assert update.status_code == (200 if can_update else 403)
    assert members.status_code == (200 if can_read_members else 403)
    if not can_update:
        assert update.json()["code"] == "PERMISSION_DENIED"


def test_members_list_shows_every_member_with_their_role(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> None:
    owner, lawyer = make_account(), make_account()
    add_member(db_session, owner.organization_id, lawyer.user_id, MembershipRole.LAWYER)

    response = api_client.get(
        organization_url(owner.organization_id, "/members"), headers=owner.headers
    )

    assert response.status_code == 200
    roles = {member["email"]: member["role"] for member in response.json()}
    assert roles == {owner.email: "owner", lawyer.email: "lawyer"}
