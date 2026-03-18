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
        if isinstance(call_tools, str) and call_tools != "all":
                # Convert a single string into a list to satisfy the list[str] requirement
                call_tools = [call_tools]        
        with self.container.agent.override(model=TestModel(call_tools=call_tools)):
            result = self.container.agent.run_sync(question, deps=self.container.deps)
        return result.output
