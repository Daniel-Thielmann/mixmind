"""Backend-computed DJ mix scoring — source of truth for M3, M4, M6."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MixScore:
    """Aggregated backend-computed scoring for a track pair."""

    dj_score: int
    mix_difficulty: str
    recommended_transition_length: str


class MixScoringService:
    """Compute mix difficulty, DJ score, and transition length from backend metrics.

    These values are the source of truth — the LLM receives them as context
    but must never contradict them.
    """

    def compute(
        self,
        compatibility_score: float,
        tempo_difference: float,
        energy_difference: float,
    ) -> MixScore:
        dj_score = self._compute_dj_score(compatibility_score)
        mix_difficulty = self._compute_mix_difficulty(
            tempo_difference, compatibility_score, energy_difference
        )
        transition_length = self._compute_transition_length(
            tempo_difference, energy_difference, compatibility_score
        )
        return MixScore(
            dj_score=dj_score,
            mix_difficulty=mix_difficulty,
            recommended_transition_length=transition_length,
        )

    # ------------------------------------------------------------------
    # DJ Score (0-100)
    # ------------------------------------------------------------------

    def compute_explanation(self, mix_score: MixScore) -> str:
        """Return a human-readable explanation of the DJ score (M10).

        Injected into ``professional_notes`` by the agent.
        """
        compat_part = "Compatibility Score is the primary factor."
        if mix_score.dj_score >= 95:
            compat_part = "Near-perfect backend compatibility."
        elif mix_score.dj_score >= 80:
            compat_part = "Strong backend compatibility across tempo and energy."
        elif mix_score.dj_score >= 60:
            compat_part = "Good backend compatibility with minor tempo or energy gaps."
        elif mix_score.dj_score >= 40:
            compat_part = (
                "Moderate compatibility — tempo or energy differences are noticeable."
            )
        else:
            compat_part = "Low compatibility — significant tempo or energy mismatch."

        diff_part = f"Mix difficulty is {mix_score.mix_difficulty.lower()}."
        if mix_score.mix_difficulty in ("Very Easy", "Easy"):
            diff_part += " Smooth transition expected."
        elif mix_score.mix_difficulty == "Expert":
            diff_part += " Requires careful manual control."

        return (
            f"DJ Score: {mix_score.dj_score}/100 — {compat_part} "
            f"{diff_part} "
            f"Recommended transition: {mix_score.recommended_transition_length}."
        )

    @staticmethod
    def _compute_dj_score(compatibility_score: float) -> int:
        """Map compatibility_score (0-100) to a DJ score (0-100).

        Uses the same thresholds as CompatibilityService._overall_rating
        for consistency.
        """
        if compatibility_score >= 95.0:
            return 98
        if compatibility_score >= 80.0:
            return 85
        if compatibility_score >= 60.0:
            return 70
        if compatibility_score >= 40.0:
            return 50
        return 30

    # ------------------------------------------------------------------
    # Mix Difficulty
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_mix_difficulty(
        tempo_difference: float,
        compatibility_score: float,
        energy_difference: float,
    ) -> str:
        """Determine mix difficulty from tempo, compatibility, and energy.

        Very Easy:  BPM diff <= 2 AND score >= 80 AND energy diff <= 0.05
        Easy:       BPM diff <= 5 AND score >= 60 AND energy diff <= 0.10
        Medium:     BPM diff <= 8 AND score >= 40 AND energy diff <= 0.20
        Hard:       BPM diff <= 12 OR score >= 20
        Expert:     Otherwise
        """
        if (
            tempo_difference <= 2.0
            and compatibility_score >= 80.0
            and energy_difference <= 0.05
        ):
            return "Very Easy"
        if (
            tempo_difference <= 5.0
            and compatibility_score >= 60.0
            and energy_difference <= 0.10
        ):
            return "Easy"
        if (
            tempo_difference <= 8.0
            and compatibility_score >= 40.0
            and energy_difference <= 0.20
        ):
            return "Medium"
        if tempo_difference <= 12.0 or compatibility_score >= 20.0:
            return "Hard"
        return "Expert"

    # ------------------------------------------------------------------
    # Transition Length
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_transition_length(
        tempo_difference: float,
        energy_difference: float,
        compatibility_score: float,
    ) -> str:
        """Pick a transition bar count aligned with the mix difficulty.

        64 bars:  Very Easy (long, smooth blend possible)
        32 bars:  Easy / Medium (moderate blend)
        16 bars:  Hard (shorter, more controlled)
        8 bars:   Expert (short, punchy)
        """
        difficulty = MixScoringService._compute_mix_difficulty(
            tempo_difference, compatibility_score, energy_difference
        )
        mapping = {
            "Very Easy": "64 bars",
            "Easy": "32 bars",
            "Medium": "32 bars",
            "Hard": "16 bars",
            "Expert": "8 bars",
        }
        return mapping.get(difficulty, "16 bars")


mix_scoring_service = MixScoringService()
