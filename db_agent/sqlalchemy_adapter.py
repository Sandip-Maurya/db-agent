from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Any

from sqlalchemy import MetaData, Table, create_engine, func, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import SQLAlchemyError

from .domain import ColumnProfile, QueryResult, SchemaSnapshot, TableProfile, TableSummary
from .ports import DatabaseAdapter
from .safety import QuerySafetyPolicy


class SQLAlchemyAdapter(DatabaseAdapter):
    def __init__(
        self,
        connection_uri: str,
        *,
        dialect: str,
        database_name: str,
        schema_name: str | None = None,
        max_sample_rows: int = 5,
        max_rows_per_query: int = 200,
        default_query_limit: int = 50,
        query_timeout_seconds: int = 15,
        engine_kwargs: dict | None = None,
    ) -> None:
        self.connection_uri = connection_uri
        self.dialect = dialect
        self.database_name = database_name
        self.schema_name = schema_name
        self.max_sample_rows = max_sample_rows
        self.query_timeout_seconds = query_timeout_seconds
        self.safety_policy = QuerySafetyPolicy(
            max_rows=max_rows_per_query,
            default_limit=default_query_limit,
        )

        kwargs = {"future": True}
        if engine_kwargs:
            kwargs.update(engine_kwargs)

        self._engine: Engine = create_engine(connection_uri, **kwargs)
        
    def list_tables(self) -> list[str]:
        inspector = inspect(self._engine)
        return sorted(inspector.get_table_names(schema=self.schema_name))

    def list_table_summaries_light(self) -> list[TableSummary]:
        inspector = inspect(self._engine)
        names = sorted(inspector.get_table_names(schema=self.schema_name))
        if not names:
            return []
        batch = self._list_table_summaries_from_multi_columns(inspector, names)
        if batch is not None:
            return batch
        return self._list_table_summaries_light_per_table(inspector, names)

    def _list_table_summaries_from_multi_columns(
        self, inspector: Inspector, names: list[str]
    ) -> list[TableSummary] | None:
        try:
            multi = inspector.get_multi_columns(
                schema=self.schema_name, filter_names=names
            )
        except Exception:
            return None
        summaries: list[TableSummary] = []
        for name in names:
            columns = self._lookup_multi_columns(multi, self.schema_name, name)
            if columns is None:
                return None
            col_names = [column["name"] for column in columns]
            summaries.append(
                TableSummary(
                    name=name,
                    description=self._infer_description(name, col_names),
                    row_count_estimate=None,
                    column_names=col_names,
                )
            )
        return summaries

    @staticmethod
    def _lookup_multi_columns(
        multi: dict[Any, Any], schema: str | None, table_name: str
    ) -> list[dict[str, Any]] | None:
        for key in ((schema, table_name), (None, table_name)):
            if key in multi:
                return multi[key]
        for key, cols in multi.items():
            if not isinstance(key, tuple) or len(key) != 2:
                continue
            sch, tbl = key
            tbl_str = tbl if isinstance(tbl, str) else str(tbl)
            if tbl_str != table_name:
                continue
            if schema is None or sch is None or sch == schema:
                return cols
        return None

    def _list_table_summaries_light_per_table(
        self, inspector: Inspector, names: list[str]
    ) -> list[TableSummary]:
        summaries: list[TableSummary] = []
        for name in names:
            columns = inspector.get_columns(name, schema=self.schema_name)
            col_names = [column["name"] for column in columns]
            summaries.append(
                TableSummary(
                    name=name,
                    description=self._infer_description(name, col_names),
                    row_count_estimate=None,
                    column_names=col_names,
                )
            )
        return summaries

    def get_table_profile(self, table_name: str) -> TableProfile:
        inspector = inspect(self._engine)
        tables = inspector.get_table_names(schema=self.schema_name)
        if table_name not in tables:
            raise ValueError(f"Unknown table: {table_name}. Available tables: {tables}")

        pk = set(inspector.get_pk_constraint(table_name, schema=self.schema_name).get("constrained_columns") or [])
        columns = [
            ColumnProfile(
                name=column["name"],
                data_type=str(column.get("type", "unknown")),
                nullable=bool(column.get("nullable", True)),
                default=None if column.get("default") is None else str(column.get("default")),
                is_primary_key=column["name"] in pk,
            )
            for column in inspector.get_columns(table_name, schema=self.schema_name)
        ]
        fks = []
        for fk in inspector.get_foreign_keys(table_name, schema=self.schema_name):
            for constrained, referred in zip(fk.get("constrained_columns", []), fk.get("referred_columns", []), strict=False):
                referred_table = fk.get("referred_table") or "unknown"
                fks.append(f"{constrained} -> {referred_table}.{referred}")

        with self._engine.begin() as conn:
            metadata = MetaData(schema=self.schema_name)
            table = Table(table_name, metadata, autoload_with=conn)
            row_count = conn.execute(select(func.count()).select_from(table)).scalar_one()
            sample_rows = conn.execute(select(table).limit(self.max_sample_rows)).mappings().all()

        return TableProfile(
            name=table_name,
            schema_name=self.schema_name,
            kind="table",
            row_count_estimate=int(row_count),
            description=self._infer_description(table_name, [c.name for c in columns]),
            columns=columns,
            foreign_keys=fks,
            sample_rows=[dict(row) for row in sample_rows],
        )

    def get_schema_snapshot(self) -> SchemaSnapshot:
        return SchemaSnapshot(
            dialect=self.dialect,
            database_name=self.database_name,
            tables=[self.get_table_profile(name) for name in self.list_tables()],
        )

    def sample_rows(self, table_name: str, limit: int) -> list[dict[str, Any]]:
        requested_limit = min(max(1, limit), self.max_sample_rows)
        inspector = inspect(self._engine)
        tables = inspector.get_table_names(schema=self.schema_name)
        if table_name not in tables:
            raise ValueError(f"Unknown table: {table_name}. Available tables: {tables}")
        with self._engine.begin() as conn:
            metadata = MetaData(schema=self.schema_name)
            table = Table(table_name, metadata, autoload_with=conn)
            rows = conn.execute(select(table).limit(requested_limit)).mappings().all()
        return [dict(row) for row in rows]

    def execute_query(self, sql: str) -> QueryResult:
        safe_sql = self.safety_policy.validate_sql(sql)
        start = perf_counter()
        try:
            with self._engine.begin() as conn:
                rows = conn.execute(text(safe_sql)).mappings().all()
        except SQLAlchemyError as exc:
            raise ValueError(f"Query execution failed: {exc}") from exc
        duration_ms = round((perf_counter() - start) * 1000, 2)
        dict_rows = [dict(row) for row in rows]
        columns = list(dict_rows[0].keys()) if dict_rows else []
        truncated = len(dict_rows) >= self.safety_policy.max_rows
        return QueryResult(
            sql=safe_sql,
            columns=columns,
            rows=dict_rows,
            row_count=len(dict_rows),
            truncated=truncated,
            execution_metadata={
                "dialect": self.dialect,
                "database": self.database_name,
                "duration_ms": duration_ms,
                "timeout_seconds": self.query_timeout_seconds,
            },
        )

    def close(self) -> None:
        self._engine.dispose()

    @staticmethod
    def _infer_description(table_name: str, column_names: list[str]) -> str:
        lower_name = table_name.lower()
        columns = {name.lower() for name in column_names}
        if lower_name.endswith("s"):
            grain = f"Likely one row per {lower_name[:-1].replace('_', ' ')}"
        else:
            grain = f"Likely one row per {lower_name.replace('_', ' ')}"
        hints: list[str] = []
        if "created_at" in columns:
            hints.append("contains creation timestamps")
        if "status" in columns:
            hints.append("tracks status values")
        if any(name.endswith("_id") for name in columns):
            hints.append("includes identifier or relationship columns")
        return "; ".join([grain, *hints]) if hints else grain
