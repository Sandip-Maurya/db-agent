from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .domain import ColumnProfile, QueryResult, SchemaSnapshot, TableProfile
from .ports import DatabaseAdapter
from .safety import QuerySafetyPolicy


class SQLiteAdapter(DatabaseAdapter):
    def __init__(
        self,
        database_path: str,
        *,
        max_sample_rows: int = 5,
        max_rows_per_query: int = 200,
    ) -> None:
        self.database_path = str(Path(database_path).expanduser().resolve())
        self.max_sample_rows = max_sample_rows
        self.safety_policy = QuerySafetyPolicy(max_rows=max_rows_per_query)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self) -> list[str]:
        sql = """
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        return [str(row[0]) for row in rows]

    def get_table_profile(self, table_name: str) -> TableProfile:
        with self._connect() as conn:
            pragma_rows = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            if not pragma_rows:
                raise ValueError(f"Unknown table: {table_name}")

            columns = [
                ColumnProfile(
                    name=str(row[1]),
                    data_type=str(row[2] or "unknown"),
                    nullable=not bool(row[3]),
                    default=None if row[4] is None else str(row[4]),
                    is_primary_key=bool(row[5]),
                )
                for row in pragma_rows
            ]

            row_count = conn.execute(f'SELECT COUNT(*) AS count FROM "{table_name}"').fetchone()[0]
            sample_rows = self._sample_rows(conn, table_name, limit=self.max_sample_rows)
            foreign_keys = self._foreign_keys(conn, table_name)

        return TableProfile(
            name=table_name,
            kind="table",
            row_count_estimate=int(row_count),
            description=self._infer_description(table_name, columns),
            columns=columns,
            foreign_keys=foreign_keys,
            sample_rows=sample_rows,
        )

    def get_schema_snapshot(self) -> SchemaSnapshot:
        tables = [self.get_table_profile(table_name) for table_name in self.list_tables()]
        return SchemaSnapshot(
            dialect="sqlite",
            database_name=Path(self.database_path).name,
            tables=tables,
        )

    def sample_rows(self, table_name: str, limit: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            profile = conn.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            if not profile:
                raise ValueError(f"Unknown table: {table_name}")
            return self._sample_rows(conn, table_name, limit=min(limit, self.max_sample_rows))

    def execute_query(self, sql: str) -> QueryResult:
        self.safety_policy.validate_sql(sql)
        with self._connect() as conn:
            rows = conn.execute(sql).fetchall()
        dict_rows = [dict(row) for row in rows]
        columns = list(dict_rows[0].keys()) if dict_rows else []
        truncated = len(dict_rows) >= self.safety_policy.max_rows
        return QueryResult(
            sql=sql,
            columns=columns,
            rows=dict_rows,
            row_count=len(dict_rows),
            truncated=truncated,
        )

    def _sample_rows(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        *,
        limit: int,
    ) -> list[dict[str, Any]]:
        sql = f'SELECT * FROM "{table_name}" LIMIT {int(limit)}'
        rows = conn.execute(sql).fetchall()
        return [dict(row) for row in rows]

    def _foreign_keys(self, conn: sqlite3.Connection, table_name: str) -> list[str]:
        rows = conn.execute(f"PRAGMA foreign_key_list('{table_name}')").fetchall()
        return [
            f"{row[3]} -> {row[2]}.{row[4]}"
            for row in rows
        ]

    @staticmethod
    def _infer_description(table_name: str, columns: Iterable[ColumnProfile]) -> str:
        lower_name = table_name.lower()
        column_names = {column.name.lower() for column in columns}
        if lower_name.endswith("s"):
            grain = f"Likely one row per {lower_name[:-1].replace('_', ' ')}"
        else:
            grain = f"Likely one row per {lower_name.replace('_', ' ')}"

        hints: list[str] = []
        if "created_at" in column_names:
            hints.append("contains creation timestamps")
        if "status" in column_names:
            hints.append("tracks status values")
        if any(name.endswith("_id") for name in column_names):
            hints.append("includes identifier or relationship columns")

        return "; ".join([grain, *hints]) if hints else grain
