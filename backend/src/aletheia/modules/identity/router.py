from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.core.errors import ErrorResponse
from aletheia.modules.identity import sessions
from aletheia.modules.identity.dependencies import CurrentAuth
from aletheia.modules.identity.schemas import (
    CurrentUserResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from aletheia.modules.identity.service import register_account

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[Session, Depends(get_db_session)]
UNAUTHORIZED: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}
}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    },
)
def register(request: RegisterRequest, session: DbSession) -> RegisterResponse:
    return register_account(session, request)


@router.post("/login", responses=UNAUTHORIZED)
def login(request: LoginRequest, session: DbSession) -> TokenResponse:
    return sessions.login(session, request)


@router.post("/refresh", responses=UNAUTHORIZED)
def refresh(request: RefreshRequest, session: DbSession) -> TokenResponse:
    return sessions.refresh(session, request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, responses=UNAUTHORIZED)
def logout(auth: CurrentAuth, session: DbSession) -> None:
    sessions.logout(session, auth.auth_session)


@router.get("/me", responses=UNAUTHORIZED)
def me(auth: CurrentAuth) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=auth.user.id, email=auth.user.email, full_name=auth.user.full_name
    )
