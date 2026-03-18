from __future__ import annotations

from fastapi.testclient import TestClient

from db_agent.agent_models import AgentAnswer
from db_agent.api import app, get_application, get_settings
from db_agent.config import AppSettings
from db_agent.domain import ColumnProfile, TableProfile
from db_agent.tool_models import DescribeTableOutput, ListTablesOutput, TableToolSummary


class DummyFacade:
    def list_tables(self) -> ListTablesOutput:
        return ListTablesOutput(
            dialect="sqlite",
            database_name="demo.db",
            table_count=1,
            tables=[
                TableToolSummary(
                    name="orders",
                    description="Orders table",
                    row_count_estimate=4,
                    column_names=["order_id", "currency"],
                )
            ],
        )

    def describe_table(self, table_name: str) -> DescribeTableOutput:
        if table_name != "orders":
            raise ValueError("Unknown table")
        return DescribeTableOutput(
            profile=TableProfile(
                name="orders",
                description="Orders table",
                columns=[ColumnProfile(name="order_id", data_type="INTEGER")],
                sample_rows=[{"order_id": 1}],
            )
        )


class DummyContainer:
    def __init__(self) -> None:
        self.facade = DummyFacade()


class DummyApplication:
    def __init__(self) -> None:
        self.container = DummyContainer()

    def ask(self, question: str) -> AgentAnswer:
        return AgentAnswer(answer=f"Answer for: {question}", confidence="high")

    def ask_with_test_model(self, question: str) -> AgentAnswer:
        return AgentAnswer(answer=f"Test answer for: {question}", confidence="medium")


app.dependency_overrides[get_application] = lambda: DummyApplication()
app.dependency_overrides[get_settings] = lambda: AppSettings()
client = TestClient(app)


def test_health_returns_backend_summary() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["dialect"] == "sqlite"



def test_table_detail_endpoint() -> None:
    response = client.get("/tables/orders")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "orders"
    assert payload["sample_rows"] == [{"order_id": 1}]



def test_query_endpoint_returns_structured_answer() -> None:
    response = client.post("/query", json={"question": "What is in orders?", "use_test_model": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"]["answer"].startswith("Test answer")
    assert payload["answer"]["confidence"] == "medium"
