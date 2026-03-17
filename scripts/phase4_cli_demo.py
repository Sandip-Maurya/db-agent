from __future__ import annotations

from pprint import pprint

from src.app_runner import AgentApplication
from src.bootstrap import build_app_container

if __name__ == "__main__":
    app = AgentApplication(build_app_container())

    print("=== PHASE 4 TABLE OVERVIEW ===")
    pprint(app.container.facade.list_tables().model_dump())

    print("\n=== PHASE 4 TEST-MODEL AGENT OUTPUT ===")
    result = app.ask("What is the orders table about and what currencies appear in it?")
    pprint(result.model_dump())
