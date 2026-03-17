from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field


class QuerySafetyPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    max_rows: int = 200
    read_only: bool = True
    blocked_keywords: tuple[str, ...] = Field(
        default=(
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "truncate",
            "create",
            "grant",
            "revoke",
            "comment",
            "attach",
            "detach",
            "copy",
            "unload",
        )
    )

    def validate_sql(self, sql: str) -> None:
        normalized = re.sub(r"\s+", " ", sql.strip().lower())
        if not normalized:
            raise ValueError("SQL cannot be empty.")
        if ";" in normalized.rstrip(";"):
            raise ValueError("Only a single SQL statement is allowed.")
        if self.read_only:
            for keyword in self.blocked_keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", normalized):
                    raise ValueError(f"Blocked SQL keyword detected: {keyword}")
        if not re.search(r"\blimit\b", normalized):
            raise ValueError("Queries must include an explicit LIMIT clause.")
