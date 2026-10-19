"""Alembic migration environment: runs whenever you call an `alembic` command.

It's wired to the app rather than to alembic.ini, so migrations use the same
DATABASE_URL (from Settings) and the same model metadata as the running API.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.models  # noqa: F401  (registers every model's table on Base.metadata)
from alembic import context
from app.core.config import settings
from app.db.base import Base

config = context.config

# Set up Python logging from the [loggers] sections of alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# What `alembic revision --autogenerate` diffs the live database against.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """'Offline' mode (`alembic upgrade head --sql`): print the SQL instead of
    running it, e.g. for a DBA to review. No database connection needed."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """'Online' mode (the default): connect and apply migrations directly."""
    # NullPool: a one-off CLI run doesn't need a connection pool.
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
