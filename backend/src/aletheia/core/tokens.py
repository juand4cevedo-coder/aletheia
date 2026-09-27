import hashlib
import secrets

TOKEN_BYTES = 32


def generate_token() -> str:
    """Return a new URL-safe random token with 256 bits of entropy."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest used to store and look up a token."""
    return hashlib.sha256(token.encode()).hexdigest()
