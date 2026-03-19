from __future__ import annotations

from .sqlalchemy_adapter import SQLAlchemyAdapter


class PostgresAdapter(SQLAlchemyAdapter):
    def __init__(
        self,
        connection_uri: str,
        *,
        database_name: str,
        schema_name: str | None = None,
        max_sample_rows: int = 5,
        max_rows_per_query: int = 200,
        default_query_limit: int = 50,
        query_timeout_seconds: int = 15,
    ) -> None:
        connect_args: dict[str, str] = {}
        options: list[str] = []

        if schema_name:
            options.append(f"-c search_path={schema_name}")

        if query_timeout_seconds:
            timeout_ms = int(query_timeout_seconds * 1000)
            options.append(f"-c statement_timeout={timeout_ms}")

        if options:
            connect_args["options"] = " ".join(options)

        super().__init__(
            connection_uri=connection_uri,
            dialect="postgres",
            database_name=database_name,
            schema_name=schema_name,
            max_sample_rows=max_sample_rows,
            max_rows_per_query=max_rows_per_query,
            default_query_limit=default_query_limit,
            query_timeout_seconds=query_timeout_seconds,
            engine_kwargs={
                # SQLAlchemy defaults (5/10) + pre_ping for long-lived API workers
                "pool_pre_ping": True,
                "pool_size": 5,
                "max_overflow": 10,
                "connect_args": connect_args,
            },
        )