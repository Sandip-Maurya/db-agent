from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from pydantic import BaseModel, ConfigDict, Field

from db_agent.agent_models import AgentAnswer, EvidenceItem

class ApiClientError(RuntimeError):
    """Base error for Streamlit API client failures."""


class BackendUnavailableError(ApiClientError):
    """Raised when the FastAPI backend cannot be reached."""


class BackendRequestError(ApiClientError):
    """Raised when the backend returns an error response."""


class HealthPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    app_name: str
    environment: str
    dialect: str
    database_name: str
    default_query_limit: int
    max_rows_per_query: int
    max_sample_rows: int


class TableSummaryPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    row_count_estimate: int | None = None
    column_names: list[str] = Field(default_factory=list)


class TablesPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dialect: str
    database_name: str
    table_count: int
    tables: list[TableSummaryPayload] = Field(default_factory=list)


class ColumnProfilePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    data_type: str
    nullable: bool = True
    default: str | None = None
    is_primary_key: bool = False
    notes: str | None = None


class TableProfilePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    schema_name: str | None = None
    kind: str = "table"
    row_count_estimate: int | None = None
    description: str | None = None
    columns: list[ColumnProfilePayload] = Field(default_factory=list)
    foreign_keys: list[str] = Field(default_factory=list)
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)


class EvidenceItemPayload(EvidenceItem):
    """Using EvidenceItem as EvidenceItemPayload"""
    


class AgentAnswerPayload(AgentAnswer):
    """Use AgentAnswer Model for AgentAnswerPayload """


class QueryResponsePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: AgentAnswerPayload


@dataclass(slots=True)
class DbAgentApiClient:
    base_url: str
    timeout_seconds: float = 30.0
    session: requests.Session | None = None

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        if self.session is None:
            self.session = requests.Session()

    def get_health(self) -> HealthPayload:
        payload = self._request("GET", "/health")
        return HealthPayload.model_validate(payload)

    def get_tables(self) -> TablesPayload:
        payload = self._request("GET", "/tables")
        return TablesPayload.model_validate(payload)

    def get_table(self, table_name: str) -> TableProfilePayload:
        payload = self._request("GET", f"/tables/{table_name}")
        return TableProfilePayload.model_validate(payload)

    def ask(self, question: str, *, use_test_model: bool = False) -> QueryResponsePayload:
        payload = self._request(
            "POST",
            "/query",
            json={"question": question, "use_test_model": use_test_model},
        )
        return QueryResponsePayload.model_validate(payload)

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        assert self.session is not None
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, timeout=self.timeout_seconds, **kwargs)
        except requests.RequestException as exc:
            raise BackendUnavailableError("Could not reach db-agent backend") from exc

        if response.ok:
            return response.json()

        detail = self._extract_error_detail(response)
        raise BackendRequestError(detail)

    @staticmethod
    def _extract_error_detail(response: requests.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f"Backend returned HTTP {response.status_code}"

        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail
        return f"Backend returned HTTP {response.status_code}"
