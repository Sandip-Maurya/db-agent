from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .agent_models import AgentAnswer
from .app_runner import AgentApplication
from .bootstrap import build_app_container
from .config import AppSettings
from .domain import TableProfile
from .tool_models import ListTablesOutput


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    app_name: str
    environment: str
    dialect: str
    database_name: str
    default_query_limit: int
    max_rows_per_query: int
    max_sample_rows: int


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    use_test_model: bool = False


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: AgentAnswer


@lru_cache(maxsize=1)
def get_application() -> AgentApplication:
    return AgentApplication(build_app_container())


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()


app = FastAPI(title="db-agent", version="0.5.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    overview = get_application().container.facade.list_tables()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
        dialect=overview.dialect,
        database_name=overview.database_name,
        default_query_limit=settings.default_query_limit,
        max_rows_per_query=settings.max_rows_per_query,
        max_sample_rows=settings.max_sample_rows,
    )


@app.get("/tables", response_model=ListTablesOutput)
def tables() -> ListTablesOutput:
    application = get_application()
    return application.container.facade.list_tables()


@app.get("/tables/{table_name}", response_model=TableProfile)
def table_detail(table_name: str) -> TableProfile:
    application = get_application()
    try:
        return application.container.facade.describe_table(table_name).profile
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    application = get_application()

    try:
        answer = (
            application.ask_with_test_model(request.question)
            if request.use_test_model
            else application.ask(request.question)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Unexpected query failure") from exc

    return QueryResponse(answer=answer)
