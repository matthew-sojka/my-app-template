"""ORM models, one module per resource.

Import every model module here so its tables register on `Base.metadata`;
Alembic imports this package to see the full schema when autogenerating.
"""

from app.models.item import Item

__all__ = ["Item"]
