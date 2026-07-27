from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

TrackPosition = Literal["track_a", "track_b"]


class SpotifyTrackRequest(BaseModel):
    position: TrackPosition
    spotify_track_id: str = Field(min_length=1, max_length=256)


class SpotifyAnalysisRequest(BaseModel):
    tracks: list[SpotifyTrackRequest] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def _validate_tracks(self) -> SpotifyAnalysisRequest:
        if len(self.tracks) != 2:
            raise ValueError("Exactly two tracks are required.")
        positions = [t.position for t in self.tracks]
        if "track_a" not in positions or "track_b" not in positions:
            raise ValueError("Must include exactly one track_a and one track_b.")
        ids = [t.spotify_track_id for t in self.tracks]
        if ids[0] == ids[1]:
            raise ValueError("Track A and Track B must be different.")
        return self

    def get_track_a(self) -> SpotifyTrackRequest:
        return next(t for t in self.tracks if t.position == "track_a")

    def get_track_b(self) -> SpotifyTrackRequest:
        return next(t for t in self.tracks if t.position == "track_b")


class TrackAcquisitionStatus(BaseModel):
    position: TrackPosition
    spotify_track_id: str
    success: bool
    error_message: str | None = None
    title: str | None = None
    artists: str | None = None
    duration_ms: int | None = None
    artwork_url: str | None = None
