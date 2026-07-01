from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from app.audio.services.base_image_generator import BaseImageGenerator
from app.schemas.spectrogram import SpectrogramResult


class SpectrogramGenerator(BaseImageGenerator):
    """Generate and persist spectrogram images for analyzed audio files."""

    def __init__(self) -> None:
        super().__init__(image_width=1200, image_height=500)

    @property
    def _subdir_prefix(self) -> str:
        return "spectrogram"

    def generate(
        self,
        audio_path: Path,
        analysis_id: str,
        track_label: str,
    ) -> SpectrogramResult:
        """Render the spectrogram for an audio file and save it as PNG."""

        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        spectrogram_db = librosa.amplitude_to_db(magnitude, ref=np.max)

        filename = self._build_filename(track_label)
        analysis_dir = self._ensure_analysis_dir(analysis_id)
        image_path = analysis_dir / filename

        figure = plt.figure(figsize=(12, 5), dpi=100)
        axis = figure.add_subplot(111)
        spec_image = librosa.display.specshow(
            spectrogram_db,
            sr=sample_rate,
            x_axis="time",
            y_axis="hz",
            ax=axis,
        )
        figure.colorbar(spec_image, ax=[axis], format="%+2.0f dB")
        axis.set_title("Spectrogram")
        axis.set_xlabel("Time")
        axis.set_ylabel("Frequency")
        figure.tight_layout()
        figure.savefig(str(image_path), dpi=100)
        plt.close(figure)

        return SpectrogramResult(
            image_path=self._build_relative_path(analysis_id, filename),
            url=self._build_url(analysis_id, filename),
            width=self._image_width,
            height=self._image_height,
        )


spectrogram_generator = SpectrogramGenerator()
