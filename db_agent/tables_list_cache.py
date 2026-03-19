from __future__ import annotations

import time
from threading import Lock
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Thread-safe in-memory cache with a fixed TTL (wall time via monotonic clock)."""

    def __init__(self, ttl_seconds: float) -> None:
        self._ttl = ttl_seconds
        self._lock = Lock()
        self._expires_at: float = 0.0
        self._value: T | None = None

    def get_or_set(self, factory: Callable[[], T]) -> T:
        with self._lock:
            now = time.monotonic()
            if self._value is not None and now < self._expires_at:
                return self._value
            self._value = factory()
            self._expires_at = now + self._ttl
            return self._value
