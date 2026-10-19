from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# The engine owns a pool of connections, created once per process and shared.
# pool_pre_ping checks a connection is alive before handing it out, so a
# restarted database doesn't surface as errors on the next few requests.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# A factory for Sessions: a Session is a unit of work (one transaction) on top
# of a pooled connection.
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one Session per request, always closed afterwards.

    Use it as `db: Annotated[Session, Depends(get_db)]`. Tests can swap it out
    with `app.dependency_overrides[get_db]`.
    """
    with SessionLocal() as session:
        yield session
