from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

import aletheia.modules.cases.models  # noqa: F401  (registers models on Base.metadata)
import aletheia.modules.evidence.models  # noqa: F401  (registers models on Base.metadata)
import aletheia.modules.identity.models  # noqa: F401  (registers models on Base.metadata)
import aletheia.modules.organizations.models  # noqa: F401  (registers models on Base.metadata)
from aletheia.core.database import Base, build_database_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=build_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(build_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
