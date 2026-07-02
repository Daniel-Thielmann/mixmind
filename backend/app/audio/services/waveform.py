from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
from app.core.config import settings
from app.schemas.waveform import WaveformResult


class WaveformGenerator:
    """Generate and persist waveform images for analyzed audio files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "waveforms")
        self._image_width = 1200
        self._image_height = 300

    def generate(self, audio_path: Path) -> WaveformResult:
        """Render the waveform for an audio file and save it as PNG."""

        self._output_dir.mkdir(parents=True, exist_ok=True)

        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name

        figure = plt.figure(figsize=(12, 3), dpi=100)
        axis = figure.add_subplot(111)
        librosa.display.waveshow(audio_data, sr=sample_rate, ax=axis)
        axis.set_axis_off()
        figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        figure.savefig(str(image_path), dpi=100)
        plt.close(figure)

        return WaveformResult(
            image_path=(Path("processed") / "waveforms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


waveform_generator = WaveformGenerator()
