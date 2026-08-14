from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class YouTubeTrackRequest(BaseModel):
    position: str
    youtube_video_id: str = Field(pattern=r"^[A-Za-z0-9_-]{11}$")


class YouTubeAnalysisRequest(BaseModel):
    tracks: list[YouTubeTrackRequest] = Field(min_length=2, max_length=2)

    @model_validator(mode="after")
    def validate_tracks(self) -> YouTubeAnalysisRequest:
        if {track.position for track in self.tracks} != {"track_a", "track_b"}:
            raise ValueError("Must include exactly one track_a and one track_b.")
        if len({track.youtube_video_id for track in self.tracks}) != 2:
            raise ValueError("Track A and Track B must be different.")
        return self

    def video_id(self, position: str) -> str:
        return next(
            track.youtube_video_id
            for track in self.tracks
            if track.position == position
        )
