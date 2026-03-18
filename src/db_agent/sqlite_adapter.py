from __future__ import annotations

from pathlib import Path

from .sqlalchemy_adapter import SQLAlchemyAdapter


class SQLiteAdapter(SQLAlchemyAdapter):
    def __init__(
        self,
        database_path: str,
        *,
        max_sample_rows: int = 5,
        max_rows_per_query: int = 200,
        default_query_limit: int = 50,
        query_timeout_seconds: int = 15,
    ) -> None:
        resolved = str(Path(database_path).expanduser().resolve())
        super().__init__(
            f"sqlite:///{resolved}",
            dialect="sqlite",
            database_name=Path(resolved).name,
            max_sample_rows=max_sample_rows,
            max_rows_per_query=max_rows_per_query,
            default_query_limit=default_query_limit,
            query_timeout_seconds=query_timeout_seconds,
        )
