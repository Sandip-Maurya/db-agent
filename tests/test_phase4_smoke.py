from __future__ import annotations

from db_agent_app.app_runner import AgentApplication
from db_agent_app.bootstrap import build_app_container
from db_agent_app.config import AppSettings


def test_phase4_list_tables_smoke():
    app = AgentApplication(build_app_container(AppSettings()))
    overview = app.container.facade.list_tables()
    assert overview.table_count >= 1
    assert any(table.name == "orders" for table in overview.tables)


def test_phase4_test_model_agent_smoke():
    app = AgentApplication(build_app_container(AppSettings()))
    answer = app.ask_with_test_model("What data is in the orders table?")
    assert answer.answer
    assert answer.confidence in {"low", "medium", "high"}
