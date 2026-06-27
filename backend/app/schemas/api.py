from pydantic import BaseModel, Field

from app.schemas.audio import AudioAnalysis


class ApiResponse(BaseModel):
    """Generic API response envelope."""

    status: str
    message: str


class UploadAnalysisResponse(ApiResponse):
    """Response returned after analyzing the uploaded tracks."""

    track_a: AudioAnalysis = Field(description="Analysis results for track A.")
    track_b: AudioAnalysis = Field(description="Analysis results for track B.")
