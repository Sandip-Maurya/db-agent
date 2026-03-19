from __future__ import annotations

from requests import Response, Session
from requests.structures import CaseInsensitiveDict

from streamlit_app.api_client import DbAgentApiClient


class DummySession(Session):
    def __init__(self, payload: dict, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def request(self, method: str, url: str = "", params=None, data=None, headers=None, cookies=None, files=None, auth=None, timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None, **kwargs): # type: ignore
        response = Response()
        response.status_code = self.status_code
        response.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
        import json as json_module

        response._content = json_module.dumps(self.payload).encode("utf-8")
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
                    "db_query_executed": True,
                    "executed_sql": "select distinct currency from orders limit 50",
                    "confidence": "high",
                    "needs_followup": False,
                }
            }
        ),
    )

    response = client.ask("What currencies appear in orders?")
    assert response.answer.confidence == "high"
    assert response.answer.db_query_executed is True
    assert response.answer.executed_sql == "select distinct currency from orders limit 50"
