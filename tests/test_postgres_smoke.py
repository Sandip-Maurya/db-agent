from db_agent.config import AppSettings
from db_agent.factory import create_database_adapter

def test_postgres_adapter_smoke():
    settings = AppSettings()
    adapter = create_database_adapter(settings)
    tables = adapter.list_tables()
    assert isinstance(tables, list)
    