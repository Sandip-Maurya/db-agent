from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "demo.db"


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_total REAL NOT NULL,
            currency TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE support_tickets (
            ticket_id INTEGER PRIMARY KEY,
            customer_email TEXT NOT NULL,
            topic TEXT NOT NULL,
            priority TEXT NOT NULL,
            opened_at TEXT NOT NULL,
            resolved_at TEXT
        );

        CREATE TABLE marketing_campaigns (
            campaign_id INTEGER PRIMARY KEY,
            channel TEXT NOT NULL,
            campaign_name TEXT NOT NULL,
            budget REAL NOT NULL,
            launch_date TEXT NOT NULL,
            region TEXT NOT NULL
        );
        """
    )

    cur.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1, "Aarav Mehta", "aarav@example.com", "India", "active", "2026-01-05"),
            (2, "Sara Kim", "sara@example.com", "Singapore", "active", "2026-01-09"),
            (3, "Luis Ortega", "luis@example.com", "Spain", "inactive", "2025-12-21"),
        ],
    )
    cur.executemany(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        [
            (101, 1, 1200.0, "INR", "paid", "2026-02-03"),
            (102, 1, 499.0, "INR", "refunded", "2026-02-11"),
            (103, 2, 79.5, "USD", "paid", "2026-02-14"),
        ],
    )
    cur.executemany(
        "INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?)",
        [
            (1001, "aarav@example.com", "refund request", "high", "2026-02-12", "2026-02-13"),
            (1002, "luis@example.com", "login issue", "medium", "2026-02-20", None),
        ],
    )
    cur.executemany(
        "INSERT INTO marketing_campaigns VALUES (?, ?, ?, ?, ?, ?)",
        [
            (501, "google", "Q1 Search Expansion", 15000.0, "2026-01-15", "APAC"),
            (502, "linkedin", "B2B Awareness Sprint", 9000.0, "2026-02-01", "EMEA"),
        ],
    )

    conn.commit()
    conn.close()
    print(f"Created demo database at {DB_PATH}")


if __name__ == "__main__":
    main()
