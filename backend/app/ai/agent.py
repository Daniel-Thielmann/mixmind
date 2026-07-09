"""DJ agent orchestration — LLM now produces only subjective text fields."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.ai.cache import RecommendationCache, recommendation_cache
from app.ai.client import LLMClient
from app.ai.exceptions import LLMAllModelsFailed
from app.ai.llm_manager import LLMManager
from app.ai.metrics import LLMMetricsCollector, llm_metrics
from app.ai.mix_rule_engine import MixRuleEngine, mix_rule_engine
from app.ai.prompts import build_dj_messages, build_llm_payload
from app.ai.recommendation_assembler import (
    RecommendationAssembler,
    recommendation_assembler,
)
from app.ai.text_schemas import AITextRecommendation
from app.core.config import settings
from app.schemas.api import UploadAnalysisResponse
from app.services.mix_scoring_service import (
    MixScore,
    MixScoringService,
    mix_scoring_service,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class DJAgent:
    def __init__(
        self,
        client: LLMClient | None = None,
        llm_manager: LLMManager | None = None,
        mix_scorer: MixScoringService | None = None,
        rule_engine: MixRuleEngine | None = None,
        assembler: RecommendationAssembler | None = None,
        cache: RecommendationCache | None = None,
        metrics_collector: LLMMetricsCollector | None = None,
    ) -> None:
        self._cache = cache or recommendation_cache
        self._metrics_collector = metrics_collector or llm_metrics
        self._rule_engine = rule_engine or mix_rule_engine
        self._assembler = assembler or recommendation_assembler
        self._llm_manager = llm_manager or LLMManager(
            models=[settings.OPENROUTER_MODEL, *settings.OPENROUTER_MODELS],
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
            client=client,
            timeout=settings.LLM_TIMEOUT,
            max_retries=settings.LLM_MAX_RETRIES,
            backoff_base=settings.LLM_RETRY_BACKOFF_BASE,
        )
        self._mix_scorer = mix_scorer or mix_scoring_service

    def _get_cache_key_data(
        self, response: UploadAnalysisResponse
    ) -> tuple[Any, Any, Any]:
        track_a_data = (
            response.track_a.model_dump()
            if hasattr(response.track_a, "model_dump")
            else {}
        )
        track_b_data = (
            response.track_b.model_dump()
            if hasattr(response.track_b, "model_dump")
            else {}
        )
        compat_data = (
            response.compatibility.model_dump()
            if hasattr(response.compatibility, "model_dump")
            else {}
        )
        return (track_a_data, track_b_data, compat_data)

    def recommend(self, response: UploadAnalysisResponse) -> Any:
        self._metrics_collector.record_request()

        mix_score = self._mix_scorer.compute(
            compatibility_score=response.compatibility.compatibility_score,
            tempo_difference=response.compatibility.tempo_difference,
            energy_difference=response.compatibility.energy_difference,
        )

        rule_output = self._rule_engine.build(response, mix_score)

        cache_key_data = self._get_cache_key_data(response)
        cached = self._cache.get(*cache_key_data)

        if cached is not None:
            self._metrics_collector.record_cache_hit()
            llm_text = cached
            model = llm_text.pop("_cached_model", "")
            elapsed = 0.0
            attempts = 0
            fallback_occurred = False
        else:
            self._metrics_collector.record_cache_miss()

            payload = self._build_payload(response, mix_score)
            messages = build_dj_messages(payload)

            start = time.monotonic()

            try:
                parsed, model, attempts = self._llm_manager.generate(
                    messages,
                    temperature=0.0,
                    max_tokens=500,
                    validator=self._validate_text_dict,
                )
                llm_text = parsed
                elapsed = time.monotonic() - start
                fallback_occurred = False
            except LLMAllModelsFailed:
                llm_text = self._fallback_text_dict()
                model = ""
                attempts = 0
                elapsed = time.monotonic() - start
                fallback_occurred = True

            llm_text["_cached_model"] = model
            self._cache.set(*cache_key_data, llm_text)
            llm_text.pop("_cached_model", None)

        assembled = self._assembler.assemble(
            rule_output=rule_output,
            llm_text=llm_text,
            mix_score=mix_score,
            model=model,
            attempts=attempts,
            elapsed=elapsed,
            fallback_occurred=fallback_occurred,
        )

        score_explanation = self._mix_scorer.compute_explanation(mix_score)
        if assembled.professional_notes:
            assembled.professional_notes += "\n\n" + score_explanation
        else:
            assembled.professional_notes = score_explanation

        logger.info(
            "Recommendation assembled — model: %s | attempts: %d | latency: %.2fs"
            " | fallback: %s",
            model or "none",
            attempts,
            elapsed,
            "yes" if fallback_occurred else "no",
        )
        return assembled

    @staticmethod
    def _validate_text_dict(parsed: dict[str, Any]) -> bool:
        try:
            AITextRecommendation.model_validate(parsed)
            return True
        except (ValidationError, ValueError, TypeError):
            return False

    def _build_payload(
        self,
        response: UploadAnalysisResponse,
        mix_score: MixScore,
    ) -> dict[str, Any]:
        return build_llm_payload(response, mix_score)

    @staticmethod
    def _fallback_text_dict() -> dict[str, Any]:
        return {
            "summary": "AI recommendation unavailable.",
            "mix_direction": "Review the transition manually before mixing.",
            "club_tip": "Proceed with the existing compatibility score.",
            "professional_notes": (
                "The AI assistant could not produce a valid response."
            ),
            "confidence": 0,
        }


dj_agent = DJAgent()
