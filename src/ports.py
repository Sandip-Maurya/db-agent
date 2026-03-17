from __future__ import annotations

from abc import ABC, abstractmethod

from .domain import QueryResult, SchemaSnapshot, TableProfile


class DatabaseAdapter(ABC):
    @abstractmethod
    def list_tables(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_table_profile(self, table_name: str) -> TableProfile:
        raise NotImplementedError

    @abstractmethod
    def get_schema_snapshot(self) -> SchemaSnapshot:
        raise NotImplementedError

    @abstractmethod
    def execute_query(self, sql: str) -> QueryResult:
        raise NotImplementedError
