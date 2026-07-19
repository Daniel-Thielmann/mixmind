import logging
from pathlib import Path
from uuid import uuid4

import numpy as np
import soundfile as sf
import soxr
from PIL import Image

from app.core.config import settings
from app.core.log_utils import log_memory
from app.domain.value_objects.visualization import SpectrogramResult

logger = logging.getLogger(__name__)


class SpectrogramGenerator:
    """Generate a bounded spectrogram PNG without Matplotlib."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "spectrograms")
        self._image_width = 1200
        self._image_height = 500

    @staticmethod
    def _load_bounded(audio_path: Path) -> tuple[np.ndarray, int]:
        with sf.SoundFile(str(audio_path)) as audio_file:
            native_sr = int(audio_file.samplerate)
            decoded = audio_file.read(
                frames=native_sr * settings.ANALYSIS_MAX_DURATION,
                dtype="float32",
                always_2d=True,
            )
        mono = decoded.mean(axis=1, dtype=np.float32)
        if native_sr != settings.ANALYSIS_SAMPLE_RATE:
            mono = soxr.resample(
                mono, native_sr, settings.ANALYSIS_SAMPLE_RATE, quality="LQ"
            )
        return np.ascontiguousarray(
            mono, dtype=np.float32
        ), settings.ANALYSIS_SAMPLE_RATE

    def generate(
        self,
        audio_path: Path,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> SpectrogramResult:
        logger.info("  SpectrogramGenerator starting for: %s", audio_path.name)
        log_memory("Spectrogram start")
        self._output_dir.mkdir(parents=True, exist_ok=True)

        if audio_data is None or sample_rate is None:
            audio_data, sample_rate = self._load_bounded(audio_path)

        fft_size = 1024
        column_count = min(self._image_width, max(1, audio_data.size // fft_size))
        starts = np.linspace(
            0, max(0, audio_data.size - fft_size), num=column_count, dtype=np.int64
        )
        window = np.hanning(fft_size).astype(np.float32)
        magnitude = np.empty((fft_size // 2 + 1, column_count), dtype=np.float32)
        for column, start in enumerate(starts):
            frame = audio_data[start : start + fft_size]
            magnitude[:, column] = np.abs(np.fft.rfft(frame * window))

        db = 20.0 * np.log10(np.maximum(magnitude, 1e-6))
        del magnitude
        db -= float(db.max())
        intensity = np.clip((db + 80.0) / 80.0, 0.0, 1.0)
        del db

        red = np.asarray(20 + 35 * intensity, dtype=np.uint8)
        green = np.asarray(20 + 220 * intensity, dtype=np.uint8)
        blue = np.asarray(35 + 180 * np.sqrt(intensity), dtype=np.uint8)
        rgb = np.dstack((red, green, blue))[::-1]
        image = Image.fromarray(rgb, mode="RGB")
        image = image.resize(
            (self._image_width, self._image_height), resample=Image.Resampling.BILINEAR
        )

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name
        image.save(image_path, format="PNG", optimize=True)
        image.close()
        log_memory("Spectrogram end")

        return SpectrogramResult(
            image_path=(Path("processed") / "spectrograms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


spectrogram_generator = SpectrogramGenerator()
