from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="Type of evidence such as table, columns, sample, or query")
    detail: str = Field(description="Human-readable evidence detail")


class AgentAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str = Field(description="Natural language answer to the user's question")
    assumptions: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    sql_executed: str | None = Field(default=None, description="SQL used to answer the question, if any")
    confidence: Literal["low", "medium", "high"] = Field(default="medium")
    needs_followup: bool = Field(default=False)
