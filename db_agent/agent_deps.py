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
    allowed_tables_loaded: bool = False

    def ensure_allowed_tables(self) -> None:
        if self.allowed_tables_loaded:
            return

        try:
            overview = self.facade.list_tables()
            self.allowed_tables = [table.name for table in overview.tables]
        except Exception as exc:  # noqa: BLE001 - keep app running on startup failures
            self.logger.warning(
                "Failed to preload table list; continuing without it: %s", exc
            )
        finally:
            self.allowed_tables_loaded = True

    @classmethod
    def from_facade(
        cls,
        settings: AppSettings,
        facade: DatabaseToolFacade,
        logger: logging.Logger | None = None,
    ) -> "AgentDeps":
        return cls(
            settings=settings,
            facade=facade,
            logger=logger or logging.getLogger(settings.app_name),
        )
