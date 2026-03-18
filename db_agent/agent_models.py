from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="Type of evidence such as table, columns, sample, or query")
    detail: str = Field(description="Human-readable evidence detail")


class AgentAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(description="Natural language answer to the user's question")
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = Field(default="medium")
    needs_followup: bool = Field(default=False)
    db_query_executed: bool = Field(..., description="Whether sql is required to answer user question. True/False")
    executed_sql: str | None = Field(default=None, description="SQL used to answer the question, if any")
    