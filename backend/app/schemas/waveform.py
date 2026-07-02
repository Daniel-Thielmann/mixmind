from pydantic import BaseModel, Field


class WaveformResult(BaseModel):
    """Metadata for a generated waveform image."""

    image_path: str = Field(description="Relative path to the generated PNG.")
    width: int = Field(description="Image width in pixels.")
    height: int = Field(description="Image height in pixels.")


class Waveforms(BaseModel):
    """Waveform images generated for the uploaded tracks."""

    track_a: WaveformResult = Field(description="Waveform for track A.")
    track_b: WaveformResult = Field(description="Waveform for track B.")
