from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase

# Deterministic names for indexes and constraints. Without this, Postgres picks
# names itself, and Alembic can't reliably find (or drop) them in later migrations.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Parent class for all ORM models. Its `metadata` collects every table,
    which is what Alembic compares against the database to autogenerate migrations."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Default column type per Python type in `Mapped[...]` hints. Store every
    # datetime timezone-aware (Postgres `timestamptz`) to avoid naive-time bugs.
    type_annotation_map = {datetime: DateTime(timezone=True)}
