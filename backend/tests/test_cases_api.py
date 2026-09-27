import re
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.modules.cases.models import CaseMember, CaseRole
from aletheia.modules.organizations.models import Membership, MembershipRole
from tests.factories import Account

pytestmark = pytest.mark.integration

AccountFactory = Callable[[], Account]


def cases_url(organization_id: uuid.UUID, suffix: str = "") -> str:
    return f"/api/v1/organizations/{organization_id}/cases{suffix}"


def add_member(
    session: Session, organization_id: uuid.UUID, user_id: uuid.UUID, role: MembershipRole
) -> None:
    session.add(Membership(organization_id=organization_id, user_id=user_id, role=role))
    session.commit()


def create_case(
    client: TestClient,
    account: Account,
    organization_id: uuid.UUID | None = None,
    title: str = "Proceso de alimentos",
) -> dict[str, Any]:
    """Create a case as `account`, in their own organization unless another is given."""
    response = client.post(
        cases_url(organization_id or account.organization_id),
        json={"title": title},
        headers=account.headers,
    )
    assert response.status_code == 201
    return response.json()


# --- creation ----------------------------------------------------------------


def test_creating_a_case_assigns_a_reference_and_makes_the_creator_lead(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()

    case = create_case(api_client, owner)

    year = datetime.now(UTC).year
    assert case["reference"] == f"CAS-{year}-000001"
    assert case["status"] == "active"
    assert case["my_role"] == "lead"


def test_references_are_consecutive_within_an_organization(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()

    references = [create_case(api_client, owner)["reference"] for _ in range(3)]

    assert [reference[-6:] for reference in references] == ["000001", "000002", "000003"]
    assert all(re.fullmatch(r"CAS-\d{4}-\d{6}", reference) for reference in references)


def test_each_organization_has_its_own_numbering(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    alice, bob = make_account(), make_account()
    create_case(api_client, alice)
    create_case(api_client, alice)

    bobs_first_case = create_case(api_client, bob)

    assert bobs_first_case["reference"].endswith("-000001")


@pytest.mark.parametrize("role", [MembershipRole.ADMIN, MembershipRole.COLLABORATOR])
def test_roles_without_case_create_cannot_create_cases(
    api_client: TestClient, db_session: Session, make_account: AccountFactory, role: MembershipRole
) -> None:
    owner, member = make_account(), make_account()
    add_member(db_session, owner.organization_id, member.user_id, role)

    response = api_client.post(
        cases_url(owner.organization_id), json={"title": "Caso"}, headers=member.headers
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_case_title_cannot_be_blank(api_client: TestClient, make_account: AccountFactory) -> None:
    owner = make_account()

    response = api_client.post(
        cases_url(owner.organization_id), json={"title": "   "}, headers=owner.headers
    )

    assert response.status_code == 422


# --- per-case access ---------------------------------------------------------


def test_organization_members_only_see_cases_they_belong_to(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> None:
    owner, lawyer = make_account(), make_account()
    add_member(db_session, owner.organization_id, lawyer.user_id, MembershipRole.LAWYER)
    owners_case = create_case(api_client, owner)
    lawyers_case = create_case(api_client, lawyer, owner.organization_id)

    listed = api_client.get(cases_url(owner.organization_id), headers=lawyer.headers)
    direct = api_client.get(
        cases_url(owner.organization_id, f"/{owners_case['id']}"), headers=lawyer.headers
    )

    assert [case["id"] for case in listed.json()] == [lawyers_case["id"]]
    assert direct.status_code == 404
    assert direct.json()["code"] == "CASE_NOT_FOUND"


def test_case_member_can_read_the_case(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    owner = make_account()
    case = create_case(api_client, owner)

    response = api_client.get(
        cases_url(owner.organization_id, f"/{case['id']}"), headers=owner.headers
    )

    assert response.status_code == 200
    assert response.json()["reference"] == case["reference"]


# --- tenant isolation --------------------------------------------------------


def test_case_cannot_be_reached_through_another_organization(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> None:
    alice, bob = make_account(), make_account()
    add_member(db_session, bob.organization_id, alice.user_id, MembershipRole.LAWYER)
    alices_case = create_case(api_client, alice)

    response = api_client.get(
        cases_url(bob.organization_id, f"/{alices_case['id']}"), headers=alice.headers
    )

    assert response.status_code == 404
    assert response.json()["code"] == "CASE_NOT_FOUND"


def test_other_tenants_cannot_list_or_read_cases(
    api_client: TestClient, make_account: AccountFactory
) -> None:
    alice, mallory = make_account(), make_account()
    case = create_case(api_client, alice)

    listed = api_client.get(cases_url(alice.organization_id), headers=mallory.headers)
    direct = api_client.get(
        cases_url(alice.organization_id, f"/{case['id']}"), headers=mallory.headers
    )

    for response in (listed, direct):
        assert response.status_code == 404
        assert response.json()["code"] == "ORGANIZATION_NOT_FOUND"


def test_database_rejects_case_members_from_another_organization(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> None:
    alice, mallory = make_account(), make_account()
    case = create_case(api_client, alice)

    db_session.add(
        CaseMember(
            case_id=uuid.UUID(case["id"]),
            user_id=mallory.user_id,
            organization_id=alice.organization_id,
            role=CaseRole.VIEWER,
        )
    )

    with pytest.raises(IntegrityError, match="fk_case_members_membership"):
        db_session.flush()
