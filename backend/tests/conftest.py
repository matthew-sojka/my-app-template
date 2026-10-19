import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from alembic import command
from app.db.session import engine, get_db
from app.main import app

BACKEND_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def require_db() -> None:
    """Skip a test when Postgres isn't reachable (start it with `docker compose up db`).

    In CI (GitHub Actions sets CI=true) a missing database fails instead: a broken
    Postgres service must not turn into a green build with the DB tests skipped.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except OperationalError as exc:
        if os.environ.get("CI") == "true":
            raise RuntimeError("Postgres not reachable at DATABASE_URL in CI") from exc
        pytest.skip("Postgres not reachable at DATABASE_URL")


@pytest.fixture(scope="session")
def migrated_db(require_db: None) -> None:
    """Bring the schema up to date once per test run, exactly as a deploy would."""
    command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")


@pytest.fixture
def db_session(migrated_db: None) -> Iterator[Session]:
    """A Session whose work is rolled back after each test, so tests never leave
    data behind or see each other's rows.

    How: open an outer transaction on one connection and never commit it. With
    join_transaction_mode="create_savepoint", the app's `db.commit()` / `db.rollback()`
    only release / roll back SAVEPOINTs inside it, so app code runs unmodified.
    """
    with engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """Test client whose requests use the rolled-back `db_session`."""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
