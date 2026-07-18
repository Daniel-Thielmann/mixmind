"""Internal metrics for LLM operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ModelStats:
    total_calls: int = 0
    successes: int = 0
    failures: int = 0
    timeouts: int = 0
    rate_limits: int = 0
    json_errors: int = 0
    total_latency: float = 0.0


class LLMMetricsCollector:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.requests: int = 0
        self.success: int = 0
        self.fallbacks: int = 0
        self.timeouts: int = 0
        self.rate_limits: int = 0
        self.json_errors: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self._model_stats: dict[str, ModelStats] = {}

    def record_request(self) -> None:
        self.requests += 1

    def record_success(self, model: str, latency: float) -> None:
        self.success += 1
        stats = self._model_stats.setdefault(model, ModelStats())
        stats.total_calls += 1
        stats.successes += 1
        stats.total_latency += latency

    def record_fallback(self) -> None:
        self.fallbacks += 1

    def record_timeout(self, model: str) -> None:
        self.timeouts += 1
        stats = self._model_stats.setdefault(model, ModelStats())
        stats.total_calls += 1
        stats.timeouts += 1
        stats.failures += 1

    def record_rate_limit(self, model: str) -> None:
        self.rate_limits += 1
        stats = self._model_stats.setdefault(model, ModelStats())
        stats.total_calls += 1
        stats.rate_limits += 1
        stats.failures += 1

    def record_json_error(self) -> None:
        self.json_errors += 1

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        self.cache_misses += 1

    @property
    def average_latency(self) -> float:
        total = sum(s.total_latency for s in self._model_stats.values())
        total_calls = sum(s.total_calls for s in self._model_stats.values())
        return total / max(1, total_calls)

    def stats(self) -> dict[str, Any]:
        return {
            "requests": self.requests,
            "success": self.success,
            "fallbacks": self.fallbacks,
            "timeouts": self.timeouts,
            "rate_limits": self.rate_limits,
            "json_errors": self.json_errors,
            "average_latency": round(self.average_latency, 3),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
        }


llm_metrics = LLMMetricsCollector()
