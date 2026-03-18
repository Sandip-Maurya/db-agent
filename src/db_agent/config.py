from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

SupportedDialect = Literal["sqlite", "postgres", "mysql", "redshift"]
SupportedEnvironment = Literal["dev", "test", "prod"]


class DatabaseSettings(BaseModel):
    dialect: SupportedDialect = "sqlite"
    database: str = Field(default="./demo.db", description="Path or database name")
    uri: str | None = Field(default=None, description="Optional full SQLAlchemy connection URL")
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: SecretStr | None = None
    schema_name: str | None = None

    @property
    def is_sqlite(self) -> bool:
        return self.dialect == "sqlite"

    @property
    def sqlalchemy_scheme(self) -> str:
        return {
            "sqlite": "sqlite",
            "postgres": "postgresql+psycopg",
            "mysql": "mysql+pymysql",
            "redshift": "redshift+psycopg2",
        }[self.dialect]

    def build_connection_uri(self) -> str:
        if self.uri:
            return self.uri
        if self.is_sqlite:
            return f"sqlite:///{Path(self.database).expanduser().resolve()}"
        if not all([self.host, self.port, self.username]):
            raise ValueError(
                f"Database settings for dialect={self.dialect!r} require either db.uri or host/port/username/database"
            )
        password = self.password.get_secret_value() if self.password else ""
        password_part = f":{password}" if password else ""
        return f"{self.sqlalchemy_scheme}://{self.username}{password_part}@{self.host}:{self.port}/{self.database}"


class ModelSettings(BaseModel):
    provider_model: str = Field(
        default="test",
        description="Pydantic AI model identifier, e.g. 'openai:gpt-5-mini' or 'anthropic:claude-sonnet-4-5'.",
    )


class ApiSettings(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_AGENT_",
        env_nested_delimiter="__",
        extra="ignore",
        env_file=".env"
    )

    app_name: str = "db-agent-app"
    environment: SupportedEnvironment = "dev"
    db: DatabaseSettings = DatabaseSettings()
    model: ModelSettings = ModelSettings()
    api: ApiSettings = ApiSettings()
    max_rows_per_query: int = 200
    max_sample_rows: int = 5
    query_timeout_seconds: int = 15
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    default_query_limit: int = 50

    @cached_property
    def sqlite_path(self) -> Path:
        return Path(self.db.database).expanduser().resolve()
