from pydantic import BaseModel, Field


class CompatibilityResult(BaseModel):
    """Heuristic compatibility summary for two analyzed tracks."""

    compatibility_score: float = Field(
        description="Overall compatibility score from 0 to 100."
    )
    tempo_difference: float = Field(
        description="Absolute BPM difference between the two tracks."
    )
    energy_difference: float = Field(
        description="Absolute RMS energy difference between the two tracks."
    )
    tempo_match: str = Field(description="Textual tempo similarity rating.")
    energy_match: str = Field(description="Textual energy similarity rating.")
    overall_rating: str = Field(description="Overall compatibility classification.")


Recommendation = CompatibilityResult
