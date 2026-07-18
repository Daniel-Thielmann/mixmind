from pydantic import BaseModel, ConfigDict, Field


class TempoAnalysis(BaseModel):
    difference: str = Field(description="Interpretation of the tempo gap.")
    recommendation: str = Field(description="Recommended tempo adjustment strategy.")


class EnergyAnalysis(BaseModel):
    difference: str = Field(description="Interpretation of the energy delta.")
    recommendation: str = Field(description="Recommended energy management strategy.")


class CompatibilityAnalysis(BaseModel):
    score: str = Field(description="Human-readable reading of the numeric score.")
    interpretation: str = Field(
        default="Interpretation unavailable.",
        description="Practical meaning of the compatibility score.",
    )


class MixStrategy(BaseModel):
    before_transition: str = Field(
        description="Preparation steps before the transition."
    )
    during_transition: str = Field(
        description="Actions to execute during the transition."
    )
    after_transition: str = Field(
        description="Follow-up steps after the transition lands."
    )


class DJExecution(BaseModel):
    loop: str = Field(description="Looping recommendation (bars / position).")
    eq: str = Field(description="EQ settings or filter guidance.")
    filter: str = Field(description="Filter-sweep recommendation.")
    tempo_fader: str = Field(
        default="No recommendation.",
        description="Tempo-fader / pitch adjustment.",
    )
    phrase_matching: str = Field(
        default="No recommendation.",
        description="Phrase-matching advice (entry bar / exit bar).",
    )
    cue_point: str = Field(
        default="No recommendation.",
        description="Suggested cue-point position for Track B.",
    )


class AIRecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ai_provider: str | None = Field(
        default=None, description="LLM provider name (e.g. openrouter)."
    )
    ai_model: str | None = Field(
        default=None, description="Model identifier used for this response."
    )
    ai_latency: float | None = Field(
        default=None, description="Total request latency in seconds."
    )

    summary: str = Field(description="One-sentence verdict for the track pair.")
    mix_direction: str = Field(
        description="High-level direction (blend, cut, bridge, etc.)."
    )
    transition_quality: str = Field(
        description="Expected transition quality (Low / Medium / High)."
    )
    transition_type: str = Field(description="Specific transition technique.")
    confidence: int = Field(ge=0, le=100, description="Confidence score from 0 to 100.")
    tempo_analysis: TempoAnalysis = Field(description="BPM-based analysis.")
    energy_analysis: EnergyAnalysis = Field(description="RMS-energy comparison.")
    compatibility_analysis: CompatibilityAnalysis = Field(
        description="Compatibility score interpretation."
    )
    mix_strategy: MixStrategy = Field(description="Three-phase mix strategy.")
    dj_execution: DJExecution = Field(description="Specific DJ techniques to apply.")
    club_tip: str = Field(default="", description="Practical club or performance tip.")
    professional_notes: str = Field(
        default="", description="Additional professional observations."
    )
    risks: list[str] = Field(
        default_factory=list, description="Potential risks or failure modes."
    )
    best_use_case: str = Field(
        default="", description="Ideal set context for this track pair."
    )
    risk_level: str = Field(
        default="Medium", description="Overall risk level (Low / Medium / High)."
    )

    mix_difficulty: str = Field(
        default="Medium",
        description="Calculated mix difficulty (Very Easy / Easy / Medium / Hard / Expert).",
    )
    recommended_transition_length: str = Field(
        default="16 bars",
        description="Recommended transition length (8 bars / 16 bars / 32 bars / 64 bars).",
    )
    alternative_strategy: str = Field(
        default="",
        description="Alternative mixing strategy if the primary is not ideal.",
    )
    dj_score: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Backend-calculated DJ mix score from 0 to 100.",
    )
    why_this_strategy: str = Field(
        default="",
        description="One-sentence explanation of why this strategy was chosen.",
    )
    transition_timeline: dict[str, str] = Field(
        default_factory=dict,
        description="Bar-by-bar timeline of the transition (e.g. bar_1, bar_9).",
    )

    ai_retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of LLM retry attempts before success or fallback.",
    )
    ai_fallback_occurred: bool = Field(
        default=False, description="Whether a fallback response was used."
    )
