import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse, ServiceUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/ready", responses={503: {"model": ErrorResponse}})
def readiness(session: Annotated[Session, Depends(get_db_session)]) -> HealthResponse:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.warning("Database readiness check failed", exc_info=exc)
        raise ServiceUnavailableError() from exc
    return HealthResponse(status="ok")
