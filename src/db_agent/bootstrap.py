from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from .agent_app import build_database_agent
from .agent_deps import AgentDeps
from .config import AppSettings
from .factory import create_database_adapter
from .services import SchemaExplorerService
from .tool_facade import DatabaseToolFacade


@dataclass(slots=True)
class AppContainer:
    settings: AppSettings
    agent: Any
    deps: AgentDeps
    facade: DatabaseToolFacade
    service: SchemaExplorerService


def configure_logging(settings: AppSettings) -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger(settings.app_name)


def build_app_container(settings: AppSettings | None = None) -> AppContainer:
    settings = settings or AppSettings()
    logger = configure_logging(settings)
    adapter = create_database_adapter(settings)
    service = SchemaExplorerService(adapter)
    facade = DatabaseToolFacade(service)
    deps = AgentDeps.from_facade(settings=settings, facade=facade, logger=logger)
    agent = build_database_agent(model=settings.model.provider_model)
    return AppContainer(settings=settings, agent=agent, deps=deps, facade=facade, service=service)
