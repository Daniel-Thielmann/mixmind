from pydantic import BaseModel


class Recommendation(BaseModel):
    """Recommendation data for mixing two tracks."""

    compatibility_score: float
    recommended_mix_point: float
    crossfade_duration: float
