from __future__ import annotations

from dataclasses import dataclass, field
import logging

from .config import AppSettings
from .tool_facade import DatabaseToolFacade


@dataclass(slots=True)
class AgentDeps:
    settings: AppSettings
    facade: DatabaseToolFacade
    logger: logging.Logger
    allowed_tables: list[str] = field(default_factory=list)

    @classmethod
    def from_facade(
        cls,
        settings: AppSettings,
        facade: DatabaseToolFacade,
        logger: logging.Logger | None = None,
    ) -> "AgentDeps":
        overview = facade.list_tables()
        return cls(
            settings=settings,
            facade=facade,
            logger=logger or logging.getLogger(settings.app_name),
            allowed_tables=[table.name for table in overview.tables],
        )
