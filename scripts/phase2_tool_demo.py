from __future__ import annotations

from pprint import pprint

from src import AppSettings, DatabaseToolFacade, SchemaExplorerService, create_database_adapter


def main() -> None:
    settings = AppSettings()
    adapter = create_database_adapter(settings)
    service = SchemaExplorerService(adapter)
    tools = DatabaseToolFacade(service)

    print("=== TOOL: list_tables ===")
    pprint(tools.list_tables().model_dump())

    print("\n=== TOOL: describe_table('support_tickets') ===")
    pprint(tools.describe_table("support_tickets").model_dump())

    print("\n=== TOOL: sample_rows('customers', limit=3) ===")
    pprint(tools.sample_rows("customers", limit=3).model_dump())

    print("\n=== TOOL: run_query(...) ===")
    pprint(
        tools.run_query(
            """
            SELECT currency, COUNT(*) AS order_count, ROUND(SUM(order_total), 2) AS gross_revenue
            FROM orders
            GROUP BY currency
            ORDER BY gross_revenue DESC
            LIMIT 10
            """
        ).model_dump()
    )


if __name__ == "__main__":
    main()
