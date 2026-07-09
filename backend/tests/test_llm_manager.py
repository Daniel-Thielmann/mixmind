"""Direct unit tests for LLMManager — repair & parse logic."""

from app.ai.exceptions import LLMAllModelsFailed
from app.ai.llm_manager import LLMManager


def _manager() -> LLMManager:
    return LLMManager(
        models=["test-model"],
        base_url="http://fake.local",
        api_key="test-key",
    )


# ===================================================================
# _extract_first_json
# ===================================================================


class TestExtractFirstJSON:
    def test_normal_object(self) -> None:
        m = _manager()
        raw = 'prefix {"a":1} suffix'
        assert m._extract_first_json(raw) == '{"a":1}'

    def test_two_objects_returns_first(self) -> None:
        m = _manager()
        raw = '{"a":1}{"b":2}'
        assert m._extract_first_json(raw) == '{"a":1}'

    def test_braces_inside_string(self) -> None:
        m = _manager()
        raw = '{"msg":"hello {world}","nested":{"a":1}}'
        assert m._extract_first_json(raw) == raw

    def test_escaped_quotes_inside_string(self) -> None:
        m = _manager()
        raw = '{"msg":"he said \\"hello\\"","nested":{"a":1}}'
        assert m._extract_first_json(raw) == raw

    def test_truncated_no_close_brace(self) -> None:
        m = _manager()
        raw = '{"a":1,"b":2'
        assert m._extract_first_json(raw) == raw

    def test_no_json_returns_original(self) -> None:
        m = _manager()
        raw = "just text"
        assert m._extract_first_json(raw) == raw

    def test_three_objects_returns_first(self) -> None:
        m = _manager()
        raw = '{"a":1}{"b":2}{"c":3}'
        assert m._extract_first_json(raw) == '{"a":1}'

    def test_object_with_array(self) -> None:
        m = _manager()
        raw = '{"items":[1,{"x":"y"},3]} trailing'
        assert m._extract_first_json(raw) == '{"items":[1,{"x":"y"},3]}'


# ===================================================================
# _repair_and_parse
# ===================================================================


class TestRepairAndParse:
    def test_valid_json(self) -> None:
        m = _manager()
        result = m._repair_and_parse('{"summary":"hello","confidence":50}')
        assert result is not None
        assert result["summary"] == "hello"

    def test_two_jsons_uses_first(self) -> None:
        m = _manager()
        result = m._repair_and_parse('{"a":1}{"b":2}')
        assert result is not None
        assert result["a"] == 1
        assert "b" not in result

    def test_with_extra_text(self) -> None:
        m = _manager()
        raw = 'Here:\n```\n{"summary":"test"}\n```\nDone.'
        result = m._repair_and_parse(raw)
        assert result is not None
        assert result["summary"] == "test"

    def test_truncated_missing_brace(self) -> None:
        m = _manager()
        result = m._repair_and_parse('{"summary":"hello"')
        assert result is not None
        assert result["summary"] == "hello"

    def test_trailing_comma(self) -> None:
        m = _manager()
        result = m._repair_and_parse('{"a":"b","c":"d",}')
        assert result is not None
        assert result["a"] == "b"
        assert result["c"] == "d"

    def test_single_quotes(self) -> None:
        m = _manager()
        result = m._repair_and_parse("{'a':'b'}")
        assert result is not None
        assert result["a"] == "b"

    def test_returns_none_for_gibberish(self) -> None:
        m = _manager()
        assert m._repair_and_parse("this is not json at all") is None

    def test_returns_none_for_empty(self) -> None:
        m = _manager()
        assert m._repair_and_parse("") is None

    def test_returns_none_for_whitespace(self) -> None:
        m = _manager()
        assert m._repair_and_parse("   \n  ") is None


# ===================================================================
# _normalize
# ===================================================================


class TestNormalize:
    def test_fills_missing_text_fields(self) -> None:
        m = _manager()
        from app.ai.llm_manager import LLMMetrics

        metrics = LLMMetrics()
        parsed = {"summary": "Test"}
        m._normalize(parsed, metrics)
        assert parsed["summary"] == "Test"
        assert parsed["mix_direction"] == "No direction provided."
        assert parsed["confidence"] == 50
        assert parsed["club_tip"] == ""
        assert parsed["professional_notes"] == ""

    def test_does_not_overwrite_existing_values(self) -> None:
        m = _manager()
        from app.ai.llm_manager import LLMMetrics

        metrics = LLMMetrics()
        parsed = {
            "summary": "Custom summary",
            "confidence": 80,
            "mix_direction": "Blend",
            "club_tip": "Watch the highs",
            "professional_notes": "",
        }
        m._normalize(parsed, metrics)
        assert parsed["summary"] == "Custom summary"
        assert parsed["confidence"] == 80
        assert parsed["mix_direction"] == "Blend"
        assert parsed["club_tip"] == "Watch the highs"

    def test_ignores_unknown_fields(self) -> None:
        m = _manager()
        from app.ai.llm_manager import LLMMetrics

        metrics = LLMMetrics()
        parsed = {
            "summary": "Test",
            "risk_level": "Low",
            "tempo_analysis": {"difference": "Small"},
        }
        m._normalize(parsed, metrics)
        assert parsed["summary"] == "Test"
        assert "risk_level" in parsed  # kept but not normalized
        assert "tempo_analysis" in parsed  # kept but not normalized

    def test_records_filled_fields_in_metrics(self) -> None:
        m = _manager()
        from app.ai.llm_manager import LLMMetrics

        metrics = LLMMetrics()
        parsed = {"summary": "Test"}
        m._normalize(parsed, metrics)
        assert "mix_direction" in metrics.filled_fields


# ===================================================================
# Retryable errors (M2)
# ===================================================================


class TestIsRetryable:
    def test_429_is_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        err = LLMHTTPError(429, "Rate limited")
        assert err.is_retryable() is True
        assert err.status_code == 429

    def test_500_is_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        err = LLMHTTPError(500, "Internal error")
        assert err.is_retryable() is True

    def test_502_is_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(502, "").is_retryable() is True

    def test_503_is_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(503, "").is_retryable() is True

    def test_504_is_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(504, "").is_retryable() is True

    def test_400_is_not_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(400, "").is_retryable() is False

    def test_403_is_not_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(403, "").is_retryable() is False

    def test_0_is_not_retryable(self) -> None:
        from app.ai.exceptions import LLMHTTPError

        assert LLMHTTPError(0, "").is_retryable() is False

    def test_llm_rate_limit_error_is_retryable(self) -> None:
        from app.ai.exceptions import LLMRateLimitError

        err = LLMRateLimitError(429, "Rate limited")
        assert err.is_retryable() is True


# ===================================================================
# Backoff (M2)
# ===================================================================


class TestBackoff:
    def test_exponential_backoff(self) -> None:
        """backoff(base=1) should be 1, 2, 4, ..."""
        m = _manager()
        m._backoff_base = 1.0
        assert m._backoff(0) == 1.0
        assert m._backoff(1) == 2.0
        assert m._backoff(2) == 4.0

    def test_backoff_with_custom_base(self) -> None:
        m = _manager()
        m._backoff_base = 2.0
        assert m._backoff(0) == 2.0
        assert m._backoff(1) == 4.0
        assert m._backoff(2) == 8.0


# ===================================================================
# generate — validator callback
# ===================================================================


class TestGenerateWithValidator:
    def test_validator_rejects_response_triggers_all_models_fail(self) -> None:
        m = LLMManager(
            models=["model-a", "model-b"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        messages = [{"role": "user", "content": "test"}]

        def always_false(d: dict) -> bool:
            return False

        try:
            m.generate(messages, validator=always_false)
        except LLMAllModelsFailed:
            pass
        else:
            raise AssertionError("Expected LLMAllModelsFailed")
