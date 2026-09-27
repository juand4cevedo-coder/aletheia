import logging
from typing import Annotated, Literal

logger = logging.getLogger(__name__)

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/health/ready",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "Database unavailable"}},
)
def readiness(session: Annotated[Session, Depends(get_db_session)]) -> HealthResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Database readiness check failed", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return HealthResponse(status="ok")
