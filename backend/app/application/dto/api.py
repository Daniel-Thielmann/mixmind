from app.domain.entities.recommendation import AIRecommendationResponse
from app.domain.entities.track import AudioAnalysis
from app.domain.value_objects.compatibility import CompatibilityResult
from app.domain.value_objects.visualization import Spectrograms, Waveforms
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """Generic API response envelope."""

    status: str
    message: str


class UploadAnalysisResponse(ApiResponse):
    """Response returned after analyzing the uploaded tracks."""

    analysis_id: str = Field(description="Unique identifier for this analysis session.")

    track_a: AudioAnalysis = Field(description="Analysis results for track A.")

    track_b: AudioAnalysis = Field(description="Analysis results for track B.")

    compatibility: CompatibilityResult = Field(
        description="Heuristic compatibility result for the track pair."
    )

    ai_recommendation: AIRecommendationResponse = Field(
        description="Structured DJ assistant recommendation for the track pair."
    )

    waveforms: Waveforms = Field(description="Generated waveform images.")

    spectrograms: Spectrograms = Field(description="Generated spectrogram images.")


class AnalysisMetadata(BaseModel):
    """Persistent metadata written to analysis.json inside the session folder."""

    analysis_id: str
    track_a: AudioAnalysis
    track_b: AudioAnalysis
    compatibility: CompatibilityResult
    ai_recommendation: AIRecommendationResponse
    waveforms: Waveforms
    spectrograms: Spectrograms
