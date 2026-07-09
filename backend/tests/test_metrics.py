"""Tests for LLMMetricsCollector."""

from app.ai.metrics import LLMMetricsCollector


class TestLLMMetricsCollector:
    def test_initial_stats(self) -> None:
        m = LLMMetricsCollector()
        s = m.stats()
        assert s["requests"] == 0
        assert s["success"] == 0
        assert s["fallbacks"] == 0
        assert s["timeouts"] == 0
        assert s["rate_limits"] == 0
        assert s["json_errors"] == 0

    def test_record_request(self) -> None:
        m = LLMMetricsCollector()
        m.record_request()
        assert m.stats()["requests"] == 1

    def test_record_success(self) -> None:
        m = LLMMetricsCollector()
        m.record_success("model-a", 1.5)
        s = m.stats()
        assert s["success"] == 1
        assert s["average_latency"] == 1.5

    def test_record_fallback(self) -> None:
        m = LLMMetricsCollector()
        m.record_fallback()
        assert m.stats()["fallbacks"] == 1

    def test_record_timeout(self) -> None:
        m = LLMMetricsCollector()
        m.record_timeout("model-a")
        s = m.stats()
        assert s["timeouts"] == 1

    def test_record_rate_limit(self) -> None:
        m = LLMMetricsCollector()
        m.record_rate_limit("model-a")
        s = m.stats()
        assert s["rate_limits"] == 1

    def test_record_json_error(self) -> None:
        m = LLMMetricsCollector()
        m.record_json_error()
        assert m.stats()["json_errors"] == 1

    def test_cache_hit_miss(self) -> None:
        m = LLMMetricsCollector()
        m.record_cache_hit()
        m.record_cache_miss()
        s = m.stats()
        assert s["cache_hits"] == 1
        assert s["cache_misses"] == 1

    def test_average_latency_multiple_models(self) -> None:
        m = LLMMetricsCollector()
        m.record_success("a", 1.0)
        m.record_success("b", 3.0)
        assert m.average_latency == 2.0

    def test_average_latency_no_data(self) -> None:
        m = LLMMetricsCollector()
        assert m.average_latency == 0.0

    def test_reset(self) -> None:
        m = LLMMetricsCollector()
        m.record_request()
        m.record_success("a", 1.0)
        m.reset()
        s = m.stats()
        assert s["requests"] == 0
        assert s["success"] == 0
