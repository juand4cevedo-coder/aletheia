from aletheia.core.tokens import generate_token, hash_token


def test_generated_tokens_are_long_and_unique() -> None:
    tokens = {generate_token() for _ in range(100)}

    assert len(tokens) == 100
    assert all(len(token) >= 43 for token in tokens)


def test_hash_token_is_deterministic_and_does_not_contain_the_token() -> None:
    token = generate_token()

    assert hash_token(token) == hash_token(token)
    assert len(hash_token(token)) == 64
    assert token not in hash_token(token)
