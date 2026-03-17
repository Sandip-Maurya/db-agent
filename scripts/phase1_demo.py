from __future__ import annotations

from pprint import pprint

from src import AppSettings, SchemaExplorerService, create_database_adapter


def main() -> None:
    settings = AppSettings()
    adapter = create_database_adapter(settings)
    service = SchemaExplorerService(adapter)

    snapshot = service.overview()
    print("=== DATABASE OVERVIEW ===")
    print(f"Dialect: {snapshot.dialect}")
    print(f"Database: {snapshot.database_name}")
    print(f"Tables: {[table.name for table in snapshot.tables]}")

    print("\n=== TABLE PROFILE: orders ===")
    order_profile = service.describe_table("orders")
    pprint(order_profile.model_dump())

    print("\n=== SAFE QUERY DEMO ===")
    result = service.query(
        """
        SELECT status, COUNT(*) AS order_count, ROUND(SUM(order_total), 2) AS gross_revenue
        FROM orders
        GROUP BY status
        ORDER BY gross_revenue DESC
        LIMIT 10
        """
    )
    pprint(result.model_dump())


if __name__ == "__main__":
    main()
