import os
import warnings
from pathlib import Path

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from src.enums import Environment

SOURCE_DIR = Path(__file__).resolve().parent
SERVER_DIR = SOURCE_DIR.parent
BASE_DIR = SERVER_DIR.parent

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
ENV_FILE = BASE_DIR / f".env.{ENVIRONMENT}"


class ServerSettings(BaseSettings):
    # Environment
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = BASE_DIR.name
    ENVIRONMENT: str = ENVIRONMENT

    @computed_field
    @property
    def ENVIRONMENT_(self) -> Environment:
        return Environment(self.ENVIRONMENT)

    DOMAIN: str
    FRONT_BASE_URL: str

    # Telegram
    TG_BOT_TOKEN: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_AIO_URI(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    SQLALCHEMY_ECHO: bool

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT_ == Environment.LOCAL:
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)

        return self


settings = ServerSettings()  # type: ignore
