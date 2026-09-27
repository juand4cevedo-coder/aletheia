from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.modules.identity.schemas import RegisterRequest, RegisterResponse
from aletheia.modules.identity.service import register_account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
def register(
    request: RegisterRequest, session: Annotated[Session, Depends(get_db_session)]
) -> RegisterResponse:
    return register_account(session, request)
