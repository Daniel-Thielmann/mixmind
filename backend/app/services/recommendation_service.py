from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import Recommendation


class RecommendationService:
    """Generates mixing recommendations from two audio analyses."""

    def recommend(
        self,
        track_a: AudioAnalysis,
        track_b: AudioAnalysis,
    ) -> Recommendation:
        raise NotImplementedError
