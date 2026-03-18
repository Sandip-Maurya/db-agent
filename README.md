# db-agent

`db-agent` is a read-only database analyst app built with Pydantic AI. It connects to a single configured database, exposes inspection/query tools to an agent, and lets you ask questions through either a CLI or a FastAPI service.

## Naming and layout

- **Repository / project name:** `db-agent`
- **Python package:** `db_agent`
- **Source layout:** `src/db_agent/`

Use `db_agent` for Python imports and `db-agent` for the installed CLI command.

## Features

- single database connection per app instance
- adapter/factory architecture for sqlite, postgres, mysql, and redshift
- safe read-only querying with automatic `LIMIT` injection
- pydantic-ai agent with typed dependencies and structured output
- CLI and FastAPI entrypoints
- smoke tests and demo scripts

## Setup

```bash
pip install -e .
python -m scripts.create_demo_db
```

## CLI

Run the app either as a module or through the installed console script:

```bash
python -m db_agent --list-tables
python -m db_agent --describe-table orders
python -m db_agent --test-model "What is the orders table about?"

db-agent --list-tables
```

With a real model configured:

```bash
export DB_AGENT_MODEL__PROVIDER_MODEL=openai:gpt-5-mini
python -m db_agent "What currencies appear in orders?"
```

## FastAPI

```bash
python -m scripts.run_api
```

Then call:

- `GET /health`
- `GET /tables`
- `POST /query`

Example body:

```json
{"question": "What is the orders table about?", "use_test_model": true}
```

## Database configuration

### SQLite

```bash
export DB_AGENT_DB__DIALECT=sqlite
export DB_AGENT_DB__DATABASE=demo.db
```

### Postgres / MySQL / Redshift

Prefer a full URI:

```bash
export DB_AGENT_DB__DIALECT=postgres
export DB_AGENT_DB__URI=postgresql+psycopg://user:pass@localhost:5432/mydb
```

You can also use component settings:

```bash
export DB_AGENT_DB__HOST=localhost
export DB_AGENT_DB__PORT=5432
export DB_AGENT_DB__USERNAME=user
export DB_AGENT_DB__PASSWORD=pass
export DB_AGENT_DB__DATABASE=mydb
```

## Project structure

```text
src/db_agent/       Application package
scripts/            Demo and runner scripts
tests/              Smoke tests
```

## Development checks

```bash
python -m pytest -q
python -m db_agent --help
```
