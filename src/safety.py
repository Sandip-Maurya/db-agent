from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(slots=True)
class QuerySafetyPolicy:
    max_rows: int = 200
    default_limit: int = 50
    read_only: bool = True
    blocked_keywords: tuple[str, ...] = field(
        default=(
            "insert",
            "update",
            "delete",
            "alter",
            "drop",
            "truncate",
            "create",
            "replace",
            "attach",
            "detach",
            "pragma",
            "grant",
            "revoke",
            "copy",
            "unload",
            "merge",
        )
    )

    def validate_sql(self, sql: str) -> str:
        normalized = re.sub(r"\s+", " ", sql.strip())
        lowered = normalized.lower()
        if not normalized:
            raise ValueError("SQL cannot be empty.")
        if ";" in normalized.rstrip(";"):
            raise ValueError("Only a single SQL statement is allowed.")
        if self.read_only:
            for keyword in self.blocked_keywords:
                if re.search(rf"\b{re.escape(keyword)}\b", lowered):
                    raise ValueError(f"Blocked SQL keyword detected: {keyword}")
            if not re.match(r"^\s*(with\b.+?select\b|select\b)", lowered, flags=re.DOTALL):
                raise ValueError("Only SELECT queries are allowed.")
        sql_with_limit = self._ensure_limit(normalized)
        self._validate_limit_value(sql_with_limit)
        return sql_with_limit

    def _ensure_limit(self, sql: str) -> str:
        sql = sql.rstrip().rstrip(";").rstrip()
        lowered = sql.lower()
        if re.search(r"\blimit\s+\d+\b", lowered):
            return sql
        return f"{sql.rstrip()}\nLIMIT {self.default_limit}"

    def _validate_limit_value(self, sql: str) -> None:
        match = re.search(r"\blimit\s+(\d+)\b", sql.lower())
        if not match:
            raise ValueError("A LIMIT clause is required.")
        limit_value = int(match.group(1))
        if limit_value > self.max_rows:
            raise ValueError(
                f"LIMIT {limit_value} exceeds the configured maximum of {self.max_rows}."
            )
