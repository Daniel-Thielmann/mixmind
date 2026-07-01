from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import settings


class BaseImageGenerator(ABC):
    """
    Shared infrastructure for image generators.

    Handles analysis‑directory creation, filename generation, and
    public‑URL construction so that concrete subclasses only need to
    implement the DSP rendering logic.
    """

    def __init__(self, image_width: int, image_height: int) -> None:
        self._image_width = image_width
        self._image_height = image_height

    def _ensure_analysis_dir(self, analysis_id: str) -> Path:
        analysis_dir = settings.analysis_path / analysis_id
        analysis_dir.mkdir(parents=True, exist_ok=True)
        return analysis_dir

    def _build_filename(self, track_label: str) -> str:
        return f"{self._subdir_prefix}_track_{track_label}.png"

    def _build_relative_path(self, analysis_id: str, filename: str) -> str:
        return f"processed/analysis/{analysis_id}/{filename}"

    def _build_url(self, analysis_id: str, filename: str) -> str:
        base = settings.BASE_URL.rstrip("/")
        return f"{base}/static/analysis/{analysis_id}/{filename}"

    @property
    @abstractmethod
    def _subdir_prefix(self) -> str:
        """Used as the filename prefix, e.g. 'waveform' or 'spectrogram'."""
