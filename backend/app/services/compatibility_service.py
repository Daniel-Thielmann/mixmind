from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult


class CompatibilityService:
    """Calculate heuristic compatibility between two analyzed tracks."""

    def compare(
        self,
        track_a: AudioAnalysis,
        track_b: AudioAnalysis,
    ) -> CompatibilityResult:
        """Compare tempo, energy, and harmonic key to return a normalized result."""

        tempo_difference = abs(track_a.bpm - track_b.bpm)
        energy_difference = abs(track_a.energy - track_b.energy)

        tempo_factor = self._tempo_factor(tempo_difference)
        energy_factor = self._energy_factor(energy_difference)
        
        # Extrai o fator harmônico usando os códigos Camelot
        harmonic_factor = self._harmonic_factor(track_a.camelot, track_b.camelot)

        # Nova distribuição de pesos!!!
        compatibility_score = round(
            (harmonic_factor * 40.0) + (tempo_factor * 40.0) + (energy_factor * 20.0),
            1,
        )

        return CompatibilityResult(
            compatibility_score=compatibility_score,
            tempo_difference=round(tempo_difference, 2),
            energy_difference=round(energy_difference, 4),
            tempo_match=self._tempo_match(tempo_difference),
            energy_match=self._energy_match(energy_difference),
            harmonic_match=self._harmonic_match_label(harmonic_factor),
            overall_rating=self._overall_rating(compatibility_score),
        )

    def _harmonic_factor(self, camelot_a: str, camelot_b: str) -> float:
        """Calcula o multiplicador harmônico baseado na Roda de Camelot."""
        if camelot_a == "Unknown" or camelot_b == "Unknown":
            return 0.5  # Neutro se o librosa não conseguir identificar

        if camelot_a == camelot_b:
            return 1.0  # Perfect Match

        # ("12A" -> num=12, letter="A")
        num_a, letter_a = int(camelot_a[:-1]), camelot_a[-1]
        num_b, letter_b = int(camelot_b[:-1]), camelot_b[-1]

        # Relative Match: Mesma tônica, muda a escala (ex: 1A -> 1B)
        if num_a == num_b and letter_a != letter_b:
            return 0.8

        # Adjacent Match: Mesma escala, sobe ou desce 1 passo (ex: 1A -> 2A ou 1A -> 12A)
        if letter_a == letter_b:
            diff = abs(num_a - num_b)
            if diff == 1 or diff == 11:  # 11 resolve a volta na roda de 12 para 1
                return 0.8

        # Energy Boost: Sobe 2 semitons (+2 na roda)
        diff = abs(num_a - num_b)
        if letter_a == letter_b and (diff == 2 or diff == 10):
            return 0.6

        # Harmonic Clash
        return 0.0

    def _harmonic_match_label(self, harmonic_factor: float) -> str:
        """Retorna a string legível para o resultado harmônico."""
        if harmonic_factor == 1.0:
            return "Perfect"
        if harmonic_factor == 0.8:
            return "Good (Relative/Adjacent)"
        if harmonic_factor == 0.6:
            return "Fair (Energy Boost)"
        if harmonic_factor == 0.5:
            return "Unknown"
        
        return "Clash"

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
        if compatibility_score >= 90.0:
            return "Excellent"

        if compatibility_score >= 75.0:
            return "Very Good"

        if compatibility_score >= 55.0:
            return "Good"

        if compatibility_score >= 40.0:
            return "Fair"

        return "Poor"


compatibility_service = CompatibilityService()