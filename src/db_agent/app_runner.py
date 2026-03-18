from __future__ import annotations

from pydantic_ai.models.test import TestModel

from .agent_models import AgentAnswer
from .bootstrap import AppContainer, build_app_container


class AgentApplication:
    def __init__(self, container: AppContainer | None = None) -> None:
        self.container = container or build_app_container()

    def ask(self, question: str) -> AgentAnswer:
        result = self.container.agent.run_sync(question, deps=self.container.deps)
        return result.output

    def ask_with_test_model(self, question: str, *, call_tools: list[str] | str = "all") -> AgentAnswer:
        with self.container.agent.override(model=TestModel(call_tools=call_tools)):
            result = self.container.agent.run_sync(question, deps=self.container.deps)
        return result.output
