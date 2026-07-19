import logging
from pathlib import Path
from uuid import uuid4

import numpy as np
import soundfile as sf
import soxr
from PIL import Image, ImageDraw

from app.core.config import settings
from app.core.log_utils import log_memory
from app.domain.value_objects.visualization import WaveformResult

logger = logging.getLogger(__name__)


class WaveformGenerator:
    """Generate a bounded waveform PNG without Matplotlib."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "waveforms")
        self._image_width = 1200
        self._image_height = 300

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
    ) -> WaveformResult:
        logger.info("  WaveformGenerator starting for: %s", audio_path.name)
        log_memory("Waveform start")
        self._output_dir.mkdir(parents=True, exist_ok=True)

        if audio_data is None or sample_rate is None:
            audio_data, sample_rate = self._load_bounded(audio_path)

        width = self._image_width
        height = self._image_height
        samples_per_column = max(1, audio_data.size // width)
        usable = min(audio_data.size, samples_per_column * width)
        peaks = np.max(
            np.abs(audio_data[:usable].reshape(-1, samples_per_column)), axis=1
        )
        if peaks.size < width:
            peaks = np.pad(peaks, (0, width - peaks.size))
        peaks = peaks[:width]
        scale = float(np.max(peaks)) or 1.0
        amplitudes = np.clip(peaks / scale, 0.0, 1.0)

        image = Image.new("RGB", (width, height), (8, 15, 24))
        draw = ImageDraw.Draw(image)
        center = height // 2
        for x, amplitude in enumerate(amplitudes):
            half = max(1, int(amplitude * (height // 2 - 8)))
            draw.line((x, center - half, x, center + half), fill=(51, 224, 199))

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name
        image.save(image_path, format="PNG", optimize=True)
        image.close()
        log_memory("Waveform end")

        return WaveformResult(
            image_path=(Path("processed") / "waveforms" / image_name).as_posix(),
            width=width,
            height=height,
        )


waveform_generator = WaveformGenerator()
