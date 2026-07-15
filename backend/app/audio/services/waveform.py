import logging
import time
from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
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

    def generate(
        self,
        audio_path: Path,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> WaveformResult:
        """Render the waveform for an audio file and save it as PNG.

        Parameters
        ----------
        audio_path : Path
            Path to the audio file (used for naming even if audio_data provided).
        audio_data : np.ndarray | None
            Pre-loaded mono audio array. If None, loads from file.
        sample_rate : int | None
            Sample rate corresponding to audio_data. Required if audio_data provided.
        """
        logger.info("  WaveformGenerator starting for: %s", audio_path.name)
        log_memory("Waveform start")

        self._output_dir.mkdir(parents=True, exist_ok=True)

        # ---- librosa.load (avoided when pre-loaded data provided) ----
        if audio_data is not None and sample_rate is not None:
            logger.info("  Waveform: using pre-loaded audio data (single-load)")
        else:
            logger.info("  Waveform: loading audio...")
            load_start = time.monotonic()
            audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
            log_memory("Waveform after load")
            logger.info(
                "  Waveform: loaded in %.2f s | dtype=%s | shape=%s"
                " | nbytes=%d (%.2f MB)",
                time.monotonic() - load_start,
                audio_data.dtype,
                audio_data.shape,
                audio_data.nbytes,
                audio_data.nbytes / (1024 * 1024),
            )

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name

        # ---- Figure creation ----
        logger.info("  Waveform: creating matplotlib figure...")
        log_memory("Waveform before figure")
        figure = plt.figure(figsize=(12, 3), dpi=100)
        axis = figure.add_subplot(111)
        log_memory("Waveform after figure")

        # ---- waveshow ----
        logger.info("  Waveform: rendering waveshow...")
        librosa.display.waveshow(audio_data, sr=sample_rate, ax=axis)
        axis.set_axis_off()
        figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # ---- Release audio data after rendering ----
        del audio_data
        logger.info("  Waveform: audio data released")

        # ---- savefig ----
        logger.info("  Waveform: saving PNG (1200x300, 100dpi)...")
        log_memory("Waveform before savefig")
        figure.savefig(str(image_path), dpi=100)
        log_memory("Waveform after savefig")

        # ---- close + cleanup ----
        figure.clf()
        plt.close(figure)
        del figure
        logger.info("  Waveform: figure closed and released")

        log_memory("Waveform end")

        return WaveformResult(
            image_path=(Path("processed") / "waveforms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


waveform_generator = WaveformGenerator()
