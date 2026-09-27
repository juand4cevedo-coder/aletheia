import pytest
from pydantic import ValidationError

from aletheia.modules.identity.schemas import RegisterRequest

VALID_DATA = {
    "email": "Ana.Perez@Example.COM",
    "password": "correct horse battery staple",
    "full_name": "  Ana Pérez  ",
    "organization_name": "  Pérez & Asociados  ",
}


def test_register_request_normalizes_email_and_names() -> None:
    request = RegisterRequest.model_validate(VALID_DATA)

    assert request.email == "ana.perez@example.com"
    assert request.full_name == "Ana Pérez"
    assert request.organization_name == "Pérez & Asociados"


def test_register_request_keeps_password_exactly_as_given() -> None:
    request = RegisterRequest.model_validate({**VALID_DATA, "password": "  spaces matter here  "})

    assert request.password == "  spaces matter here  "


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", "not-an-email"),
        ("password", "fourteen chars"),
        ("password", "x" * 129),
        ("full_name", "   "),
        ("organization_name", ""),
    ],
)
def test_register_request_rejects_invalid_values(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        RegisterRequest.model_validate({**VALID_DATA, field: value})
