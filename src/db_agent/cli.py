from __future__ import annotations

import argparse
import json
import sys

from .app_runner import AgentApplication
from .bootstrap import build_app_container


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ask questions against a single configured database.")
    parser.add_argument("question", nargs="?", help="Question for the database agent")
    parser.add_argument("--test-model", action="store_true", help="Use Pydantic AI TestModel instead of a real LLM")
    parser.add_argument("--list-tables", action="store_true", help="Print the database overview and exit")
    parser.add_argument("--describe-table", help="Describe a single table and exit")
    parser.add_argument("--sample-table", help="Sample rows from a single table and exit")
    parser.add_argument("--sample-limit", type=int, default=5)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    container = build_app_container()
    app = AgentApplication(container)

    if args.list_tables:
        print(json.dumps(container.facade.list_tables().model_dump(), indent=2, default=str))
        return 0
    if args.describe_table:
        print(json.dumps(container.facade.describe_table(args.describe_table).model_dump(), indent=2, default=str))
        return 0
    if args.sample_table:
        print(json.dumps(container.facade.sample_rows(args.sample_table, limit=args.sample_limit).model_dump(), indent=2, default=str))
        return 0
    if not args.question:
        parser.error("A question is required unless using --list-tables or --describe-table or --sample-table")

    answer = app.ask_with_test_model(args.question) if args.test_model else app.ask(args.question)
    print(json.dumps(answer.model_dump(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
