from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session, get_engine
from aletheia.main import app


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
