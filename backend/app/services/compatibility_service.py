from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult


class CompatibilityService:
    """Calculate heuristic compatibility between two analyzed tracks."""

    def compare(
        self,
        track_a: AudioAnalysis,
        track_b: AudioAnalysis,
    ) -> CompatibilityResult:
        """Compare tempo and energy and return a normalized result."""

        tempo_difference = abs(track_a.bpm - track_b.bpm)
        energy_difference = abs(track_a.energy - track_b.energy)

        tempo_factor = self._tempo_factor(tempo_difference)
        energy_factor = self._energy_factor(energy_difference)

        compatibility_score = round(
            (tempo_factor * 60.0) + (energy_factor * 40.0),
            1,
        )

        return CompatibilityResult(
            compatibility_score=compatibility_score,
            tempo_difference=round(tempo_difference, 2),
            energy_difference=round(energy_difference, 4),
            tempo_match=self._tempo_match(tempo_difference),
            energy_match=self._energy_match(energy_difference),
            overall_rating=self._overall_rating(compatibility_score),
        )

    def _tempo_factor(self, tempo_difference: float) -> float:
        if tempo_difference <= 2.0:
            return 1.0

        if tempo_difference <= 5.0:
            return 0.75

        return 0.35

    def _energy_factor(self, energy_difference: float) -> float:
        return max(0.0, 1.0 - energy_difference)

    def _tempo_match(self, tempo_difference: float) -> str:
        if tempo_difference <= 2.0:
            return "Excellent"

        if tempo_difference <= 5.0:
            return "Very Good"

        if tempo_difference <= 8.0:
            return "Good"

        if tempo_difference <= 12.0:
            return "Fair"

        return "Poor"

    def _energy_match(self, energy_difference: float) -> str:
        if energy_difference <= 0.02:
            return "Excellent"

        if energy_difference <= 0.05:
            return "Very Good"

        if energy_difference <= 0.10:
            return "Good"

        if energy_difference <= 0.20:
            return "Fair"

        return "Poor"

    def _overall_rating(self, compatibility_score: float) -> str:
        if compatibility_score >= 95.0:
            return "Excellent"

        if compatibility_score >= 80.0:
            return "Very Good"

        if compatibility_score >= 60.0:
            return "Good"

        if compatibility_score >= 40.0:
            return "Fair"

        return "Poor"


compatibility_service = CompatibilityService()
