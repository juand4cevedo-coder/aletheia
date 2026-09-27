import hashlib
import uuid
from collections.abc import Iterator

import pytest

from aletheia.core.storage import (
    ObjectAlreadyExistsError,
    ObjectIntegrityError,
    ObjectStorage,
    get_storage,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def storage() -> ObjectStorage:
    return get_storage()


@pytest.fixture
def key(storage: ObjectStorage) -> Iterator[str]:
    """A unique key under a test prefix, removed after the test."""
    object_key = f"tests/{uuid.uuid4()}"
    yield object_key
    # The application never deletes originals; only tests clean up after themselves.
    storage._client.delete_object(Bucket=storage._bucket, Key=object_key)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_new_object_is_stored_and_read_back_unchanged(storage: ObjectStorage, key: str) -> None:
    data = b"contenido de prueba" * 100

    storage.put_new_object(key, data, sha256_hex=sha256_hex(data), content_type="text/plain")

    assert storage.read_object(key) == data


def test_existing_object_is_never_overwritten(storage: ObjectStorage, key: str) -> None:
    original = b"original"
    storage.put_new_object(
        key, original, sha256_hex=sha256_hex(original), content_type="text/plain"
    )

    with pytest.raises(ObjectAlreadyExistsError):
        storage.put_new_object(
            key, b"tampered", sha256_hex=sha256_hex(b"tampered"), content_type="text/plain"
        )

    assert storage.read_object(key) == original


def test_upload_with_mismatching_checksum_is_rejected(storage: ObjectStorage, key: str) -> None:
    with pytest.raises(ObjectIntegrityError):
        storage.put_new_object(
            key, b"actual bytes", sha256_hex=sha256_hex(b"other bytes"), content_type="text/plain"
        )


def test_storage_is_ready(storage: ObjectStorage) -> None:
    storage.check_ready()
