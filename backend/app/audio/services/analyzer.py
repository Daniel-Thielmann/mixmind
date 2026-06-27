from pathlib import Path

from app.schemas.audio import AudioAnalysis


class AudioAnalyzer:
    """Analyzes converted audio files and extracts metrics."""

    def analyze(self, audio_path: Path) -> AudioAnalysis:
        raise NotImplementedError
