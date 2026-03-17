from __future__ import annotations

from .domain import QueryResult, SchemaSnapshot, TableProfile
from .ports import DatabaseAdapter


class SchemaExplorerService:
    """Application service layer used by tools and later by the agent."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self.adapter = adapter

    def overview(self) -> SchemaSnapshot:
        return self.adapter.get_schema_snapshot()

    def describe_table(self, table_name: str) -> TableProfile:
        return self.adapter.get_table_profile(table_name)

    def query(self, sql: str) -> QueryResult:
        return self.adapter.execute_query(sql)
