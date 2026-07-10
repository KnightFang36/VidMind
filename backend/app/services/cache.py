# services/cache.py
#
# Upgrade #18 — Caching
#   A tiny, dependency-free TTL cache used for:
#     • retrieval results   (video_id + question -> docs)
#     • final LLM answers    (video_id + question -> answer + sources)
#   Embedding caching is handled separately in embedding.py.
#
# In-process + LRU + TTL keeps things simple and fast. Swap for Redis in a
# multi-worker deployment if you need a shared cache.

from __future__ import annotations

import hashlib
import threading
import time
from collections import OrderedDict
from typing import Any


class TTLCache:
    """Thread-safe LRU cache with per-entry time-to-live."""

    def __init__(self, maxsize: int = 512, ttl_seconds: float = 3600.0) -> None:
        self._maxsize = maxsize
        self._ttl = ttl_seconds
        self._store: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self._lock = threading.Lock()

    @staticmethod
    def make_key(*parts: Any) -> str:
        raw = "\x1f".join(str(p) for p in parts)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at < time.time():
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)   # mark as recently used
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (time.time() + self._ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self._maxsize:
                self._store.popitem(last=False)   # evict least-recently-used

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Shared singletons used across the RAG service.
retrieval_cache = TTLCache(maxsize=512, ttl_seconds=1800.0)   # 30 min
answer_cache = TTLCache(maxsize=512, ttl_seconds=1800.0)      # 30 min