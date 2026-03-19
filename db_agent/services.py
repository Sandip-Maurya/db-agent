from __future__ import annotations

from .domain import QueryResult, SchemaSnapshot, TableProfile, TableSummary
from .ports import DatabaseAdapter


class SchemaExplorerService:
    """Application service layer used by tool facades and the agent."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self.adapter = adapter

    def overview(self) -> SchemaSnapshot:
        return self.adapter.get_schema_snapshot()

    def list_table_summaries(self) -> list[TableSummary]:
        return self.adapter.list_table_summaries_light()

    def describe_table(self, table_name: str) -> TableProfile:
        return self.adapter.get_table_profile(table_name)

    def sample_rows(self, table_name: str, *, limit: int) -> list[dict[str, object]]:
        return self.adapter.sample_rows(table_name, limit)

    def query(self, sql: str) -> QueryResult:
        return self.adapter.execute_query(sql)
