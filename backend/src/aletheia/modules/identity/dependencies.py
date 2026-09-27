from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from aletheia.core.database import get_db_session
from aletheia.modules.identity.errors import NotAuthenticatedError
from aletheia.modules.identity.sessions import AuthContext, authenticate

_bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    session: Annotated[Session, Depends(get_db_session)],
) -> AuthContext:
    if credentials is None:
        raise NotAuthenticatedError()
    auth_context = authenticate(session, credentials.credentials)
    if auth_context is None:
        raise NotAuthenticatedError()
    return auth_context


CurrentAuth = Annotated[AuthContext, Depends(get_auth_context)]
