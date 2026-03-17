from __future__ import annotations

from .services import SchemaExplorerService
from .tool_models import (
    DescribeTableOutput,
    ListTablesOutput,
    RunQueryOutput,
    SampleRowsOutput,
    TableToolSummary,
)


class DatabaseToolFacade:
    """Stable, agent-friendly facade over the application services."""

    def __init__(self, service: SchemaExplorerService) -> None:
        self.service = service

    def list_tables(self) -> ListTablesOutput:
        snapshot = self.service.overview()
        summaries = [
            TableToolSummary(
                name=table.name,
                description=table.description,
                row_count_estimate=table.row_count_estimate,
                column_names=[column.name for column in table.columns],
            )
            for table in snapshot.tables
        ]
        return ListTablesOutput(
            dialect=snapshot.dialect,
            database_name=snapshot.database_name,
            table_count=len(summaries),
            tables=summaries,
        )

    def describe_table(self, table_name: str) -> DescribeTableOutput:
        profile = self.service.describe_table(table_name)
        return DescribeTableOutput(profile=profile)

    def sample_rows(self, table_name: str, *, limit: int = 5) -> SampleRowsOutput:
        rows = self.service.sample_rows(table_name, limit=limit)
        return SampleRowsOutput(
            table_name=table_name,
            rows=rows,
            row_count=len(rows),
            requested_limit=limit,
        )

    def run_query(self, sql: str) -> RunQueryOutput:
        result = self.service.query(sql)
        return RunQueryOutput(result=result)
