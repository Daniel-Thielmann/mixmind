from pydantic import BaseModel


class AudioAnalysis(BaseModel):
    """Audio metrics extracted from a track."""

    filename: str
    duration: float
    bpm: float
    energy: float
    sample_rate: intfrom pydantic import BaseModel


class AudioAnalysis(BaseModel):

    filename: str

    duration: float

    bpm: float

    energy: float

    sample_rate: int
