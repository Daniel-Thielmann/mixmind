from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.entities.track import AudioAnalysis


class TrackRepository(ABC):
    @abstractmethod
    def save_analysis(self, analysis_id: str, analysis: AudioAnalysis) -> None: ...

    @abstractmethod
    def get_analysis(self, analysis_id: str) -> AudioAnalysis | None: ...

    @abstractmethod
    def get_audio_path(self, filename: str) -> Path | None: ...
