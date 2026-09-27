import unicodedata

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_password_hasher = PasswordHasher()


def _normalize(password: str) -> str:
    return unicodedata.normalize("NFC", password)


def hash_password(password: str) -> str:
    return _password_hasher.hash(_normalize(password))


def verify_password(*, password: str, password_hash: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, _normalize(password))
    except VerificationError, InvalidHashError:
        return False


def password_needs_rehash(password_hash: str) -> bool:
    return _password_hasher.check_needs_rehash(password_hash)
