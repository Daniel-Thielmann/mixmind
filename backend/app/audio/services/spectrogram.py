import logging
import time
from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from app.core.config import settings
from app.schemas.spectrogram import SpectrogramResult
from app.utils.log_utils import log_memory

logger = logging.getLogger(__name__)


class SpectrogramGenerator:
    """Generate and persist spectrogram images for analyzed audio files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "spectrograms")
        self._image_width = 1200
        self._image_height = 500

    def generate(self, audio_path: Path) -> SpectrogramResult:
        """Render the spectrogram for an audio file and save it as PNG."""

        logger.info("  SpectrogramGenerator starting for: %s", audio_path.name)
        log_memory("Spectrogram start")
        step_start = time.monotonic()

        self._output_dir.mkdir(parents=True, exist_ok=True)

        # POTENCIAL GARGALO: terceiro librosa.load() do mesmo arquivo.
        # AudioAnalyzer + WaveformGenerator já carregaram. Isso triplica a memória.
        logger.info("  Spectrogram: loading audio (duplicate load)...")
        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        log_memory("Spectrogram after load")
        logger.info("  Spectrogram: loaded in %.2f s", time.monotonic() - step_start)

        # POTENCIAL GARGALO: STFT em arrays grandes, especialmente para músicas longas
        logger.info("  Spectrogram: computing STFT...")
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

        log_memory("Spectrogram end")

        return SpectrogramResult(
            image_path=(Path("processed") / "spectrograms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


spectrogram_generator = SpectrogramGenerator()
