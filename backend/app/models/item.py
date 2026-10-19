from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Item(Base):
    """Example resource showing the full pattern (model → migration → schemas → routes → tests).
    Copy it for real resources, then delete it."""

    __tablename__ = "items"

    # Mapped[...] type hints drive both Python typing and column types/nullability:
    # Mapped[str] is NOT NULL, Mapped[str | None] is nullable.
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(1000))
    # server_default: the database fills it in, so it's correct even for rows
    # inserted outside the app (psql, scripts). Base maps datetime → `timestamptz`.
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
