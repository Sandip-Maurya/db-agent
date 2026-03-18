# db-agent

`db-agent` is a read-only database analyst app built with Pydantic AI. Phase 5 adds a Streamlit UI on top of the existing FastAPI backend.

## What is included in phase 5

- FastAPI backend health endpoint with configuration summary
- table list endpoint and table-detail endpoint
- Streamlit frontend for schema browsing and NL question answering
- a small typed HTTP client for the Streamlit app
- tests for the API contract and Streamlit client parsing

## Project layout

```text
.db-agent/
├─ db_agent/
│  ├─ api.py
│  └─ streamlit_settings.py
├─ streamlit_app/
│  ├─ app.py
│  ├─ api_client.py
│  ├─ state.py
│  └─ ui_components.py
├─ scripts/
│  └─ run_streamlit.py
└─ tests/
```

## Run the backend

```bash
python -m scripts.run_api
```

## Run the Streamlit UI

```bash
streamlit run streamlit_app/app.py
# or
python -m scripts.run_streamlit
```

## UI environment variables

```bash
export DB_AGENT_UI_BACKEND_BASE_URL=http://127.0.0.1:8000
export DB_AGENT_UI_REQUEST_TIMEOUT_SECONDS=30
export DB_AGENT_UI_DEBUG=false
```

## Suggested next cleanup after applying phase 5

- add a backend lifespan hook for adapter cleanup
- tighten backend exception taxonomy
- add route tests using dependency injection instead of cache mutation
- expose query execution metadata in the structured API response when the agent returns it
