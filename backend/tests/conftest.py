from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session

from aletheia.core.database import get_engine


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
