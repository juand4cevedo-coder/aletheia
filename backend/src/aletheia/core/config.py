from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ALETHEIA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: SecretStr
    db_name: str

    storage_endpoint_url: str
    storage_access_key: str
    storage_secret_key: SecretStr
    storage_bucket: str
    storage_region: str = "us-east-1"

    evidence_max_bytes: int = 100 * 1024 * 1024

    access_token_ttl_minutes: int = 15
    session_ttl_days: int = 14


@lru_cache
def get_settings() -> Settings:
    # Values come from the environment and .env; Pyright cannot see that.
    return Settings()  # pyright: ignore[reportCallIssue]
