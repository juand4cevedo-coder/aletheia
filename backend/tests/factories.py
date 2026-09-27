import uuid
from dataclasses import dataclass

TEST_PASSWORD = "correct horse battery staple"


@dataclass(frozen=True)
class Account:
    """A registered and logged-in user who owns their own organization."""

    user_id: uuid.UUID
    organization_id: uuid.UUID
    email: str
    access_token: str

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}
