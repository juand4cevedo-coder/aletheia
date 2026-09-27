from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from aletheia.core.config import get_settings


def build_database_url() -> URL:
    settings = get_settings()
    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password.get_secret_value(),
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        build_database_url(),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db_session() -> Iterator[Session]:
    with get_session_factory()() as session:
        yield session
