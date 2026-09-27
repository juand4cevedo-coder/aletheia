import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aletheia.core.security import hash_password
from aletheia.modules.identity.models import User

pytestmark = pytest.mark.integration


def make_user(email: str = "abogada@example.com") -> User:
    return User(
        email=email,
        full_name="Ana Pérez",
        password_hash=hash_password("correct horse battery staple"),
    )


def test_user_is_persisted_with_secure_defaults(db_session: Session) -> None:
    user = make_user()
    db_session.add(user)
    db_session.commit()

    stored = db_session.get(User, user.id)

    assert stored is not None
    assert stored.is_active is True
    assert stored.email_verified_at is None
    assert stored.password_hash.startswith("$argon2id$")


def test_user_email_must_be_unique(db_session: Session) -> None:
    db_session.add(make_user())
    db_session.flush()
    db_session.add(make_user())

    with pytest.raises(IntegrityError, match="uq_users_email"):
        db_session.flush()


def test_user_email_must_be_lowercase(db_session: Session) -> None:
    db_session.add(make_user(email="Abogada@Example.com"))

    with pytest.raises(IntegrityError, match="ck_users_email_lowercase"):
        db_session.flush()
