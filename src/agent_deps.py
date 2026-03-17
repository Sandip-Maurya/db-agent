from __future__ import annotations

from dataclasses import dataclass, field

from .config import AppSettings
from .tool_facade import DatabaseToolFacade


@dataclass(slots=True)
class AgentDeps:
    settings: AppSettings
    facade: DatabaseToolFacade
    allowed_tables: list[str] = field(default_factory=list)

    @classmethod
    def from_facade(cls, settings: AppSettings, facade: DatabaseToolFacade) -> "AgentDeps":
        overview = facade.list_tables()
        return cls(
            settings=settings,
            facade=facade,
            allowed_tables=[table.name for table in overview.tables],
        )
