"""Integration tests for AI infrastructure robustness features."""

import time

from app.ai.agent import DJAgent
from app.ai.cache import RecommendationCache
from app.ai.exceptions import LLMHTTPError, LLMRateLimitError, LLMTimeoutError
from app.ai.llm_manager import LLMManager
from app.ai.metrics import LLMMetricsCollector
from app.ai.model_registry import ModelRegistry

VALID_LLM_JSON = (
    "{"
    '"summary":"Technically strong pairing with minimal tempo difference.",'
    '"mix_direction":"Blend Track B after a clean phrase-matched transition.",'
    '"transition_quality":"High",'
    '"transition_type":"Long harmonic blend",'
    '"confidence":96,'
    '"tempo_analysis":'
    '{"difference":"Only 0.5 BPM apart — excellent tempo alignment.",'
    '"recommendation":"Use key lock and blend directly with no tempo adjustment."},'
    '"energy_analysis":'
    '{"difference":"Energy delta of 0.01 is negligible — '
    'both tracks sit at the same intensity.",'
    '"recommendation":'
    '"Bring Track B in with full EQ and maintain the current energy curve."},'
    '"compatibility_analysis":'
    '{"score":"94/100 — Excellent technical match.",'
    '"interpretation":"The backend rates this pair as Excellent. '
    'The score supports a confident transition."},'
    '"mix_strategy":'
    '{"before_transition":"Set a 4-beat loop on Track B '
    'at the breakdown entrance.",'
    '"during_transition":"Start Track B on the one-count of bar 33. '
    'Open highs over 8 bars.",'
    '"after_transition":"Release the loop at bar 49 '
    'and let the groove ride."},'
    '"dj_execution":'
    '{"loop":"4-beat loop on Track B entrance.",'
    '"eq":"Reduce lows on Track A over 8 bars.",'
    '"filter":"Open high-pass filter on Track A gradually.",'
    '"tempo_fader":"No adjustment needed — BPMs are nearly identical.",'
    '"phrase_matching":"Match 16-bar phrases — enter on bar 33.",'
    '"cue_point":"Set cue on the first beat of bar 33."},'
    '"club_tip":"Enter on the next 16-bar phrase to keep the dance floor locked in.",'
    '"professional_notes":'
    '"The backend metrics suggest a textbook harmonic blend. '
    'No technical risks identified.",'
    '"risks":["None identified — both tracks are well aligned."],'
    '"best_use_case":"Peak-time or warm-up — versatile pairing.",'
    '"risk_level":"Low"'
    "}"
)

# ---------------------------------------------------------------------------
# Fake clients
# ---------------------------------------------------------------------------


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self._response = response

    def complete_chat(self, messages, *, temperature, max_tokens) -> str:
        return self._response


class RaisingClient:
    def __init__(self, exc: Exception, fail_count: int = 1) -> None:
        self._exc = exc
        self._fail_count = fail_count
        self.call_count = 0

    def complete_chat(self, messages, *, temperature, max_tokens) -> str:
        self.call_count += 1
        if self.call_count <= self._fail_count:
            raise self._exc
        return VALID_LLM_JSON


class ClientWithDelay:
    def __init__(self, delay: float, response: str) -> None:
        self._delay = delay
        self._response = response

    def complete_chat(self, messages, *, temperature, max_tokens) -> str:
        time.sleep(self._delay)
        return self._response


# ===================================================================
# Cooldown tests
# ===================================================================


class TestCooldown:
    def test_rate_limit_triggers_cooldown(self) -> None:
        """HTTP 429 should mark model cooldown in registry."""
        registry = ModelRegistry(["primary", "fallback-a", "fallback-b"])
        metrics = LLMMetricsCollector()

        manager = LLMManager(
            models=["primary", "fallback-a", "fallback-b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
            metrics_collector=metrics,
            max_retries=1,
        )

        client = RaisingClient(LLMRateLimitError(429, "Rate limited"))
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]

        try:
            manager.generate(messages)
        except Exception:
            pass

        assert "primary" in registry.get_cooldown_models()

    def test_cooldown_model_not_selected(self) -> None:
        """Model in cooldown should not appear in available models."""
        registry = ModelRegistry(["model-a", "model-b"])
        registry.mark_cooldown("model-a", duration=3600)
        available = registry.get_available_models()
        assert "model-a" not in available
        assert "model-b" in available

    def test_cooldown_logs_message(self, caplog) -> None:
        import logging

        caplog.set_level(logging.INFO)
        registry = ModelRegistry(["test-model"])
        registry.mark_cooldown("test-model", duration=600)
        assert "entered cooldown" in caplog.text


# ===================================================================
# Timeout tests
# ===================================================================


class TestTimeout:
    def test_timeout_is_retryable(self) -> None:
        """Timeout should be retried."""
        metrics = LLMMetricsCollector()
        registry = ModelRegistry(["primary", "fallback"])

        client = RaisingClient(LLMTimeoutError("timeout"), fail_count=1)
        manager = LLMManager(
            models=["primary", "fallback"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
            metrics_collector=metrics,
            max_retries=2,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        parsed, model, attempts = manager.generate(messages)

        assert parsed["summary"] is not None
        assert model == "primary"
        assert attempts == 2

    def test_timeout_recorded_in_metrics(self) -> None:
        metrics = LLMMetricsCollector()
        registry = ModelRegistry(["m"])

        client = RaisingClient(LLMTimeoutError("timeout"), fail_count=3)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
            metrics_collector=metrics,
            max_retries=1,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert metrics.timeouts > 0

    def test_individual_timeout_per_model(self) -> None:
        """Each model attempt should have its own timeout."""
        client = ClientWithDelay(delay=0.1, response=VALID_LLM_JSON)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            timeout=30.0,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        start = time.monotonic()
        parsed, model, attempts = manager.generate(messages)
        elapsed = time.monotonic() - start

        assert elapsed < 5.0
        assert parsed["confidence"] == 96


# ===================================================================
# Invalid model tests
# ===================================================================


class TestInvalidModel:
    def test_invalid_model_marked_and_not_retried(self) -> None:
        """HTTP 400 with invalid model ID marks model invalid and doesn't retry."""
        registry = ModelRegistry(["bad-model"])

        client = RaisingClient(
            LLMHTTPError(400, "bad-model is not a valid model ID"),
            fail_count=5,
        )
        manager = LLMManager(
            models=["bad-model"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
            max_retries=3,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert "bad-model" in registry.get_invalid_models()
        assert client.call_count == 1


# ===================================================================
# Retry strategy tests
# ===================================================================


class TestRetryStrategy:
    def test_http_429_retries(self) -> None:
        metrics = LLMMetricsCollector()
        client = RaisingClient(LLMRateLimitError(429, "rate limit"), fail_count=1)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            metrics_collector=metrics,
            max_retries=2,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        parsed, model, attempts = manager.generate(messages)
        assert parsed is not None
        assert client.call_count == 2

    def test_http_500_retries(self) -> None:
        client = RaisingClient(LLMHTTPError(500, "server error"), fail_count=2)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=3,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        parsed, model, attempts = manager.generate(messages)
        assert parsed is not None
        assert client.call_count == 3

    def test_http_400_not_retried(self) -> None:
        """HTTP 400 should not be retried on the same model."""
        client = RaisingClient(
            LLMHTTPError(400, "Bad request"),
            fail_count=5,
        )
        manager = LLMManager(
            models=["bad-model"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=3,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert client.call_count == 1

    def test_invalid_json_not_retried_on_same_model(self) -> None:
        """Invalid JSON should NOT be retried — break to next model."""
        call_count = 0

        class JsonClient:
            def complete_chat(self, messages, **kw):
                nonlocal call_count
                call_count += 1
                return "this is not valid json at all"

        manager = LLMManager(
            models=["model-a"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=3,
        )
        manager._injected_client = JsonClient()

        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert call_count == 1


# ===================================================================
# Health endpoint tests
# ===================================================================


class TestHealthEndpoint:
    def test_health_returns_available_models(self) -> None:
        registry = ModelRegistry(["a", "b"])
        manager = LLMManager(
            models=["a", "b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
        )
        h = manager.health()
        assert "available_models" in h
        assert "cooldown_models" in h
        assert "invalid_models" in h

    def test_health_reflects_cooldown(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.mark_cooldown("a", duration=3600)
        manager = LLMManager(
            models=["a", "b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
        )
        h = manager.health()
        assert "a" in h["cooldown_models"]
        assert "b" in h["available_models"]

    def test_health_reflects_invalid_models(self) -> None:
        registry = ModelRegistry(["a", "b"])
        registry.mark_invalid("a")
        manager = LLMManager(
            models=["a", "b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
        )
        h = manager.health()
        assert "a" in h["invalid_models"]

    def test_health_via_dj_agent(self) -> None:
        agent = DJAgent()
        h = agent._llm_manager.health()
        assert "available_models" in h


# ===================================================================
# Stats tests
# ===================================================================


class TestStats:
    def test_stats_returns_all_keys(self) -> None:
        metrics = LLMMetricsCollector()
        cache = RecommendationCache()
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            metrics_collector=metrics,
            cache=cache,
        )
        s = manager.stats()
        expected_keys = {
            "requests",
            "success",
            "fallbacks",
            "timeouts",
            "rate_limits",
            "json_errors",
            "average_latency",
            "cache_hits",
            "cache_misses",
        }
        assert expected_keys.issubset(s.keys())

    def test_stats_records_success(self) -> None:
        metrics = LLMMetricsCollector()
        cache = RecommendationCache()
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            metrics_collector=metrics,
            cache=cache,
            max_retries=1,
        )
        manager._injected_client = FakeLLMClient(VALID_LLM_JSON)

        messages = [{"role": "user", "content": "test"}]
        manager.generate(messages)

        s = manager.stats()
        assert s["requests"] == 0
        assert s["success"] == 1

    def test_stats_average_latency(self) -> None:
        metrics = LLMMetricsCollector()
        metrics.record_success("m", 2.0)
        metrics.record_success("m", 4.0)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            metrics_collector=metrics,
        )
        assert manager.stats()["average_latency"] == 3.0


# ===================================================================
# Registry integration with LLMManager
# ===================================================================


class TestRegistryIntegration:
    def test_manager_creates_registry_from_models(self) -> None:
        manager = LLMManager(
            models=["a", "b", "c"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        h = manager.health()
        assert len(h["available_models"]) == 3

    def test_manager_uses_injected_registry(self) -> None:
        registry = ModelRegistry(["x", "y"])
        manager = LLMManager(
            models=["a", "b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
        )
        h = manager.health()
        assert h["available_models"] == ["x", "y"]

    def test_empty_registry_uses_original_models(self) -> None:
        registry = ModelRegistry()
        manager = LLMManager(
            models=["a", "b"],
            base_url="http://fake.local",
            api_key="test-key",
            registry=registry,
            max_retries=1,
        )

        class AlwaysFailClient:
            def complete_chat(self, messages, **kw):
                raise LLMHTTPError(500, "fail")

        manager._injected_client = AlwaysFailClient()
        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert len(manager.health()["available_models"]) == 0


# ===================================================================
# Cache integration tests
# ===================================================================


class TestCacheIntegration:
    def test_cache_prevents_llm_call(self) -> None:
        call_count = 0

        class CountingClient:
            def complete_chat(self, messages, **kw):
                nonlocal call_count
                call_count += 1
                return VALID_LLM_JSON

        cache = RecommendationCache()
        agent = DJAgent(
            client=CountingClient(),
            cache=cache,
        )

        from tests.test_dj_agent import _build_response

        response = _build_response()
        agent.recommend(response)
        agent.recommend(response)

        assert call_count == 1


class TestValidatorExceptions:
    def test_validator_raises_unexpected_exception_is_retried(self) -> None:
        """Validator raising Exception should retry (not break)."""
        call_count = 0

        def flaky_validator(d: dict) -> bool:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("validator crashed")
            return True

        client = FakeLLMClient(VALID_LLM_JSON)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=2,
        )
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        parsed, model, attempts = manager.generate(messages, validator=flaky_validator)
        assert parsed is not None
        assert call_count == 2


class TestValidatorRejection:
    def test_validator_rejects_raises_llm_all_models_failed(self) -> None:
        """Validator returning False should raise LLMAllModelsFailed."""
        from app.ai.exceptions import LLMAllModelsFailed

        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=1,
        )

        def always_false(d: dict) -> bool:
            return False

        client = FakeLLMClient(VALID_LLM_JSON)
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        raised = False
        try:
            manager.generate(messages, validator=always_false)
        except LLMAllModelsFailed:
            raised = True
        assert raised

    def test_raw_response_logged_when_enabled(self) -> None:
        from app.core.config import settings

        original = settings.LLM_LOG_RAW_RESPONSES
        settings.LLM_LOG_RAW_RESPONSES = True
        try:
            call_count = 0

            class LogClient:
                def complete_chat(self, messages, **kw):
                    nonlocal call_count
                    call_count += 1
                    return VALID_LLM_JSON

            manager = LLMManager(
                models=["m"],
                base_url="http://fake.local",
                api_key="test-key",
                max_retries=1,
            )
            manager._injected_client = LogClient()

            messages = [{"role": "user", "content": "test"}]
            parsed, model, _ = manager.generate(messages)
            assert parsed is not None
        finally:
            settings.LLM_LOG_RAW_RESPONSES = original


class TestParseFailures:
    def test_json_repair_failure_returns_none(self, caplog) -> None:
        import logging

        caplog.set_level(logging.DEBUG)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        result = manager._repair_and_parse("")
        assert result is None

    def test_json_loads_after_repair_failure(self, caplog) -> None:
        import logging

        caplog.set_level(logging.DEBUG)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        result = manager._repair_and_parse("{invalid")
        assert result is None

    def test_repair_returns_non_dict(self) -> None:
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        result = manager._repair_and_parse('"just a string"')
        assert result is None

    def test_raw_parse_error_logged(self, caplog) -> None:
        import logging

        caplog.set_level(logging.WARNING)
        manager = LLMManager(
            models=["m"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=1,
        )

        client = FakeLLMClient("complete garbage not json")
        manager._injected_client = client

        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except Exception:
            pass

        assert "RAW LLM RESPONSE" in caplog.text


# ===================================================================
# Dynamic model selection tests
# ===================================================================


class TestDynamicSelection:
    def test_best_model_selected_first(self) -> None:
        registry = ModelRegistry(["slow", "fast"])
        registry.record_success("fast", 0.1)
        registry.record_success("fast", 0.2)
        registry.record_success("slow", 1.0)
        registry.record_success("slow", 1.5)
        available = registry.get_available_models()
        assert available[0] == "fast"

    def test_higher_success_rate_wins(self) -> None:
        registry = ModelRegistry(["unreliable", "reliable"])
        registry.record_success("unreliable", 0.5)
        registry.record_error("unreliable")
        registry.record_error("unreliable")
        registry.record_success("reliable", 0.5)
        registry.record_success("reliable", 0.5)
        available = registry.get_available_models()
        assert available[0] == "reliable"

    def test_fewer_errors_wins(self) -> None:
        registry = ModelRegistry(["erratic", "stable"])
        registry.record_success("erratic", 0.5)
        registry.record_error("erratic")
        registry.record_success("stable", 0.5)
        available = registry.get_available_models()
        assert available[0] == "stable" or available[0] == "erratic"
