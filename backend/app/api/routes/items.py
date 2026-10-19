from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Item
from app.schemas.item import ItemCreate, ItemModify, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

DbSession = Annotated[Session, Depends(get_db)]


def get_item_or_404(db: Session, item_id: int) -> Item:
    item = db.get(Item, item_id)  # lookup by primary key
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")
    return item


def commit_or_409(db: Session) -> None:
    """Commit, turning a unique-constraint violation into 409 Conflict. Relying on
    the database constraint (not a check-then-insert) is race-free."""
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An item with that name exists") from exc


@router.get("", response_model=list[ItemRead])
def list_items(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Item]:
    # SQLAlchemy 2.x style: build a select(), then execute it. Always order when paginating.
    stmt = select(Item).order_by(Item.id).limit(limit).offset(offset)
    return list(db.scalars(stmt))


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: DbSession) -> Item:
    return get_item_or_404(db, item_id)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: DbSession) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    commit_or_409(db)
    db.refresh(item)  # reload DB-generated values (id, timestamps)
    return item


@router.put("/{item_id}", response_model=ItemRead)
def replace_item(item_id: int, payload: ItemModify, db: DbSession) -> Item:
    item = get_item_or_404(db, item_id)
    item.name = payload.name
    item.description = payload.description
    commit_or_409(db)
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, payload: ItemUpdate, db: DbSession) -> Item:
    item = get_item_or_404(db, item_id)
    # exclude_unset: only the fields the client actually sent.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    commit_or_409(db)
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: DbSession) -> Response:
    db.delete(get_item_or_404(db, item_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
