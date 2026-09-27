from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from aletheia.core.database import get_db_session
from aletheia.core.storage import StorageError, get_storage
from aletheia.main import app


class FailingSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", None, Exception("connection refused"))


class HealthySession:
    def execute(self, *args: object, **kwargs: object) -> None:
        return None


class FailingStorage:
    def check_ready(self) -> None:
        raise StorageError("bucket unreachable")


class HealthyStorage:
    def check_ready(self) -> None:
        return None


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def assert_unavailable(response_json: dict[str, str], request_id: str) -> None:
    assert response_json == {
        "code": "SERVICE_UNAVAILABLE",
        "message": "The service is temporarily unavailable.",
        "request_id": request_id,
    }


def test_readiness_returns_503_when_database_is_unavailable(client: TestClient) -> None:
    app.dependency_overrides[get_db_session] = FailingSession
    app.dependency_overrides[get_storage] = HealthyStorage

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert_unavailable(response.json(), response.headers["X-Request-ID"])


def test_readiness_returns_503_when_storage_is_unavailable(client: TestClient) -> None:
    app.dependency_overrides[get_db_session] = HealthySession
    app.dependency_overrides[get_storage] = FailingStorage

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert_unavailable(response.json(), response.headers["X-Request-ID"])


@pytest.mark.integration
def test_readiness_returns_ok_when_dependencies_are_available(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
