"""Small process-local caches for frequently read guild configuration."""

from __future__ import annotations

import os
import threading
import time
from collections import OrderedDict
from typing import Generic, TypeVar


K = TypeVar('K')
V = TypeVar('V')
MISSING = object()


class TTLCache(Generic[K, V]):
    """A thread-safe, size-bounded TTL cache."""

    def __init__(self, max_size: int, ttl: float):
        self.max_size = max(1, max_size)
        self.ttl = max(0.1, ttl)
        self._items: OrderedDict[K, tuple[float, V]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: K, default=MISSING):
        now = time.monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return default
            expires_at, value = item
            if expires_at <= now:
                del self._items[key]
                return default
            self._items.move_to_end(key)
            return value

    def set(self, key: K, value: V, ttl: float | None = None) -> None:
        expires_at = time.monotonic() + (self.ttl if ttl is None else max(0.1, ttl))
        with self._lock:
            self._items[key] = (expires_at, value)
            self._items.move_to_end(key)
            while len(self._items) > self.max_size:
                self._items.popitem(last=False)

    def pop(self, key: K) -> None:
        with self._lock:
            self._items.pop(key, None)

    def pop_guild(self, guild_id: int) -> None:
        with self._lock:
            for key in tuple(self._items):
                if isinstance(key, tuple) and key and key[0] == guild_id:
                    del self._items[key]


guild_cache: TTLCache[int, object] = TTLCache(
    max_size=int(os.getenv('GUILD_CACHE_SIZE', '75000')),
    ttl=float(os.getenv('GUILD_CACHE_TTL', '300')),
)
filter_cache: TTLCache[tuple, bool] = TTLCache(
    max_size=int(os.getenv('FILTER_CACHE_SIZE', '200000')),
    ttl=float(os.getenv('FILTER_CACHE_TTL', '60')),
)
webhook_cache: TTLCache[int, object | None] = TTLCache(
    max_size=int(os.getenv('WEBHOOK_CACHE_SIZE', '100000')),
    ttl=float(os.getenv('WEBHOOK_CACHE_TTL', '3600')),
)


def invalidate_guild(guild_id: int) -> None:
    """Invalidate locally cached settings after a settings interaction."""

    guild_cache.pop(guild_id)
    filter_cache.pop_guild(guild_id)
