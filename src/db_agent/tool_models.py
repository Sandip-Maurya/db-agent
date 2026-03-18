from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .domain import QueryResult, TableProfile


class TableToolSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    row_count_estimate: int | None = None
    column_names: list[str] = Field(default_factory=list)


class ListTablesOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dialect: str
    database_name: str
    table_count: int
    tables: list[TableToolSummary] = Field(default_factory=list)


class DescribeTableOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: TableProfile


class SampleRowsOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_name: str
    rows: list[dict[str, object]] = Field(default_factory=list)
    row_count: int
    requested_limit: int


class RunQueryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    result: QueryResult
