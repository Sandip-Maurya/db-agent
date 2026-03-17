from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


SupportedDialect = Literal["sqlite", "postgres", "mysql", "redshift"]


class DatabaseSettings(BaseModel):
    dialect: SupportedDialect = "sqlite"
    database: str = Field(default="./demo.db", description="Path or database name")
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None
    schema_name: str | None = None

    @property
    def is_sqlite(self) -> bool:
        return self.dialect == "sqlite"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB_AGENT_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    app_name: str = "db-agent-app"
    environment: Literal["dev", "test", "prod"] = "dev"
    db: DatabaseSettings = DatabaseSettings()
    max_rows_per_query: int = 200
    max_sample_rows: int = 5
    query_timeout_seconds: int = 15

    @cached_property
    def sqlite_path(self) -> Path:
        return Path(self.db.database).expanduser().resolve()
