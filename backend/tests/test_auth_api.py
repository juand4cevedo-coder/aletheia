import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from aletheia.core.tokens import hash_token
from aletheia.modules.identity.models import AuthSession, User

pytestmark = pytest.mark.integration

PASSWORD = "correct horse battery staple"


@pytest.fixture
def credentials(api_client: TestClient) -> dict[str, str]:
    email = f"ana.{uuid.uuid4().hex[:12]}@example.com"
    response = api_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": PASSWORD,
            "full_name": "Ana Pérez",
            "organization_name": "Pérez & Asociados",
        },
    )
    assert response.status_code == 201
    return {"email": email, "password": PASSWORD}


@pytest.fixture
def tokens(api_client: TestClient, credentials: dict[str, str]) -> dict[str, Any]:
    response = api_client.post("/api/v1/auth/login", json=credentials)
    assert response.status_code == 200
    return response.json()


def bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def me_status(client: TestClient, access_token: str) -> int:
    return client.get("/api/v1/auth/me", headers=bearer(access_token)).status_code


def refresh_status(client: TestClient, refresh_token: str) -> int:
    return client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}).status_code


def session_for(db_session: Session, access_token: str) -> AuthSession:
    return db_session.scalars(
        select(AuthSession).where(AuthSession.access_token_hash == hash_token(access_token))
    ).one()


# --- login -------------------------------------------------------------------


def test_login_returns_a_token_pair(tokens: dict[str, Any]) -> None:
    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] == 15 * 60
    assert tokens["access_token"] != tokens["refresh_token"]


def test_login_accepts_email_in_any_case(
    api_client: TestClient, credentials: dict[str, str]
) -> None:
    response = api_client.post(
        "/api/v1/auth/login", json={**credentials, "email": credentials["email"].upper()}
    )

    assert response.status_code == 200


def test_login_stores_only_token_hashes(db_session: Session, tokens: dict[str, Any]) -> None:
    auth_session = session_for(db_session, tokens["access_token"])

    assert auth_session.access_token_hash != tokens["access_token"]
    assert auth_session.refresh_token_hash == hash_token(tokens["refresh_token"])


def test_wrong_password_and_unknown_email_get_the_same_response(
    api_client: TestClient, credentials: dict[str, str]
) -> None:
    wrong_password = api_client.post(
        "/api/v1/auth/login", json={**credentials, "password": "not the right password"}
    )
    unknown_email = api_client.post(
        "/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
    )

    for response in (wrong_password, unknown_email):
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"
    assert wrong_password.json()["message"] == unknown_email.json()["message"]


def test_inactive_user_cannot_log_in(
    api_client: TestClient, db_session: Session, credentials: dict[str, str]
) -> None:
    user = db_session.scalars(select(User).where(User.email == credentials["email"])).one()
    user.is_active = False
    db_session.commit()

    response = api_client.post("/api/v1/auth/login", json=credentials)

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


# --- access token ------------------------------------------------------------


def test_me_returns_the_authenticated_user(
    api_client: TestClient, credentials: dict[str, str], tokens: dict[str, Any]
) -> None:
    response = api_client.get("/api/v1/auth/me", headers=bearer(tokens["access_token"]))

    assert response.status_code == 200
    assert response.json()["email"] == credentials["email"]


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer invalid-token"}, {"Authorization": "Basic abc"}],
)
def test_me_rejects_missing_or_invalid_credentials(
    api_client: TestClient, headers: dict[str, str]
) -> None:
    response = api_client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_expired_access_token_is_rejected(
    api_client: TestClient, db_session: Session, tokens: dict[str, Any]
) -> None:
    auth_session = session_for(db_session, tokens["access_token"])
    auth_session.access_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()

    assert me_status(api_client, tokens["access_token"]) == 401


# --- refresh -----------------------------------------------------------------


def test_refresh_rotates_both_tokens(api_client: TestClient, tokens: dict[str, Any]) -> None:
    response = api_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )

    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["access_token"] != tokens["access_token"]
    assert new_tokens["refresh_token"] != tokens["refresh_token"]
    assert me_status(api_client, tokens["access_token"]) == 401
    assert me_status(api_client, new_tokens["access_token"]) == 200


def test_reusing_a_rotated_refresh_token_revokes_the_session(
    api_client: TestClient, db_session: Session, tokens: dict[str, Any]
) -> None:
    rotated = api_client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    ).json()

    reuse = api_client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert reuse.status_code == 401
    assert reuse.json()["code"] == "INVALID_REFRESH_TOKEN"
    assert session_for(db_session, rotated["access_token"]).revocation_reason == (
        "refresh_token_reuse"
    )
    assert me_status(api_client, rotated["access_token"]) == 401
    assert refresh_status(api_client, rotated["refresh_token"]) == 401


def test_unknown_refresh_token_is_rejected(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/refresh", json={"refresh_token": "unknown"})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_REFRESH_TOKEN"


def test_expired_session_cannot_be_refreshed(
    api_client: TestClient, db_session: Session, tokens: dict[str, Any]
) -> None:
    auth_session = session_for(db_session, tokens["access_token"])
    auth_session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()

    assert refresh_status(api_client, tokens["refresh_token"]) == 401


# --- logout ------------------------------------------------------------------


def test_logout_revokes_the_session_immediately(
    api_client: TestClient, db_session: Session, tokens: dict[str, Any]
) -> None:
    auth_session = session_for(db_session, tokens["access_token"])

    response = api_client.post("/api/v1/auth/logout", headers=bearer(tokens["access_token"]))

    assert response.status_code == 204
    assert auth_session.revocation_reason == "logout"
    assert me_status(api_client, tokens["access_token"]) == 401
    assert refresh_status(api_client, tokens["refresh_token"]) == 401
