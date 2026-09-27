import uuid
from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aletheia.modules.organizations.models import Membership, MembershipRole
from tests.factories import Account

pytestmark = pytest.mark.integration

AccountFactory = Callable[[], Account]


@pytest.fixture
def firm(
    api_client: TestClient, db_session: Session, make_account: AccountFactory
) -> dict[str, Any]:
    """An organization with a lead lawyer who owns one case, plus a second lawyer."""
    lead, colleague = make_account(), make_account()
    db_session.add(
        Membership(
            organization_id=lead.organization_id,
            user_id=colleague.user_id,
            role=MembershipRole.LAWYER,
        )
    )
    db_session.commit()
    response = api_client.post(
        f"/api/v1/organizations/{lead.organization_id}/cases",
        json={"title": "Proceso de alimentos", "description": "Descripción inicial"},
        headers=lead.headers,
    )
    assert response.status_code == 201
    return {
        "lead": lead,
        "colleague": colleague,
        "case_url": f"/api/v1/organizations/{lead.organization_id}/cases/{response.json()['id']}",
    }


def add(client: TestClient, firm: dict[str, Any], user_id: uuid.UUID, role: str) -> int:
    response = client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(user_id), "role": role},
        headers=firm["lead"].headers,
    )
    return response.status_code


# --- updating the case -------------------------------------------------------


@pytest.mark.parametrize(("role", "expected"), [("lead", 200), ("editor", 200), ("viewer", 403)])
def test_only_leads_and_editors_can_update_the_case(
    api_client: TestClient, firm: dict[str, Any], role: str, expected: int
) -> None:
    colleague = firm["colleague"]
    assert add(api_client, firm, colleague.user_id, role) == 201

    response = api_client.patch(
        firm["case_url"], json={"title": "Nuevo título"}, headers=colleague.headers
    )

    assert response.status_code == expected


def test_partial_update_changes_only_the_given_fields(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    response = api_client.patch(
        firm["case_url"], json={"description": None}, headers=firm["lead"].headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Proceso de alimentos"
    assert body["description"] is None


@pytest.mark.parametrize("title", [None, "   "])
def test_case_title_cannot_be_null_or_blank(
    api_client: TestClient, firm: dict[str, Any], title: str | None
) -> None:
    response = api_client.patch(
        firm["case_url"], json={"title": title}, headers=firm["lead"].headers
    )

    assert response.status_code == 422


def test_case_detail_exposes_the_callers_permissions(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    assert add(api_client, firm, firm["colleague"].user_id, "viewer") == 201

    response = api_client.get(firm["case_url"], headers=firm["colleague"].headers)

    assert response.json()["my_permissions"] == ["case:read"]


# --- managing members --------------------------------------------------------


def test_lead_can_add_an_organization_member_to_the_case(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    colleague = firm["colleague"]

    assert add(api_client, firm, colleague.user_id, "editor") == 201

    members = api_client.get(f"{firm['case_url']}/members", headers=firm["lead"].headers).json()
    assert {member["email"]: member["role"] for member in members} == {
        firm["lead"].email: "lead",
        colleague.email: "editor",
    }
    assert api_client.get(firm["case_url"], headers=colleague.headers).status_code == 200


def test_users_outside_the_organization_cannot_be_added(
    api_client: TestClient, firm: dict[str, Any], make_account: AccountFactory
) -> None:
    outsider = make_account()

    response = api_client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(outsider.user_id), "role": "viewer"},
        headers=firm["lead"].headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "ORGANIZATION_MEMBER_NOT_FOUND"


def test_a_member_cannot_be_added_twice(api_client: TestClient, firm: dict[str, Any]) -> None:
    assert add(api_client, firm, firm["colleague"].user_id, "viewer") == 201

    response = api_client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(firm["colleague"].user_id), "role": "editor"},
        headers=firm["lead"].headers,
    )

    assert response.status_code == 409
    assert response.json()["code"] == "CASE_MEMBER_ALREADY_EXISTS"


def test_editors_cannot_manage_members(api_client: TestClient, firm: dict[str, Any]) -> None:
    colleague = firm["colleague"]
    assert add(api_client, firm, colleague.user_id, "editor") == 201

    response = api_client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(firm["lead"].user_id), "role": "viewer"},
        headers=colleague.headers,
    )

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


def test_organization_members_outside_the_case_cannot_manage_it(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    response = api_client.post(
        f"{firm['case_url']}/members",
        json={"user_id": str(firm["colleague"].user_id), "role": "lead"},
        headers=firm["colleague"].headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "CASE_NOT_FOUND"


def test_lead_can_change_a_members_role(api_client: TestClient, firm: dict[str, Any]) -> None:
    colleague = firm["colleague"]
    assert add(api_client, firm, colleague.user_id, "viewer") == 201

    response = api_client.patch(
        f"{firm['case_url']}/members/{colleague.user_id}",
        json={"role": "editor"},
        headers=firm["lead"].headers,
    )

    assert response.status_code == 200
    assert response.json()["role"] == "editor"


def test_removed_member_loses_access(api_client: TestClient, firm: dict[str, Any]) -> None:
    colleague = firm["colleague"]
    assert add(api_client, firm, colleague.user_id, "editor") == 201

    response = api_client.delete(
        f"{firm['case_url']}/members/{colleague.user_id}", headers=firm["lead"].headers
    )

    assert response.status_code == 204
    assert api_client.get(firm["case_url"], headers=colleague.headers).status_code == 404


def test_unknown_case_member_is_reported(api_client: TestClient, firm: dict[str, Any]) -> None:
    response = api_client.delete(
        f"{firm['case_url']}/members/{uuid.uuid4()}", headers=firm["lead"].headers
    )

    assert response.status_code == 404
    assert response.json()["code"] == "CASE_MEMBER_NOT_FOUND"


# --- last lead protection ----------------------------------------------------


def test_the_last_lead_cannot_be_demoted_or_removed(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    lead = firm["lead"]
    member_url = f"{firm['case_url']}/members/{lead.user_id}"

    demote = api_client.patch(member_url, json={"role": "viewer"}, headers=lead.headers)
    remove = api_client.delete(member_url, headers=lead.headers)

    for response in (demote, remove):
        assert response.status_code == 409
        assert response.json()["code"] == "LAST_CASE_LEAD"


def test_a_lead_can_step_down_when_another_lead_remains(
    api_client: TestClient, firm: dict[str, Any]
) -> None:
    lead, colleague = firm["lead"], firm["colleague"]
    assert add(api_client, firm, colleague.user_id, "lead") == 201

    response = api_client.delete(f"{firm['case_url']}/members/{lead.user_id}", headers=lead.headers)

    assert response.status_code == 204
    assert api_client.get(firm["case_url"], headers=lead.headers).status_code == 404
    assert api_client.get(firm["case_url"], headers=colleague.headers).status_code == 200
