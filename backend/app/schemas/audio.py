from pydantic import BaseModel, Field


class AudioAnalysis(BaseModel):
    """Audio metrics extracted from a track."""

    filename: str = Field(description="Original filename of the uploaded track.")
    duration: float = Field(description="Track duration in seconds.")
    sample_rate: int = Field(description="Audio sample rate in Hertz.")
    bpm: float = Field(description="Estimated tempo in beats per minute.")
    energy: float = Field(description="Average RMS energy of the track.")
