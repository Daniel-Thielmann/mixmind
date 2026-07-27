from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpotifyTrackMetadata:
    spotify_id: str
    spotify_url: str
    title: str
    artists: tuple[str, ...]
    album: str
    duration_ms: int
    isrc: str | None = None
    artwork_url: str | None = None
    popularity: int = 0

    @property
    def duration_seconds(self) -> float:
        return self.duration_ms / 1000.0

    @property
    def artist_names(self) -> str:
        return ", ".join(self.artists)

    def filename_safe(self) -> str:
        safe_title = "".join(
            c if c.isalnum() or c in " _-" else "_" for c in self.title
        )
        return f"{safe_title}_{self.spotify_id}.mp3"
