from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from app.core.config import settings
from app.schemas.spectrogram import SpectrogramResult


class SpectrogramGenerator:
    """Generate and persist spectrogram images for analyzed audio files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "spectrograms")
        self._image_width = 1200
        self._image_height = 500

    def generate(self, audio_path: Path) -> SpectrogramResult:
        """Render the spectrogram for an audio file and save it as PNG."""

        self._output_dir.mkdir(parents=True, exist_ok=True)

        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        spectrogram_db = librosa.amplitude_to_db(magnitude, ref=np.max)

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name

        figure = plt.figure(figsize=(12, 5), dpi=100)
        axis = figure.add_subplot(111)
        spec_image = librosa.display.specshow(
            spectrogram_db,
            sr=sample_rate,
            x_axis="time",
            y_axis="hz",
            ax=axis,
        )
        figure.colorbar(spec_image, ax=axis, format="%+2.0f dB")
        axis.set_title("Spectrogram")
        axis.set_xlabel("Time")
        axis.set_ylabel("Frequency")
        figure.tight_layout()
        figure.savefig(str(image_path), dpi=100)
        plt.close(figure)

        return SpectrogramResult(
            image_path=(Path("processed") / "spectrograms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


spectrogram_generator = SpectrogramGenerator()
