# db-agent-app phase 4

This phase integrates the earlier layers into a single app.

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

```bash
python -m db_agent_app --list-tables
python -m db_agent_app --describe-table orders
python -m db_agent_app --test-model "What is the orders table about?"
```

With a real model configured:

```bash
set DB_AGENT_MODEL__PROVIDER_MODEL=openai:gpt-5-mini
python -m db_agent_app "What currencies appear in orders?"
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
set DB_AGENT_DB__DIALECT=sqlite
set DB_AGENT_DB__DATABASE=demo.db
```

### Postgres/MySQL/Redshift

Prefer a full URI:

```bash
set DB_AGENT_DB__DIALECT=postgres
set DB_AGENT_DB__URI=postgresql+psycopg://user:pass@localhost:5432/mydb
```

You can also use component settings:

```bash
set DB_AGENT_DB__HOST=localhost
set DB_AGENT_DB__PORT=5432
set DB_AGENT_DB__USERNAME=user
set DB_AGENT_DB__PASSWORD=pass
set DB_AGENT_DB__DATABASE=mydb
```
