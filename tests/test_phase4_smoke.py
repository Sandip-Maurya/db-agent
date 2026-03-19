from __future__ import annotations

from db_agent.app_runner import AgentApplication
from db_agent.bootstrap import build_app_container
from db_agent.config import AppSettings


def test_phase4_list_tables_smoke():
    app = AgentApplication(build_app_container(AppSettings()))
    overview = app.container.facade.list_tables()
    assert overview.table_count >= 1
    assert overview.table_count == len(overview.tables)
    assert all(bool(table.name) for table in overview.tables)


def test_phase4_test_model_agent_smoke():
    app = AgentApplication(build_app_container(AppSettings()))
    answer = app.ask_with_test_model("List the available tables.", call_tools=["list_tables"])
    assert answer.answer
    assert answer.confidence in {"low", "medium", "high"}
