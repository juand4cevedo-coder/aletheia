from aletheia.core.security import hash_password, password_needs_rehash, verify_password


def test_hash_password_uses_argon2id_and_never_stores_plaintext() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash.startswith("$argon2id$")
    assert "correct horse battery staple" not in password_hash


def test_hash_password_uses_a_random_salt() -> None:
    assert hash_password("same password") != hash_password("same password")


def test_verify_password_accepts_the_correct_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert verify_password(password="correct horse battery staple", password_hash=password_hash)


def test_verify_password_rejects_a_wrong_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert not verify_password(password="wrong password", password_hash=password_hash)


def test_verify_password_rejects_a_malformed_hash() -> None:
    assert not verify_password(password="anything", password_hash="not-a-valid-hash")


def test_fresh_hash_does_not_need_rehash() -> None:
    assert not password_needs_rehash(hash_password("correct horse battery staple"))
