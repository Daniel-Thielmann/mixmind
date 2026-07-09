"""Tests for RecommendationCache."""

import time

from app.ai.cache import RecommendationCache


class TestRecommendationCache:
    def test_cache_miss_on_empty(self) -> None:
        cache = RecommendationCache()
        result = cache.get({"a": 1}, {"b": 2}, {"c": 3})
        assert result is None

    def test_cache_hit_after_set(self) -> None:
        cache = RecommendationCache()
        track_a = {"filename": "a.mp3", "bpm": 128.0}
        track_b = {"filename": "b.mp3", "bpm": 130.0}
        compat = {"score": 90.0}
        cache.set(track_a, track_b, compat, {"summary": "test"})
        result = cache.get(track_a, track_b, compat)
        assert result is not None
        assert result["summary"] == "test"

    def test_cache_key_is_content_based(self) -> None:
        cache = RecommendationCache()
        data_a = {"filename": "a.mp3", "bpm": 128.0}
        data_b = {"filename": "b.mp3", "bpm": 130.0}
        compat = {"score": 90.0}
        cache.set(data_a, data_b, compat, {"result": "first"})
        result = cache.get(data_a, data_b, compat)
        assert result["result"] == "first"

    def test_cache_key_differs_for_diff_data(self) -> None:
        cache = RecommendationCache()
        ta1 = {"filename": "a.mp3", "bpm": 128.0}
        tb1 = {"filename": "b.mp3", "bpm": 130.0}
        ta2 = {"filename": "c.mp3", "bpm": 120.0}
        tb2 = {"filename": "d.mp3", "bpm": 125.0}
        compat = {"score": 90.0}
        cache.set(ta1, tb1, compat, {"result": "first"})
        result = cache.get(ta2, tb2, compat)
        assert result is None

    def test_cache_expires_after_ttl(self) -> None:
        cache = RecommendationCache(ttl=0.001)
        track_a = {"filename": "a.mp3"}
        track_b = {"filename": "b.mp3"}
        compat = {"score": 90.0}
        cache.set(track_a, track_b, compat, {"summary": "test"})
        time.sleep(0.01)
        result = cache.get(track_a, track_b, compat)
        assert result is None

    def test_clear_empties_cache(self) -> None:
        cache = RecommendationCache()
        cache.set({"a": 1}, {"b": 2}, {"c": 3}, {"data": "x"})
        cache.clear()
        assert cache.get({"a": 1}, {"b": 2}, {"c": 3}) is None
        assert cache.stats()["size"] == 0

    def test_stats(self) -> None:
        cache = RecommendationCache()
        assert cache.stats()["size"] == 0
        assert cache.stats()["hits"] == 0
        assert cache.stats()["misses"] == 0
        cache.get({"a": 1}, {"b": 2}, {"c": 3})
        assert cache.stats()["misses"] == 1
        cache.set({"a": 1}, {"b": 2}, {"c": 3}, {"x": "y"})
        cache.get({"a": 1}, {"b": 2}, {"c": 3})
        assert cache.stats()["hits"] == 1

    def test_clear_resets_stats(self) -> None:
        cache = RecommendationCache()
        cache.get({"a": 1}, {"b": 2}, {"c": 3})
        cache.set({"a": 1}, {"b": 2}, {"c": 3}, {"x": "y"})
        cache.get({"a": 1}, {"b": 2}, {"c": 3})
        cache.clear()
        stats = cache.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0

    def test_key_uses_track_a_track_b_compat(self) -> None:
        cache = RecommendationCache()
        track_a = {"filename": "x.mp3"}
        track_b = {"filename": "y.mp3"}
        compat = {"score": 80.0}
        cache.set(track_a, track_b, compat, {"result": "ok"})
        result = cache.get(track_a, track_b, {"score": 90.0})
        assert result is None
