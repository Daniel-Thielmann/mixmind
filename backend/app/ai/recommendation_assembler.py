"""Assembles the full AIRecommendationResponse from backend + LLM output."""

from __future__ import annotations

from typing import Any

from app.ai.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.services.mix_scoring_service import MixScore


def _ensure(d: dict[str, Any], key: str, default: dict[str, Any]) -> dict[str, Any]:
    """Return ``d[key]`` if it is a non-empty dict, else *default*."""
    val = d.get(key)
    return val if isinstance(val, dict) and val else default


class RecommendationAssembler:
    """Merges deterministic rule-engine output with LLM text into the final response.

    The final ``AIRecommendationResponse`` is contract-compatible with the frontend.
    The frontend cannot tell which fields came from the backend vs. the LLM.
    """

    def assemble(
        self,
        rule_output: dict[str, Any],
        llm_text: dict[str, Any],
        mix_score: MixScore,
        model: str = "",
        attempts: int = 0,
        elapsed: float = 0.0,
        fallback_occurred: bool = False,
    ) -> AIRecommendationResponse:
        return AIRecommendationResponse(
            ai_provider="openrouter" if not fallback_occurred else None,
            ai_model=model or None,
            ai_latency=round(elapsed, 3) if not fallback_occurred else None,
            ai_retry_count=max(0, attempts - 1),
            ai_fallback_occurred=fallback_occurred,
            summary=llm_text.get("summary", "AI recommendation unavailable."),
            mix_direction=llm_text.get(
                "mix_direction",
                "Review the transition manually before mixing.",
            ),
            transition_quality=rule_output.get("transition_quality", "Medium"),
            transition_type=rule_output.get("transition_type", "Standard blend"),
            confidence=llm_text.get("confidence", 50),
            tempo_analysis=TempoAnalysis(
                **_ensure(
                    rule_output,
                    "tempo_analysis",
                    {
                        "difference": "No tempo analysis available.",
                        "recommendation": "Match tempos manually.",
                    },
                )
            ),
            energy_analysis=EnergyAnalysis(
                **_ensure(
                    rule_output,
                    "energy_analysis",
                    {
                        "difference": "No energy analysis available.",
                        "recommendation": "Use your ears to match energy.",
                    },
                )
            ),
            compatibility_analysis=CompatibilityAnalysis(
                **_ensure(
                    rule_output,
                    "compatibility_analysis",
                    {
                        "score": "No score available.",
                        "interpretation": "Interpretation unavailable.",
                    },
                )
            ),
            mix_strategy=MixStrategy(
                **_ensure(
                    rule_output,
                    "mix_strategy",
                    {
                        "before_transition": "Prepare your cue points.",
                        "during_transition": "Use a standard blend.",
                        "after_transition": "Monitor the mix.",
                    },
                )
            ),
            dj_execution=DJExecution(**_ensure(rule_output, "dj_execution", {})),
            club_tip=llm_text.get("club_tip", ""),
            professional_notes=llm_text.get("professional_notes", ""),
            risks=rule_output.get("risks", []),
            best_use_case=rule_output.get("best_use_case", ""),
            risk_level=rule_output.get("risk_level", "Medium"),
            mix_difficulty=mix_score.mix_difficulty,
            recommended_transition_length=mix_score.recommended_transition_length,
            alternative_strategy=rule_output.get("alternative_strategy", ""),
            dj_score=mix_score.dj_score,
            why_this_strategy=rule_output.get("why_this_strategy", ""),
            transition_timeline=rule_output.get("transition_timeline", {}),
        )


recommendation_assembler = RecommendationAssembler()
