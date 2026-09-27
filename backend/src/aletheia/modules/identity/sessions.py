from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from aletheia.core.config import get_settings
from aletheia.core.security import hash_password, password_needs_rehash, verify_password
from aletheia.core.tokens import generate_token, hash_token
from aletheia.modules.identity.errors import InvalidCredentialsError, InvalidRefreshTokenError
from aletheia.modules.identity.models import AuthSession, User
from aletheia.modules.identity.schemas import LoginRequest, TokenResponse

# Verified when the email does not exist, so both failure paths cost the same time.
_DUMMY_PASSWORD_HASH = hash_password("aletheia-timing-equalization-placeholder")


@dataclass(frozen=True)
class AuthContext:
    user: User
    auth_session: AuthSession


def _now() -> datetime:
    return datetime.now(UTC)


def _issue_tokens(auth_session: AuthSession, now: datetime) -> TokenResponse:
    """Generate a fresh token pair, store only their hashes and return the plaintext pair."""
    ttl = timedelta(minutes=get_settings().access_token_ttl_minutes)
    access_token = generate_token()
    refresh_token = generate_token()
    auth_session.access_token_hash = hash_token(access_token)
    auth_session.access_expires_at = now + ttl
    auth_session.refresh_token_hash = hash_token(refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(ttl.total_seconds()),
    )


def login(session: Session, request: LoginRequest) -> TokenResponse:
    user = session.scalars(select(User).where(User.email == request.email)).one_or_none()

    if user is None:
        verify_password(password=request.password, password_hash=_DUMMY_PASSWORD_HASH)
        raise InvalidCredentialsError()
    if not verify_password(password=request.password, password_hash=user.password_hash):
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InvalidCredentialsError()

    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(request.password)

    now = _now()
    auth_session = AuthSession(
        user_id=user.id,
        expires_at=now + timedelta(days=get_settings().session_ttl_days),
    )
    tokens = _issue_tokens(auth_session, now)
    session.add(auth_session)
    session.commit()
    return tokens


def authenticate(session: Session, access_token: str) -> AuthContext | None:
    now = _now()
    statement = (
        select(AuthSession, User)
        .join(User, User.id == AuthSession.user_id)
        .where(
            AuthSession.access_token_hash == hash_token(access_token),
            AuthSession.access_expires_at > now,
            AuthSession.expires_at > now,
            AuthSession.revoked_at.is_(None),
            User.is_active.is_(True),
        )
    )
    row = session.execute(statement).one_or_none()
    if row is None:
        return None
    auth_session, user = row
    return AuthContext(user=user, auth_session=auth_session)


def refresh(session: Session, refresh_token: str) -> TokenResponse:
    token_hash = hash_token(refresh_token)
    auth_session = session.scalars(
        select(AuthSession)
        .where(
            or_(
                AuthSession.refresh_token_hash == token_hash,
                AuthSession.previous_refresh_token_hash == token_hash,
            )
        )
        .with_for_update()
    ).one_or_none()

    if auth_session is None:
        raise InvalidRefreshTokenError()

    now = _now()

    if auth_session.previous_refresh_token_hash == token_hash:
        # A rotated token was presented again: it may have been stolen.
        if auth_session.revoked_at is None:
            _revoke(auth_session, now, reason="refresh_token_reuse")
            session.commit()
        raise InvalidRefreshTokenError()

    if auth_session.revoked_at is not None or auth_session.expires_at <= now:
        raise InvalidRefreshTokenError()

    user = session.get(User, auth_session.user_id)
    if user is None or not user.is_active:
        raise InvalidRefreshTokenError()

    auth_session.previous_refresh_token_hash = token_hash
    auth_session.last_refreshed_at = now
    tokens = _issue_tokens(auth_session, now)
    session.commit()
    return tokens


def logout(session: Session, auth_session: AuthSession) -> None:
    _revoke(auth_session, _now(), reason="logout")
    session.commit()


def _revoke(auth_session: AuthSession, now: datetime, *, reason: str) -> None:
    auth_session.revoked_at = now
    auth_session.revocation_reason = reason
