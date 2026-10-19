from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Response shape. FastAPI validates the output against this and
    publishes it in the OpenAPI schema, which the frontend can generate types from."""

    status: Literal["ok", "degraded"]
    environment: str
    database: Literal["ok", "unavailable"]


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthResponse,
            "description": "Database unreachable",
        }
    },
)
def health(db: Annotated[Session, Depends(get_db)], response: Response) -> HealthResponse:
    """Is the API up and can it reach the database?

    Returns 200 when everything is fine. If the database is unreachable it returns
    503 with the same body shape, so callers see which part failed while load
    balancers stop routing traffic to this instance.
    """
    try:
        db.execute(text("SELECT 1"))
        database: Literal["ok", "unavailable"] = "ok"
    except SQLAlchemyError:
        database = "unavailable"
        # The injected Response lets us set the status code but still return the model.
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="ok" if database == "ok" else "degraded",
        environment=settings.environment,
        database=database,
    )
