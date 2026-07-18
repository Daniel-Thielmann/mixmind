from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class AudioAnalyzerPort(ABC):
    @abstractmethod
    def analyze(
        self,
        audio_path: Path,
        *,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> dict[str, object]: ...


class WaveformPort(ABC):
    @abstractmethod
    def generate(
        self,
        audio_path: Path,
        *,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> object: ...


class SpectrogramPort(ABC):
    @abstractmethod
    def generate(
        self,
        audio_path: Path,
        *,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> object: ...
