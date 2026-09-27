import base64
from functools import lru_cache
from typing import TYPE_CHECKING, BinaryIO

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from aletheia.core.config import get_settings

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


class StorageError(Exception):
    """The object storage could not complete an operation."""


class ObjectAlreadyExistsError(StorageError):
    """An object with the same key already exists and was not overwritten."""


class ObjectIntegrityError(StorageError):
    """The storage rejected an upload because its content did not match the declared SHA-256."""


class ObjectStorage:
    """Minimal, write-once access to an S3-compatible bucket."""

    def __init__(self, client: S3Client, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def put_new_object(
        self, key: str, data: bytes | BinaryIO, *, sha256_hex: str, content_type: str
    ) -> None:
        """Store `data` under `key` only if no object exists there yet.

        The storage verifies the SHA-256 on arrival and rejects the upload if it
        does not match, so corrupted transfers are never stored.
        """
        checksum = base64.b64encode(bytes.fromhex(sha256_hex)).decode()
        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                ChecksumSHA256=checksum,
                IfNoneMatch="*",
            )
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code")
            if code == "PreconditionFailed":
                raise ObjectAlreadyExistsError(key) from error
            if code in {"BadDigest", "InvalidDigest"}:
                raise ObjectIntegrityError(key) from error
            raise StorageError(key) from error
        except BotoCoreError as error:
            raise StorageError(key) from error

    def read_object(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except (ClientError, BotoCoreError) as error:
            raise StorageError(key) from error

    def check_ready(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except (ClientError, BotoCoreError) as error:
            raise StorageError(self._bucket) from error


@lru_cache
def get_storage() -> ObjectStorage:
    settings = get_settings()
    client = boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint_url,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key.get_secret_value(),
        region_name=settings.storage_region,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            connect_timeout=5,
            read_timeout=30,
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )
    return ObjectStorage(client, settings.storage_bucket)
