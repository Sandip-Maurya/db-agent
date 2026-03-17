from __future__ import annotations

from .config import AppSettings
from .ports import DatabaseAdapter
from .sqlite_adapter import SQLiteAdapter


class UnsupportedDialectError(ValueError):
    pass


def create_database_adapter(settings: AppSettings) -> DatabaseAdapter:
    match settings.db.dialect:
        case "sqlite":
            return SQLiteAdapter(
                database_path=str(settings.sqlite_path),
                max_sample_rows=settings.max_sample_rows,
                max_rows_per_query=settings.max_rows_per_query,
            )
        case "postgres" | "mysql" | "redshift":
            raise UnsupportedDialectError(
                f"Dialect '{settings.db.dialect}' is planned for a later phase. "
                "The architecture is already adapter-based, so adding a concrete adapter "
                "for this dialect is isolated to the infrastructure layer."
            )
        case other:
            raise UnsupportedDialectError(f"Unsupported dialect: {other}")
