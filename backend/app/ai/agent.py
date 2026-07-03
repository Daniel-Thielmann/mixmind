"""DJ agent orchestration built on top of an OpenAI-compatible LLM client."""

from __future__ import annotations

import logging
import time
from typing import Any

from app.ai.client import LLMClient
from app.ai.exceptions import LLMAllModelsFailed
from app.ai.llm_manager import LLMManager
from app.ai.prompts import build_dj_messages, build_llm_payload
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
from app.services.mix_scoring_service import (
    MixScore,
    MixScoringService,
    mix_scoring_service,
)
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class DJAgent:
    """Generates structured DJ recommendations from backend audio features.

    Builds the LLM payload, delegates to ``LLMManager`` for model fallback,
    retry, JSON repair, normalisation, and validation — then returns the
    validated response or a safe fallback.
    """

    def __init__(
        self,
        client: LLMClient | None = None,
        llm_manager: LLMManager | None = None,
        mix_scorer: MixScoringService | None = None,
    ) -> None:
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(self, response: UploadAnalysisResponse) -> AIRecommendationResponse:
        """Return a validated recommendation or a safe fallback response."""
        # Compute backend source-of-truth fields.
        mix_score = self._mix_scorer.compute(
            compatibility_score=response.compatibility.compatibility_score,
            tempo_difference=response.compatibility.tempo_difference,
            energy_difference=response.compatibility.energy_difference,
        )

        payload = self._build_payload(response, mix_score)
        messages = build_dj_messages(payload)

        start = time.monotonic()

        try:
            parsed, model, attempts = self._llm_manager.generate(
                messages,
                temperature=0.0,
                max_tokens=1500,
                validator=self._validate_dict,
            )
        except LLMAllModelsFailed:
            logger.warning(
                "LLM request failed after %.2fs — all models exhausted",
                time.monotonic() - start,
            )
            return self._apply_backend_fields(
                self._fallback_response(),
                mix_score,
                retry_count=0,
                fallback_occurred=True,
            )

        elapsed = time.monotonic() - start

        # Re-validate now that we know it passes — also gets the model instance.
        try:
            validated = AIRecommendationResponse.model_validate(parsed)
        except (ValidationError, ValueError, TypeError) as exc:
            logger.warning(
                "LLM response validation failed after %.2fs — %s: %s",
                elapsed,
                type(exc).__name__,
                exc,
            )
            return self._apply_backend_fields(
                self._fallback_response(),
                mix_score,
                retry_count=attempts,
                fallback_occurred=True,
            )

        validated.ai_provider = "openrouter"
        validated.ai_model = model
        validated.ai_latency = round(elapsed, 3)
        validated.ai_retry_count = attempts - 1
        validated.ai_fallback_occurred = False

        validated = self._apply_backend_fields(validated, mix_score)

        # Inject DJ score explanation into professional_notes (M10).
        score_explanation = self._mix_scorer.compute_explanation(mix_score)
        if validated.professional_notes:
            validated.professional_notes += "\n\n" + score_explanation
        else:
            validated.professional_notes = score_explanation

        logger.info(
            "LLM success — model: %s | attempts: %d | latency: %.2fs",
            model,
            attempts,
            elapsed,
        )
        return validated

    @staticmethod
    def _apply_backend_fields(
        rec: AIRecommendationResponse,
        mix_score: MixScore,
        retry_count: int = 0,
        fallback_occurred: bool = False,
    ) -> AIRecommendationResponse:
        """Apply backend-computed source-of-truth fields (M3, M4, M6)."""
        rec.dj_score = mix_score.dj_score
        rec.mix_difficulty = mix_score.mix_difficulty
        rec.recommended_transition_length = mix_score.recommended_transition_length
        rec.ai_retry_count = retry_count
        rec.ai_fallback_occurred = fallback_occurred
        return rec

    # ------------------------------------------------------------------
    # Validator callback (used by LLMManager)
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_dict(parsed: dict[str, Any]) -> bool:
        """Return ``True`` if *parsed* passes the Pydantic schema.

        Used as the ``validator`` callback inside ``LLMManager.generate()``
        so that validation failures trigger a retry with the next model.
        """
        try:
            AIRecommendationResponse.model_validate(parsed)
            return True
        except (ValidationError, ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Payload building
    # ------------------------------------------------------------------

    def _build_payload(
        self,
        response: UploadAnalysisResponse,
        mix_score: MixScore,
    ) -> dict[str, Any]:
        """Build the structured payload to send to the LLM."""
        return build_llm_payload(response, mix_score)

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _fallback_response(self) -> AIRecommendationResponse:
        """Return a safe recommendation when the model output cannot be trusted."""

        return AIRecommendationResponse(
            summary="AI recommendation unavailable.",
            mix_direction="Review the transition manually before mixing.",
            transition_quality="Unavailable",
            transition_type="Fallback review",
            confidence=0,
            tempo_analysis=TempoAnalysis(
                difference=(
                    "The backend analysis completed, but "
                    "the AI could not interpret the data."
                ),
                recommendation=(
                    "Use manual beatmatching and your ear "
                    "to evaluate the tempo relationship."
                ),
            ),
            energy_analysis=EnergyAnalysis(
                difference=(
                    "The backend analysis completed, but "
                    "the AI could not interpret the data."
                ),
                recommendation=(
                    "Rely on the backend energy metrics and your own judgment."
                ),
            ),
            compatibility_analysis=CompatibilityAnalysis(
                score=(
                    "The backend computed a score, but the AI could not interpret it."
                ),
                interpretation=(
                    "Use the backend compatibility score as your primary reference."
                ),
            ),
            mix_strategy=MixStrategy(
                before_transition=(
                    "Prepare cue points and listen to both tracks in headphones."
                ),
                during_transition=(
                    "Use a standard blend and adjust based on what you hear."
                ),
                after_transition=("Monitor the mix and adjust EQ as needed."),
            ),
            dj_execution=DJExecution(
                loop="Not available — set a loop manually if needed.",
                eq="Use standard EQ technique — reduce lows on the incoming track.",
                filter="Apply a high-pass filter on the outgoing track if desired.",
                tempo_fader="Adjust the tempo fader gradually while listening.",
                phrase_matching="Match phrases visually using the waveform.",
                cue_point="Set a cue point at the first beat of a phrase.",
            ),
            club_tip=(
                "Proceed with the existing compatibility score and "
                "verify the blend manually in your headphones."
            ),
            professional_notes=(
                "The AI assistant could not produce a valid response. "
                "All recommendations above are generic fallback guidance."
            ),
            risks=["AI analysis unavailable — proceed with manual mixing."],
            best_use_case="Use the backend compatibility metrics as your guide.",
            risk_level="High",
            mix_difficulty="Medium",
            recommended_transition_length="16 bars",
            alternative_strategy="",
            dj_score=50,
            why_this_strategy="",
            transition_timeline={},
        )


dj_agent = DJAgent()
