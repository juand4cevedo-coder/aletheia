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


@lru_cache
def get_settings() -> Settings:
    return Settings()
