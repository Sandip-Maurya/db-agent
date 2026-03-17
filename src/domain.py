from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ColumnProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    data_type: str
    nullable: bool = True
    default: str | None = None
    is_primary_key: bool = False
    notes: str | None = None


class TableProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    schema_name: str | None = None
    kind: str = "table"
    row_count_estimate: int | None = None
    description: str | None = None
    columns: list[ColumnProfile] = Field(default_factory=list)
    foreign_keys: list[str] = Field(default_factory=list)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)


class TableSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    row_count_estimate: int | None = None
    column_names: list[str] = Field(default_factory=list)


class SchemaSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dialect: str
    database_name: str
    tables: list[TableProfile] = Field(default_factory=list)


class QueryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool = False
    execution_metadata: dict[str, Any] = Field(default_factory=dict)
