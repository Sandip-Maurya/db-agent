from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic_ai import Agent, RunContext

from .agent_deps import AgentDeps
from .agent_models import AgentAnswer, EvidenceItem

BASE_INSTRUCTIONS = """
You are a read-only database analyst.
Your job is to answer questions about the available data and explain tables clearly.
Always ground your answer in tool results.
Never invent tables, columns, joins, or values.
Prefer to inspect metadata before running SQL.
Use SQL only for read-only analytical retrieval.
If the question cannot be answered from available data, say so plainly.
Return a concise answer, assumptions, evidence, confidence, and whether follow-up is needed.
""".strip()


def build_database_agent(model: Any | None = None) -> Agent[AgentDeps, AgentAnswer]:
    agent = Agent(
        model or "test",
        deps_type=AgentDeps,
        output_type=AgentAnswer,
        instructions=BASE_INSTRUCTIONS,
    )

    @agent.instructions
    def runtime_instructions(ctx: RunContext[AgentDeps]) -> str:
        settings = ctx.deps.settings
        allowed = ", ".join(ctx.deps.allowed_tables) if ctx.deps.allowed_tables else "none"
        return (
            f"Database dialect: {settings.db.dialect}. "
            f"Database name: {settings.db.database}. "
            f"Allowed tables: {allowed}. "
            f"Max sample rows: {settings.max_sample_rows}. "
            f"Max rows per query: {settings.max_rows_per_query}. "
            "For schema questions, prefer list_tables, describe_table, and sample_rows. "
            "For analytical questions, inspect metadata first and then use run_query if needed."
        )

    @agent.tool
    def list_tables(ctx: RunContext[AgentDeps]) -> dict[str, Any]:
        """List all accessible tables with brief descriptions and column names."""
        return ctx.deps.facade.list_tables().model_dump()

    @agent.tool
    def describe_table(ctx: RunContext[AgentDeps], table_name: str) -> dict[str, Any]:
        """Describe one table, including columns, sample rows, and inferred metadata."""
        return ctx.deps.facade.describe_table(table_name).model_dump()

    @agent.tool
    def sample_rows(ctx: RunContext[AgentDeps], table_name: str, limit: int = 5) -> dict[str, Any]:
        """Return a small sample of rows from a table to understand its contents."""
        safe_limit = min(max(1, limit), ctx.deps.settings.max_sample_rows)
        return ctx.deps.facade.sample_rows(table_name, limit=safe_limit).model_dump()

    @agent.tool
    def run_query(ctx: RunContext[AgentDeps], sql: str) -> dict[str, Any]:
        """Execute a read-only SQL query after the application's safety policy validates it."""
        return ctx.deps.facade.run_query(sql).model_dump()

    return agent


def build_default_answer(
    *,
    question: str,
    available_tables: Sequence[str],
    sql: str | None = None,
) -> AgentAnswer:
    evidence = [
        EvidenceItem(kind="tables", detail=", ".join(available_tables) or "no tables discovered"),
    ]
    if sql:
        evidence.append(EvidenceItem(kind="query", detail=sql))

    return AgentAnswer(
        answer=(
            "This is a placeholder answer shape for deterministic local testing. "
            f"Question received: {question}"
        ),
        assumptions=["The demo database is representative of the target schema."],
        evidence=evidence,
        sql_executed=sql,
        confidence="medium",
        needs_followup=False,
    )
