"""Tests for DJAgent — using injected fake clients."""

from app.ai.agent import DJAgent
from app.ai.exceptions import LLMAllModelsFailed, LLMHTTPError
from app.ai.llm_manager import LLMManager
from app.ai.prompts import build_llm_payload
from app.ai.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.core.config import settings
from app.schemas.api import UploadAnalysisResponse
from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.schemas.spectrogram import SpectrogramResult, Spectrograms
from app.schemas.waveform import WaveformResult, Waveforms

# ---------------------------------------------------------------------------
# Fake clients
# ---------------------------------------------------------------------------


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self._response = response

    def complete_chat(self, messages, *, temperature: float, max_tokens: int) -> str:
        return self._response


class RaisingLLMClient:
    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    def complete_chat(self, messages, *, temperature: float, max_tokens: int) -> str:
        raise self._exc


class RetryThenSucceedClient:
    """Fails first *fail_count* calls with retryable error, then returns *response*."""

    def __init__(self, response: str, fail_count: int = 1) -> None:
        self._response = response
        self._fail_count = fail_count
        self.call_count = 0
        self._error = LLMHTTPError(500, "Simulated retryable failure")

    def complete_chat(self, messages, *, temperature: float, max_tokens: int) -> str:
        self.call_count += 1
        if self.call_count <= self._fail_count:
            raise self._error
        return self._response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


VALID_LLM_JSON = (
    "{"
    '"summary":"Technically strong pairing with minimal tempo difference.",'
    '"mix_direction":"Blend Track B after a clean phrase-matched transition.",'
    '"club_tip":"Enter on the next 16-bar phrase to keep the dance floor locked in.",'
    '"professional_notes":'
    '"The backend metrics suggest a textbook harmonic blend. '
    'No technical risks identified.",'
    '"confidence":96'
    "}"
)


def _build_response() -> UploadAnalysisResponse:
    return UploadAnalysisResponse(
        status="success",
        message="Tracks analyzed successfully",
        analysis_id="test-session",
        track_a=AudioAnalysis(
            filename="Track A",
            bpm=128.0,
            energy=0.18,
            duration=210.0,
            sample_rate=44100,
        ),
        track_b=AudioAnalysis(
            filename="Track B",
            bpm=127.5,
            energy=0.17,
            duration=214.0,
            sample_rate=44100,
        ),
        compatibility=CompatibilityResult(
            compatibility_score=94.0,
            tempo_difference=0.5,
            energy_difference=0.01,
            tempo_match="Excellent",
            energy_match="Excellent",
            overall_rating="Excellent",
        ),
        ai_recommendation=AIRecommendationResponse(
            summary="",
            mix_direction="",
            transition_quality="",
            transition_type="",
            confidence=0,
            tempo_analysis=TempoAnalysis(difference="", recommendation=""),
            energy_analysis=EnergyAnalysis(difference="", recommendation=""),
            compatibility_analysis=CompatibilityAnalysis(score="", interpretation=""),
            mix_strategy=MixStrategy(
                before_transition="",
                during_transition="",
                after_transition="",
            ),
            dj_execution=DJExecution(
                loop="",
                eq="",
                filter="",
                tempo_fader="",
                phrase_matching="",
                cue_point="",
            ),
            club_tip="",
            professional_notes="",
            risks=[],
            best_use_case="",
            risk_level="",
        ),
        waveforms=Waveforms(
            track_a=WaveformResult(image_path="", width=1200, height=300),
            track_b=WaveformResult(image_path="", width=1200, height=300),
        ),
        spectrograms=Spectrograms(
            track_a=SpectrogramResult(image_path="", width=1200, height=500),
            track_b=SpectrogramResult(image_path="", width=1200, height=500),
        ),
    )


def _expected_valid() -> AIRecommendationResponse:
    return AIRecommendationResponse(
        ai_provider="openrouter",
        ai_model=settings.OPENROUTER_MODEL,
        ai_retry_count=0,
        ai_fallback_occurred=False,
        dj_score=85,
        mix_difficulty="Very Easy",
        recommended_transition_length="64 bars",
        summary="Technically strong pairing with minimal tempo difference.",
        mix_direction="Blend Track B after a clean phrase-matched transition.",
        transition_quality="High",
        transition_type="Long harmonic blend",
        confidence=96,
        tempo_analysis=TempoAnalysis(
            difference="Only 0.5 BPM apart — excellent tempo alignment.",
            recommendation="Use key lock and blend directly with no tempo adjustment.",
        ),
        energy_analysis=EnergyAnalysis(
            difference=(
                "Energy delta is negligible — both tracks sit at the same intensity."
            ),
            recommendation=(
                "Bring Track B in with full EQ and maintain the current energy curve."
            ),
        ),
        compatibility_analysis=CompatibilityAnalysis(
            score="94/100 — Excellent technical match.",
            interpretation=(
                "The backend rates this pair as Excellent. "
                "The score supports a confident transition."
            ),
        ),
        mix_strategy=MixStrategy(
            before_transition=(
                "Set a 4-beat cue point on Track B at bar 1. "
                "Align phrasing for a 64 bars blend."
            ),
            during_transition=(
                "Start Track B on the one-count. Open highs over 32 bars."
            ),
            after_transition=("Complete the blend by bar 64. Release any loops."),
        ),
        dj_execution=DJExecution(
            loop="4-bar loop on Track B entrance.",
            eq="Reduce lows on Track A over 8 bars. Open Track B with mids first.",
            filter="Apply a high-pass filter on Track A sweeping from 40Hz to 250Hz.",
            tempo_fader="No adjustment needed — BPMs are nearly identical.",
            phrase_matching="Match 16-bar phrases. Enter on bar 1 of a new phrase.",
            cue_point="Set cue on the first beat of the target phrase.",
        ),
        club_tip="Enter on the next 16-bar phrase to keep the dance floor locked in.",
        professional_notes=(
            "The backend metrics suggest a textbook harmonic blend. "
            "No technical risks identified.\n\n"
            "DJ Score: 85/100 — Strong backend compatibility across tempo and energy. "
            "Mix difficulty is very easy. Smooth transition expected. "
            "Recommended transition: 64 bars."
        ),
        risks=[
            "Risk: None identified|Impact: Low|"
            "Mitigation: Standard monitoring during the transition"
        ],
        best_use_case="Peak-time or warm-up",
        risk_level="Low",
        alternative_strategy="Try a loop bridge if the blend feels too long.",
        why_this_strategy=(
            "BPM difference of 0.5 and compatibility of 94/100 "
            "make this a straightforward blend requiring minimal intervention."
        ),
        transition_timeline={
            "bar_1": "Start Track B intro",
            "bar_17": "Begin opening highs",
            "bar_33": "Swap bass lines",
            "bar_49": "Track A begins fade out",
            "bar_57": "Close filter on Track A",
            "bar_64": "Track B fully active",
        },
    )


# ===================================================================
# build_llm_payload
# ===================================================================


def test_build_llm_payload_includes_mix_scoring() -> None:
    from app.services.mix_scoring_service import MixScore

    mix_score = MixScore(
        dj_score=85, mix_difficulty="Very Easy", recommended_transition_length="64 bars"
    )
    payload = build_llm_payload(_build_response(), mix_score=mix_score)
    assert payload["mix_scoring"]["dj_score"] == 85
    assert payload["mix_scoring"]["mix_difficulty"] == "Very Easy"
    assert payload["mix_scoring"]["recommended_transition_length"] == "64 bars"


def test_build_llm_payload_includes_analysis_id() -> None:
    payload = build_llm_payload(_build_response())
    assert payload["analysis_id"] == "test-session"


def test_build_llm_payload_omits_status_and_message() -> None:
    payload = build_llm_payload(_build_response())
    assert "status" not in payload
    assert "message" not in payload


def test_build_llm_payload_includes_track_a_fields() -> None:
    payload = build_llm_payload(_build_response())
    track_a = payload["track_a"]
    assert track_a["filename"] == "Track A"
    assert track_a["bpm"] == 128.0
    assert track_a["energy"] == 0.18
    assert "duration" not in track_a
    assert "sample_rate" not in track_a


def test_build_llm_payload_includes_track_b_fields() -> None:
    payload = build_llm_payload(_build_response())
    track_b = payload["track_b"]
    assert track_b["filename"] == "Track B"
    assert track_b["bpm"] == 127.5
    assert track_b["energy"] == 0.17
    assert "duration" not in track_b
    assert "sample_rate" not in track_b


def test_build_llm_payload_includes_nested_compatibility() -> None:
    payload = build_llm_payload(_build_response())
    compat = payload["compatibility"]
    assert compat["compatibility_score"] == 94.0
    assert compat["tempo_difference"] == 0.5
    assert compat["energy_difference"] == 0.01
    assert "tempo_match" not in compat
    assert "energy_match" not in compat
    assert compat["overall_rating"] == "Excellent"


# ===================================================================
# recommend — valid response
# ===================================================================


class TestValidResponse:
    def test_parses_valid_json_response(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        expected = _expected_valid()
        assert response.model_dump(exclude={"ai_latency"}) == expected.model_dump(
            exclude={"ai_latency"}
        )

    def test_handles_json_with_code_fences(self) -> None:
        raw = "```json\n" + VALID_LLM_JSON + "\n```"
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96

    def test_handles_json_in_fences_without_language(self) -> None:
        raw = "```\n" + VALID_LLM_JSON + "\n```"
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96

    def test_handles_extra_text_before_json(self) -> None:
        raw = "Here is the analysis:\n\n" + VALID_LLM_JSON
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96

    def test_handles_extra_text_after_json(self) -> None:
        raw = VALID_LLM_JSON + "\n\nThis is a great mix!"
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96

    def test_handles_trailing_comma(self) -> None:
        raw = VALID_LLM_JSON[:-1] + ",}"
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96

    def test_handles_two_jsons(self) -> None:
        raw = VALID_LLM_JSON + '{"second":"object"}'
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 96
        assert "Technically strong" in response.summary

    def test_successful_response_sets_provider_fields(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.ai_provider == "openrouter"
        assert response.ai_model == settings.OPENROUTER_MODEL
        assert response.ai_latency is not None
        assert response.ai_latency >= 0

    def test_fallback_response_has_null_provider_fields(self) -> None:
        agent = DJAgent(client=FakeLLMClient("bad data"))
        response = agent.recommend(_build_response())
        assert response.ai_provider is None
        assert response.ai_model is None
        assert response.ai_latency is None


# ===================================================================
# normalisation (previously fallback scenarios)
# ===================================================================


class TestNormalisation:
    def test_normalises_minimal_json(self) -> None:
        raw = (
            '{"summary":"Mix","confidence":50,'
            '"mix_direction":"Blend","club_tip":"","professional_notes":""}'
        )
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 50
        assert response.risk_level == "Low"  # from rule engine
        assert (
            "Excellent" in response.compatibility_analysis.interpretation
        )  # from rule engine


# ===================================================================
# fallback scenarios
# ===================================================================


class TestFallback:
    def test_fallback_for_invalid_json(self) -> None:
        agent = DJAgent(client=FakeLLMClient("not valid json"))
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert response.risk_level == "Low"  # from rule engine
        assert "unavailable" in response.summary.lower()

    def test_fallback_for_empty_response(self) -> None:
        agent = DJAgent(client=FakeLLMClient(""))
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert "unavailable" in response.summary.lower()

    def test_fallback_for_blank_response(self) -> None:
        agent = DJAgent(client=FakeLLMClient("   \n  "))
        response = agent.recommend(_build_response())
        assert response.confidence == 0

    def test_fallback_for_timeout(self) -> None:
        agent = DJAgent(client=RaisingLLMClient(TimeoutError("LLM provider timed out")))
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert "unavailable" in response.summary.lower()

    def test_fallback_for_http_error(self) -> None:
        agent = DJAgent(
            client=RaisingLLMClient(RuntimeError("HTTP 429: Too Many Requests"))
        )
        response = agent.recommend(_build_response())
        assert response.confidence == 0

    def test_fallback_response_has_zero_confidence(self) -> None:
        agent = DJAgent(client=FakeLLMClient(""))
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert response.risk_level == "Low"  # from rule engine


# ===================================================================
# retry logic
# ===================================================================


class TestRetry:
    def test_retry_succeeds_after_one_failure(self) -> None:
        client = RetryThenSucceedClient(VALID_LLM_JSON, fail_count=1)
        agent = DJAgent(client=client)
        response = agent.recommend(_build_response())
        assert response.confidence == 96
        assert client.call_count == 2

    def test_retry_exhausted_returns_fallback(self) -> None:
        agent = DJAgent(client=RaisingLLMClient(RuntimeError("always fails")))
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert "unavailable" in response.summary.lower()


# ===================================================================
# json_repair — integration through recommend()
# ===================================================================


class TestJSONRepairIntegration:
    def test_repairs_truncated_json(self) -> None:
        truncated = (
            '{"summary":"Repaired","confidence":50,"mix_direction":"x","club_tip":"a"'
        )
        agent = DJAgent(client=FakeLLMClient(truncated))
        response = agent.recommend(_build_response())
        assert response.confidence == 50
        assert response.summary == "Repaired"

    def test_repairs_single_quotes(self) -> None:
        raw = (
            "{'summary':'Single quoted test','confidence':50,"
            "'mix_direction':'test','club_tip':'a','professional_notes':'a'}"
        )
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert response.confidence == 50


# ===================================================================
# Backend-computed fields (M3, M4, M6)
# ===================================================================


class TestBackendComputedFields:
    def test_dj_score_is_set(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.dj_score == 85

    def test_mix_difficulty_is_set(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.mix_difficulty == "Very Easy"

    def test_transition_length_is_set(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.recommended_transition_length == "64 bars"

    def test_fallback_has_backend_fields(self) -> None:
        agent = DJAgent(client=FakeLLMClient("bad data"))
        response = agent.recommend(_build_response())
        assert response.dj_score == 85
        assert response.mix_difficulty == "Very Easy"
        assert response.recommended_transition_length == "64 bars"

    def test_ai_retry_count_zero_on_success(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.ai_retry_count == 0

    def test_ai_fallback_occurred_false_on_success(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.ai_fallback_occurred is False

    def test_ai_fallback_occurred_true_on_failure(self) -> None:
        agent = DJAgent(client=RaisingLLMClient(RuntimeError("fail")))
        response = agent.recommend(_build_response())
        assert response.ai_fallback_occurred is True

    def test_fallback_risk_level_from_rule_engine(self) -> None:
        agent = DJAgent(client=FakeLLMClient("bad data"))
        response = agent.recommend(_build_response())
        assert response.risk_level == "Low"  # rule engine with high compat score


# ===================================================================
# New schema fields — defaults (M5, M7, M8)
# ===================================================================


class TestRuleEngineFields:
    def test_alternative_strategy_from_rule_engine(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert "loop bridge" in response.alternative_strategy

    def test_why_this_strategy_from_rule_engine(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert "BPM difference" in response.why_this_strategy

    def test_transition_timeline_from_rule_engine(self) -> None:
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        response = agent.recommend(_build_response())
        assert response.transition_timeline["bar_1"] == "Start Track B intro"
        assert len(response.transition_timeline) == 6

    def test_fallback_has_rule_engine_fields(self) -> None:
        agent = DJAgent(client=FakeLLMClient("bad data"))
        response = agent.recommend(_build_response())
        assert "loop bridge" in response.alternative_strategy
        assert "BPM difference" in response.why_this_strategy
        assert response.transition_timeline["bar_33"] == "Swap bass lines"

    def test_backend_fields_from_rule_engine(self) -> None:
        """Alternative strategy, why_this_strategy, timeline come from rule engine."""
        raw = (
            "{"
            '"summary":"Great mix with alternative.",'
            '"mix_direction":"Blend",'
            '"club_tip":"a",'
            '"professional_notes":"a",'
            '"confidence":90'
            "}"
        )
        agent = DJAgent(client=FakeLLMClient(raw))
        response = agent.recommend(_build_response())
        assert "loop bridge" in response.alternative_strategy
        assert "BPM difference" in response.why_this_strategy
        assert response.transition_timeline["bar_1"] == "Start Track B intro"


# ===================================================================
# Retry behavior — new retry logic (M2)
# ===================================================================


class TestNewRetryBehavior:
    def test_retryable_http_500_is_retried(self) -> None:
        """HTTP 500 should be retried (is_retryable returns True)."""
        client = RetryThenSucceedClient(VALID_LLM_JSON, fail_count=1)
        agent = DJAgent(client=client)
        response = agent.recommend(_build_response())
        assert response.confidence == 96
        assert client.call_count == 2

    def test_non_retryable_http_400_is_not_retried(self) -> None:
        """HTTP 400 should NOT be retried — moves to fallback immediately."""
        client = RaisingLLMClient(LLMHTTPError(400, "Bad request"))
        agent = DJAgent(client=client)
        response = agent.recommend(_build_response())
        assert response.confidence == 0
        assert response.ai_fallback_occurred is True

    def test_timeout_is_retried(self) -> None:
        """LLMTimeoutError should be retried."""
        from app.ai.exceptions import LLMTimeoutError

        results = [LLMTimeoutError("t1"), VALID_LLM_JSON]

        class SeqClient:
            def __init__(self):
                self.call_count = 0

            def complete_chat(self, messages, **kw):
                val = results[self.call_count]
                self.call_count += 1
                if isinstance(val, Exception):
                    raise val
                return val

        agent = DJAgent(client=SeqClient())
        response = agent.recommend(_build_response())
        assert response.confidence == 96
        assert agent._llm_manager._injected_client.call_count == 2


# ===================================================================
# LLM summary logging (M4)
# ===================================================================


class TestLLMLogging:
    def test_log_summary_contains_required_fields(self, caplog) -> None:
        import logging

        caplog.set_level(logging.INFO)
        agent = DJAgent(client=FakeLLMClient(VALID_LLM_JSON))
        agent.recommend(_build_response())
        combined = "\n".join(caplog.messages)
        assert "LLM SUMMARY" in combined
        assert "analysis id:" in combined
        assert "selected model:" in combined
        assert "elapsed:" in combined
        assert "fallback used:" in combined
        assert "retry count:" in combined
        assert "response size:" in combined
        assert "validation:" in combined

    def test_log_summary_on_fallback(self, caplog) -> None:
        import logging

        caplog.set_level(logging.INFO)
        agent = DJAgent(client=FakeLLMClient("bad data"))
        agent.recommend(_build_response())
        combined = "\n".join(caplog.messages)
        assert "LLM SUMMARY" in combined
        assert "fallback used: Yes" in combined


# ===================================================================
# Config settings (M12)
# ===================================================================


class TestConfigSettings:
    def test_llm_timeout_default_is_30(self) -> None:
        assert settings.LLM_TIMEOUT == 30

    def test_llm_max_retries_default_is_2(self) -> None:
        assert settings.LLM_MAX_RETRIES == 2

    def test_llm_backoff_default_is_1(self) -> None:
        assert settings.LLM_RETRY_BACKOFF_BASE == 1.0

    def test_llm_max_tokens_default_is_1500(self) -> None:
        assert settings.LLM_MAX_TOKENS == 1500

    def test_llm_temperature_default_is_0(self) -> None:
        assert settings.LLM_TEMPERATURE == 0.0

    def test_llm_log_raw_default_is_false(self) -> None:
        assert settings.LLM_LOG_RAW_RESPONSES is False

    def test_fallback_models_are_configured(self) -> None:
        assert len(settings.OPENROUTER_MODELS) >= 3

    def test_llm_manager_accepts_custom_timeout(self) -> None:
        manager = LLMManager(
            models=["test"],
            base_url="http://fake.local",
            api_key="test-key",
            timeout=15,
        )
        assert manager._timeout == 15

    def test_llm_manager_accepts_custom_max_retries(self) -> None:
        manager = LLMManager(
            models=["test"],
            base_url="http://fake.local",
            api_key="test-key",
            max_retries=3,
        )
        assert manager._max_retries == 3


# ===================================================================
# LLMManager — all models fail
# ===================================================================


class TestLLMManagerDirect:
    def test_all_models_fail_raises_exception(self) -> None:
        manager = LLMManager(
            models=["model-a", "model-b"],
            base_url="http://fake.local",
            api_key="test-key",
        )
        messages = [{"role": "user", "content": "test"}]
        try:
            manager.generate(messages)
        except LLMAllModelsFailed:
            pass
        else:
            raise AssertionError("Expected LLMAllModelsFailed")

    def test_injected_client_skips_fallback(self) -> None:
        client = FakeLLMClient(
            '{"summary":"ok","mix_direction":"x","club_tip":"a","professional_notes":"a","confidence":10}'
        )
        manager = LLMManager(
            models=["primary", "fallback-a", "fallback-b"],
            base_url="http://fake.local",
            api_key="test-key",
            client=client,
        )
        messages = [{"role": "user", "content": "test"}]
        parsed, model, attempts = manager.generate(messages)
        assert model == "primary"
        assert parsed["summary"] == "ok"
