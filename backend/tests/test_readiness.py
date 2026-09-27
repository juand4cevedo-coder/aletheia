from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from aletheia.core.database import get_db_session
from aletheia.main import app


class FailingSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", None, Exception("connection refused"))


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_readiness_returns_503_when_database_is_unavailable(client: TestClient) -> None:
    app.dependency_overrides[get_db_session] = FailingSession

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


@pytest.mark.integration
def test_readiness_returns_ok_when_database_is_available(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
