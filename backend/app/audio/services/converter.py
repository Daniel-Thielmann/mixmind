from pathlib import Path


class AudioConverter:
    """Converts audio files into the project standard format."""

    def convert(self, audio_path: Path) -> Path:
        raise NotImplementedError
