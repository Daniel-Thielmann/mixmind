from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.schemas.spectrogram import Spectrograms
from app.schemas.waveform import Waveforms
from pydantic import BaseModel, Field


class ApiResponse(BaseModel):
    """Generic API response envelope."""

    status: str
    message: str


class UploadAnalysisResponse(ApiResponse):
    """Response returned after analyzing the uploaded tracks."""

    track_a: AudioAnalysis = Field(description="Analysis results for track A.")

    track_b: AudioAnalysis = Field(description="Analysis results for track B.")

    compatibility: CompatibilityResult = Field(
        description="Heuristic compatibility result for the track pair."
    )

    waveforms: Waveforms = Field(description="Generated waveform images.")

    spectrograms: Spectrograms = Field(description="Generated spectrogram images.")
