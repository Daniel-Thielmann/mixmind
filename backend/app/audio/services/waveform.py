import logging
import time
from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
from app.core.config import settings
from app.schemas.waveform import WaveformResult
from app.utils.log_utils import log_memory

logger = logging.getLogger(__name__)


class WaveformGenerator:
    """Generate and persist waveform images for analyzed audio files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "waveforms")
        self._image_width = 1200
        self._image_height = 300

    def generate(self, audio_path: Path) -> WaveformResult:
        """Render the waveform for an audio file and save it as PNG."""

        logger.info("  WaveformGenerator starting for: %s", audio_path.name)
        log_memory("Waveform start")
        step_start = time.monotonic()

        self._output_dir.mkdir(parents=True, exist_ok=True)

        # POTENCIAL GARGALO: segundo librosa.load() do mesmo arquivo
        # (já carregado no AudioAnalyzer). Isso dobra o uso de memória
        # para cada track. Considere compartilhar o array de áudio.
        logger.info("  Waveform: loading audio (duplicate load)...")
        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        log_memory("Waveform after load")
        logger.info("  Waveform: loaded in %.2f s", time.monotonic() - step_start)

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name

        figure = plt.figure(figsize=(12, 3), dpi=100)
        axis = figure.add_subplot(111)
        librosa.display.waveshow(audio_data, sr=sample_rate, ax=axis)
        axis.set_axis_off()
        figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        figure.savefig(str(image_path), dpi=100)
        plt.close(figure)

        log_memory("Waveform end")

        return WaveformResult(
            image_path=(Path("processed") / "waveforms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


waveform_generator = WaveformGenerator()
