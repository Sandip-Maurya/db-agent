from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from .agent_models import AgentAnswer
from .app_runner import AgentApplication
from .bootstrap import build_app_container
from .config import AppSettings
from .domain import TableProfile
from .tables_list_cache import TTLCache
from .tool_models import ListTablesOutput

TABLES_LIST_CACHE_TTL_SECONDS = 300.0


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = AppSettings()
    container = build_app_container(settings)
    app.state.settings = settings
    app.state.application = AgentApplication(container)
    app.state.tables_list_cache = TTLCache[ListTablesOutput](
        ttl_seconds=TABLES_LIST_CACHE_TTL_SECONDS
    )

    try:
        yield
    finally:
        container.close()


app = FastAPI(title="db-agent", version="0.5.0", lifespan=lifespan)


def get_application() -> AgentApplication:
    return app.state.application


def get_settings() -> AppSettings:
    return app.state.settings


def _tables_list_cache(request: Request) -> TTLCache[ListTablesOutput]:
    """Return app-scoped cache; lazy-init if lifespan did not run (e.g. some tests)."""
    state = request.app.state
    cache = getattr(state, "tables_list_cache", None)
    if cache is None:
        cache = TTLCache[ListTablesOutput](ttl_seconds=TABLES_LIST_CACHE_TTL_SECONDS)
        state.tables_list_cache = cache
    return cache


@app.get("/health", response_model=HealthResponse)
def health(
    settings: AppSettings = Depends(get_settings),
    application: AgentApplication = Depends(get_application),
) -> HealthResponse:
    adapter = application.container.adapter
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
        dialect=getattr(adapter, "dialect", "unknown"),
        database_name=getattr(adapter, "database_name", "unknown"),
        default_query_limit=settings.default_query_limit,
        max_rows_per_query=settings.max_rows_per_query,
        max_sample_rows=settings.max_sample_rows,
    )


@app.get("/tables", response_model=ListTablesOutput)
def tables(
    request: Request,
    application: AgentApplication = Depends(get_application),
) -> ListTablesOutput:
    cache = _tables_list_cache(request)

    def load() -> ListTablesOutput:
        return application.container.facade.list_tables()

    return cache.get_or_set(load)


@app.get("/tables/{table_name}", response_model=TableProfile)
def table_detail(
    table_name: str, application: AgentApplication = Depends(get_application)
) -> TableProfile:
    try:
        return application.container.facade.describe_table(table_name).profile
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest, application: AgentApplication = Depends(get_application)
) -> QueryResponse:
    try:
        answer = (
            application.ask_with_test_model(request.question)
            if request.use_test_model
            else application.ask(request.question)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected query failure") from exc

    return QueryResponse(answer=answer)
