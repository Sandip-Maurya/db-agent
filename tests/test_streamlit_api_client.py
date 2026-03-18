from __future__ import annotations

from requests import Response
from requests.structures import CaseInsensitiveDict

from streamlit_app.api_client import DbAgentApiClient


class DummySession:
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def request(self, method: str, url: str, timeout: float, **kwargs):  # noqa: ANN001
        response = Response()
        response.status_code = self.status_code
        response.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
        import json

        response._content = json.dumps(self.payload).encode("utf-8")
        return response



def test_get_health_parses_response() -> None:
    client = DbAgentApiClient(
        base_url="http://localhost:8000",
        timeout_seconds=10,
        session=DummySession(
            {
                "status": "ok",
                "app_name": "db-agent",
                "environment": "dev",
                "dialect": "sqlite",
                "database_name": "demo.db",
                "default_query_limit": 50,
                "max_rows_per_query": 200,
                "max_sample_rows": 5,
            }
        ),
    )

    payload = client.get_health()
    assert payload.database_name == "demo.db"
    assert payload.dialect == "sqlite"



def test_ask_parses_structured_answer() -> None:
    client = DbAgentApiClient(
        base_url="http://localhost:8000",
        timeout_seconds=10,
        session=DummySession(
            {
                "answer": {
                    "answer": "Orders use INR and USD.",
                    "assumptions": [],
                    "evidence": [{"kind": "query", "detail": "Checked sample rows."}],
                    "db_query_executed": "select distinct currency from orders limit 50",
                    "confidence": "high",
                    "needs_followup": False,
                }
            }
        ),
    )

    response = client.ask("What currencies appear in orders?")
    assert response.answer.confidence == "high"
    assert response.answer.db_query_executed is not None
