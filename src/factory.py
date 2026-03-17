from __future__ import annotations

from .config import AppSettings
from .ports import DatabaseAdapter
from .sqlalchemy_adapter import SQLAlchemyAdapter
from .sqlite_adapter import SQLiteAdapter


class UnsupportedDialectError(ValueError):
    pass


def create_database_adapter(settings: AppSettings) -> DatabaseAdapter:
    if settings.db.dialect == "sqlite":
        return SQLiteAdapter(
            database_path=str(settings.sqlite_path),
            max_sample_rows=settings.max_sample_rows,
            max_rows_per_query=settings.max_rows_per_query,
            default_query_limit=settings.default_query_limit,
            query_timeout_seconds=settings.query_timeout_seconds,
        )
    if settings.db.dialect in {"postgres", "mysql", "redshift"}:
        return SQLAlchemyAdapter(
            connection_uri=settings.db.build_connection_uri(),
            dialect=settings.db.dialect,
            database_name=settings.db.database,
            schema_name=settings.db.schema_name,
            max_sample_rows=settings.max_sample_rows,
            max_rows_per_query=settings.max_rows_per_query,
            default_query_limit=settings.default_query_limit,
            query_timeout_seconds=settings.query_timeout_seconds,
        )
    raise UnsupportedDialectError(f"Unsupported dialect: {settings.db.dialect}")
