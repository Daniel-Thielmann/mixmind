from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.track import Track


class CreateTrackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: str = Field(min_length=1, max_length=255)
    duration: float | None = Field(default=None, gt=0)
    bpm: float | None = Field(default=None, ge=20, le=300)
    energy: float | None = Field(default=None, ge=0, le=1)
    key: str = Field(default="Unknown", max_length=50)
    camelot: str | None = Field(default=None, pattern=r"^(?:[1-9]|1[0-2])[AB]$")
    sample_rate: int = Field(default=0, ge=0)


class UpdateTrackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    filename: str | None = Field(default=None, min_length=1, max_length=255)
    duration: float | None = Field(default=None, gt=0)
    bpm: float | None = Field(default=None, ge=20, le=300)
    energy: float | None = Field(default=None, ge=0, le=1)
    key: str | None = Field(default=None, max_length=50)
    camelot: str | None = Field(default=None, pattern=r"^(?:[1-9]|1[0-2])[AB]$")
    sample_rate: int | None = Field(default=None, ge=0)


class TrackResponse(BaseModel):
    id: str
    filename: str
    duration: float | None
    bpm: float | None
    energy: float | None
    key: str
    camelot: str | None
    sample_rate: int

    @classmethod
    def from_entity(cls, track: Track) -> TrackResponse:
        return cls(
            id=track.track_id.value,
            filename=track.filename,
            duration=track.duration.value if track.duration else None,
            bpm=track.bpm.value if track.bpm else None,
            energy=track.energy.value if track.energy else None,
            key=track.key,
            camelot=track.camelot.value if track.camelot else None,
            sample_rate=track.sample_rate,
        )
