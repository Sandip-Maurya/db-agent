from __future__ import annotations

import time

from db_agent.tables_list_cache import TTLCache


def test_ttl_cache_reuses_value_within_ttl() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=60.0)
    calls = {"n": 0}

    def factory() -> int:
        calls["n"] += 1
        return 42

    assert cache.get_or_set(factory) == 42
    assert cache.get_or_set(factory) == 42
    assert calls["n"] == 1


def test_ttl_cache_refreshes_after_expiry() -> None:
    cache: TTLCache[int] = TTLCache(ttl_seconds=0.05)
    calls = {"n": 0}

    def factory() -> int:
        calls["n"] += 1
        return calls["n"]

    assert cache.get_or_set(factory) == 1
    time.sleep(0.08)
    assert cache.get_or_set(factory) == 2
    assert calls["n"] == 2
