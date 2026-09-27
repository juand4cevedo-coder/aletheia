import enum
from collections.abc import Iterator
from datetime import datetime
from functools import lru_cache

from sqlalchemy import URL, DateTime, Engine, Enum, MetaData, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from aletheia.core.config import get_settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }


def enum_values_check(column: str, values: type[enum.StrEnum]) -> str:
    """SQL condition that restricts `column` to the values of a string enum."""
    listed = ", ".join(f"'{member.value}'" for member in values)
    return f"{column} IN ({listed})"


def string_enum(enum_class: type[enum.StrEnum]) -> Enum:
    """Store a string enum as VARCHAR (not a native PostgreSQL ENUM), using its values."""
    return Enum(
        enum_class,
        native_enum=False,
        create_constraint=False,
        length=32,
        values_callable=lambda members: [member.value for member in members],
    )


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


def violated_constraint(error: IntegrityError) -> str | None:
    """Return the name of the database constraint that caused an IntegrityError."""
    diagnostics = getattr(error.orig, "diag", None)
    return getattr(diagnostics, "constraint_name", None)
