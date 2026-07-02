from pydantic import BaseModel, Field


class SpectrogramResult(BaseModel):
    """Metadata for a generated spectrogram image."""

    image_path: str = Field(description="Relative path to the generated PNG.")
    width: int = Field(description="Image width in pixels.")
    height: int = Field(description="Image height in pixels.")


class Spectrograms(BaseModel):
    """Spectrogram images generated for the uploaded tracks."""

    track_a: SpectrogramResult = Field(description="Spectrogram for track A.")
    track_b: SpectrogramResult = Field(description="Spectrogram for track B.")
