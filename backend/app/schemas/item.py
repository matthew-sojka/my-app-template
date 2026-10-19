from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class ItemCreate(ItemBase):
    """Request body for POST."""


class ItemModify(ItemBase):
    """Request body for PUT: all fields required; replaces the whole object."""


class ItemUpdate(BaseModel):
    """Request body for PATCH: every field optional; only the fields sent are changed."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name")
    @classmethod
    def name_not_null(cls, value: str | None) -> str:
        # Omitting `name` leaves it unchanged; sending `"name": null` is an error,
        # since the column is NOT NULL. (Validators don't run on omitted fields.)
        if value is None:
            raise ValueError("name cannot be null")
        return value


class ItemRead(ItemBase):
    """Response body. from_attributes lets FastAPI build it straight from an ORM object."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
