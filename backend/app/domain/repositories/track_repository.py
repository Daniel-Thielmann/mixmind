from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.entities.track import AudioAnalysis, Track
from app.domain.value_objects.identifiers import TrackId


class TrackRepository(ABC):
    @abstractmethod
    def save(self, entity: Track) -> None: ...

    @abstractmethod
    def find_by_id(self, track_id: TrackId) -> Track | None: ...

    @abstractmethod
    def find_all(self) -> list[Track]: ...

    @abstractmethod
    def update(self, entity: Track) -> None: ...

    @abstractmethod
    def delete(self, track_id: TrackId) -> None: ...

    @abstractmethod
    def save_analysis(self, analysis_id: str, analysis: AudioAnalysis) -> None: ...

    @abstractmethod
    def get_analysis(self, analysis_id: str) -> AudioAnalysis | None: ...

    @abstractmethod
    def get_audio_path(self, filename: str) -> Path | None: ...
