"""In-memory recommendation cache."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

_TTL = 1800


class RecommendationCache:
    def __init__(self, ttl: int = _TTL) -> None:
        self._ttl = ttl
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._hits = 0
        self._misses = 0

    def _make_key(self, track_a: Any, track_b: Any, compatibility: Any) -> str:
        raw = json.dumps(
            {"track_a": track_a, "track_b": track_b, "compatibility": compatibility},
            sort_keys=True,
            default=str,
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def get(
        self, track_a: Any, track_b: Any, compatibility: Any
    ) -> dict[str, Any] | None:
        key = self._make_key(track_a, track_b, compatibility)
        entry = self._cache.get(key)
        if entry is not None:
            ts, data = entry
            if time.monotonic() - ts < self._ttl:
                self._hits += 1
                return data
            del self._cache[key]
        self._misses += 1
        return None

    def set(
        self, track_a: Any, track_b: Any, compatibility: Any, data: dict[str, Any]
    ) -> None:
        key = self._make_key(track_a, track_b, compatibility)
        self._cache[key] = (time.monotonic(), data)

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, Any]:
        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
        }


recommendation_cache = RecommendationCache()
