from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.pool import StaticPool

from db_agent.sqlalchemy_adapter import SQLAlchemyAdapter


def test_list_table_summaries_light_in_memory_sqlite() -> None:
    """Batch path (get_multi_columns) returns names and columns for all tables."""
    adapter = SQLAlchemyAdapter(
        "sqlite://",
        dialect="sqlite",
        database_name="memory",
        engine_kwargs={
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        },
    )
    with adapter._engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, currency TEXT NOT NULL)"
            )
        )
        conn.execute(text("CREATE TABLE items (item_id INTEGER, order_id INTEGER)"))

    summaries = adapter.list_table_summaries_light()
    by_name = {s.name: s for s in summaries}
    assert set(by_name) == {"items", "orders"}
    assert by_name["orders"].column_names == ["order_id", "currency"]
    assert by_name["items"].column_names == ["item_id", "order_id"]
    assert "Likely one row per order" in (by_name["orders"].description or "")

    adapter.close()
