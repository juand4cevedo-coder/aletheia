import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from aletheia.modules.identity.models import User
from aletheia.modules.organizations.models import Membership, MembershipRole, Organization

pytestmark = pytest.mark.integration

REGISTER_URL = "/api/v1/auth/register"


@pytest.fixture
def payload() -> dict[str, Any]:
    """Registration data with a unique email, so tests never collide with existing rows."""
    return {
        "email": f"Ana.{uuid.uuid4().hex[:12]}@Example.com",
        "password": "correct horse battery staple",
        "full_name": "Ana Pérez",
        "organization_name": "Pérez & Asociados",
    }


def count_rows(session: Session) -> tuple[int, int, int]:
    return (
        session.scalar(select(func.count()).select_from(User)) or 0,
        session.scalar(select(func.count()).select_from(Organization)) or 0,
        session.scalar(select(func.count()).select_from(Membership)) or 0,
    )


def test_register_creates_user_organization_and_owner_membership(
    api_client: TestClient, db_session: Session, payload: dict[str, Any]
) -> None:
    response = api_client.post(REGISTER_URL, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"user_id", "organization_id"}

    user = db_session.get(User, uuid.UUID(body["user_id"]))
    assert user is not None
    assert user.email == payload["email"].lower()
    assert user.password_hash.startswith("$argon2id$")

    membership = db_session.get(
        Membership, (uuid.UUID(body["organization_id"]), uuid.UUID(body["user_id"]))
    )
    assert membership is not None
    assert membership.role is MembershipRole.OWNER


def test_register_rejects_an_existing_email_without_side_effects(
    api_client: TestClient, db_session: Session, payload: dict[str, Any]
) -> None:
    api_client.post(REGISTER_URL, json=payload)
    rows_before = count_rows(db_session)

    response = api_client.post(
        REGISTER_URL,
        json={**payload, "email": payload["email"].upper(), "organization_name": "Otra firma"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_REGISTERED"
    assert count_rows(db_session) == rows_before


def test_register_validation_error_does_not_echo_the_password(
    api_client: TestClient, payload: dict[str, Any]
) -> None:
    response = api_client.post(REGISTER_URL, json={**payload, "password": "short-secret"})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert response.json()["details"][0]["field"] == "body.password"
    assert "short-secret" not in response.text
