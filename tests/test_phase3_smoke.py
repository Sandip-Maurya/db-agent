from __future__ import annotations

from pydantic_ai.models.test import TestModel

from db_agent.agent_app import build_database_agent
from db_agent.agent_deps import AgentDeps
from db_agent.config import AppSettings
from db_agent.factory import create_database_adapter
from db_agent.services import SchemaExplorerService
from db_agent.tool_facade import DatabaseToolFacade


def build_deps() -> AgentDeps:
    settings = AppSettings()
    adapter = create_database_adapter(settings)
    service = SchemaExplorerService(adapter)
    facade = DatabaseToolFacade(service)
    return AgentDeps.from_facade(settings, facade)


def test_phase3_agent_smoke() -> None:
    deps = build_deps()
    agent = build_database_agent(model=TestModel(call_tools=["list_tables"]))

    result = agent.run_sync(
        "List the available tables.",
        deps=deps,
    )

    assert result.output.answer
    assert result.output.confidence in {"low", "medium", "high"}
