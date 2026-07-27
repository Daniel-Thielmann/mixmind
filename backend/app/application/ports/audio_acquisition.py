from __future__ import annotations

from typing import Protocol

from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata


class AudioAcquisitionProvider(Protocol):
    def acquire(self, track_metadata: SpotifyTrackMetadata) -> AcquiredAudio: ...
