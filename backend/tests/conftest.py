import uuid
from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session, get_engine
from aletheia.main import app
from tests.factories import TEST_PASSWORD, Account


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Session bound to an outer transaction that is always rolled back.

    Tests may commit freely; nothing is persisted in the database.
    """
    with get_engine().connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def api_client(db_session: Session) -> Iterator[TestClient]:
    """API client whose requests use the rolled-back test session."""
    app.dependency_overrides[get_db_session] = lambda: db_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def make_account(api_client: TestClient) -> Callable[[], Account]:
    """Factory that registers a new user with their own organization and logs them in."""

    def factory() -> Account:
        email = f"user.{uuid.uuid4().hex[:12]}@example.com"
        registered = api_client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": TEST_PASSWORD,
                "full_name": "Test User",
                "organization_name": f"Firma {uuid.uuid4().hex[:6]}",
            },
        )
        assert registered.status_code == 201
        logged_in = api_client.post(
            "/api/v1/auth/login", json={"email": email, "password": TEST_PASSWORD}
        )
        assert logged_in.status_code == 200
        return Account(
            user_id=uuid.UUID(registered.json()["user_id"]),
            organization_id=uuid.UUID(registered.json()["organization_id"]),
            email=email,
            access_token=logged_in.json()["access_token"],
        )

    return factory
