from __future__ import annotations

from pprint import pprint

from pydantic_ai.models.test import TestModel
from dotenv import load_dotenv

load_dotenv()

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


def main() -> None:
    deps = build_deps()
    agent = build_database_agent(model="openai:gpt-4o-mini")

    prompt = (
        "What is the orders table about, and what currencies appear in it? "
        "Use the tools to inspect the schema and data before answering."
    )
    result = agent.run_sync(prompt, deps=deps)

    print("=== PHASE 3 AGENT OUTPUT ===")
    pprint(result.output.model_dump())

    print("\n=== PHASE 3 MESSAGE COUNT ===")
    print(len(result.new_messages()))


if __name__ == "__main__":
    main()
