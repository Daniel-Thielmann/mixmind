from pydantic import BaseModel, Field


class WaveformResult(BaseModel):
    image_path: str = Field(description="Relative path to the generated PNG.")
    width: int = Field(description="Image width in pixels.")
    height: int = Field(description="Image height in pixels.")


class Waveforms(BaseModel):
    track_a: WaveformResult = Field(description="Waveform for track A.")
    track_b: WaveformResult = Field(description="Waveform for track B.")


class SpectrogramResult(BaseModel):
    image_path: str = Field(description="Relative path to the generated PNG.")
    width: int = Field(description="Image width in pixels.")
    height: int = Field(description="Image height in pixels.")


class Spectrograms(BaseModel):
    track_a: SpectrogramResult = Field(description="Spectrogram for track A.")
    track_b: SpectrogramResult = Field(description="Spectrogram for track B.")
