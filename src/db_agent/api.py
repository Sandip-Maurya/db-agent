from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from .app_runner import AgentApplication
from .bootstrap import build_app_container


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    use_test_model: bool = False


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: dict


@lru_cache(maxsize=1)
def get_application() -> AgentApplication:
    return AgentApplication(build_app_container())


app = FastAPI(title="db-agent-app", version="0.4.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/tables")
def tables() -> dict:
    application = get_application()
    return application.container.facade.list_tables().model_dump()


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    application = get_application()
    try:
        answer = (
            application.ask_with_test_model(request.question)
            if request.use_test_model
            else application.ask(request.question)
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return QueryResponse(answer=answer.model_dump())
