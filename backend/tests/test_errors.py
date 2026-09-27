import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from aletheia.core.errors import AppError, register_error_handlers
from aletheia.core.request_id import REQUEST_ID_HEADER, RequestIdMiddleware


class PaymentRequiredError(AppError):
    status_code = 402
    code = "PAYMENT_REQUIRED"
    message = "Your subscription does not allow this operation."


class Payload(BaseModel):
    name: str
    age: int


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)
    register_error_handlers(app)

    @app.get("/ok")
    def ok() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/app-error")
    def app_error() -> None:
        raise PaymentRequiredError()

    @app.get("/unexpected")
    def unexpected() -> None:
        raise RuntimeError("database password is hunter2")

    @app.post("/payload")
    def payload(data: Payload) -> Payload:
        return data

    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(build_app(), raise_server_exceptions=False)


def test_every_response_has_a_unique_request_id(client: TestClient) -> None:
    first = client.get("/ok")
    second = client.get("/ok")

    assert len(first.headers[REQUEST_ID_HEADER]) == 32
    assert first.headers[REQUEST_ID_HEADER] != second.headers[REQUEST_ID_HEADER]


def test_client_supplied_request_id_is_ignored(client: TestClient) -> None:
    response = client.get("/ok", headers={REQUEST_ID_HEADER: "attacker-controlled"})

    assert response.headers[REQUEST_ID_HEADER] != "attacker-controlled"


def test_app_error_uses_the_standard_error_format(client: TestClient) -> None:
    response = client.get("/app-error")

    assert response.status_code == 402
    assert response.json() == {
        "code": "PAYMENT_REQUIRED",
        "message": "Your subscription does not allow this operation.",
        "request_id": response.headers[REQUEST_ID_HEADER],
    }


def test_unknown_route_uses_the_standard_error_format(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
    assert response.json()["request_id"] == response.headers[REQUEST_ID_HEADER]


def test_validation_error_lists_fields_without_echoing_input(client: TestClient) -> None:
    response = client.post("/payload", json={"name": "Ana", "age": "secret-value"})

    body = response.json()
    assert response.status_code == 422
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"][0]["field"] == "body.age"
    assert "secret-value" not in response.text


def test_unexpected_error_hides_internal_details(client: TestClient) -> None:
    response = client.get("/unexpected")

    assert response.status_code == 500
    assert response.json() == {
        "code": "INTERNAL_ERROR",
        "message": "An unexpected error occurred.",
        "request_id": response.headers[REQUEST_ID_HEADER],
    }
    assert "hunter2" not in response.text
