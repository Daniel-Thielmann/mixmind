import gc
import logging
import time
from pathlib import Path
from uuid import uuid4

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from app.core.config import settings
from app.core.log_utils import log_memory
from app.domain.value_objects.visualization import SpectrogramResult

logger = logging.getLogger(__name__)


class SpectrogramGenerator:
    """Generate and persist spectrogram images for analyzed audio files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or (settings.processed_path / "spectrograms")
        self._image_width = 1200
        self._image_height = 500

    def generate(
        self,
        audio_path: Path,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> SpectrogramResult:
        """Render the spectrogram for an audio file and save it as PNG.

        Parameters
        ----------
        audio_path : Path
            Path to the audio file (used for naming even if audio_data provided).
        audio_data : np.ndarray | None
            Pre-loaded mono audio array. If None, loads from file.
        sample_rate : int | None
            Sample rate corresponding to audio_data. Required if audio_data provided.
        """
        logger.info("  SpectrogramGenerator starting for: %s", audio_path.name)
        log_memory("Spectrogram start")

        self._output_dir.mkdir(parents=True, exist_ok=True)

        # ---- librosa.load (avoided when pre-loaded data provided) ----
        if audio_data is not None and sample_rate is not None:
            logger.info("  Spectrogram: using pre-loaded audio data (single-load)")
        else:
            logger.info("  Spectrogram: loading audio...")
            load_start = time.monotonic()
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            audio_data = y
            sample_rate = int(sr)
            log_memory("Spectrogram after load")
            logger.info(
                "  Spectrogram: loaded in %.2f s | dtype=%s | shape=%s"
                " | nbytes=%d (%.2f MB)",
                time.monotonic() - load_start,
                audio_data.dtype,
                audio_data.shape,
                audio_data.nbytes,
                audio_data.nbytes / (1024 * 1024),
            )

        # ---- Chained STFT → magnitude → dB ----
        # n_fft=1024, hop_length=1024 reduz arrays do STFT em ~4×
        # (stft: 108→27 MB, magnitude: 54→13 MB, dB: 54→13 MB).
        # Chaining elimina referências intermediárias: CPython coleta stft
        # assim que np.abs() termina, e coleta magnitude assim que
        # amplitude_to_db() termina. Pico: stft + magnitude brevemente
        # (~40 MB), nunca stft + magnitude + dB simultaneamente.
        logger.info("  Spectrogram: computing STFT + magnitude + dB (chained)...")
        log_memory("Spectrogram before STFT")
        chain_start = time.monotonic()
        spectrogram_db = librosa.amplitude_to_db(
            np.abs(librosa.stft(audio_data, n_fft=1024, hop_length=1024)), ref=np.max
        )
        logger.info(
            "  Spectrogram: STFT→|·|→dB computed in %.2f s | shape=%s",
            time.monotonic() - chain_start,
            spectrogram_db.shape,
        )
        log_memory("Spectrogram after dB")

        # ---- Release audio data (local ref only; caller must free too) ----
        del audio_data
        logger.info("  Spectrogram: audio data local reference released")

        image_name = f"{uuid4().hex}.png"
        image_path = self._output_dir / image_name

        # ---- Figure creation ----
        logger.info("  Spectrogram: creating matplotlib figure...")
        log_memory("Spectrogram before figure")
        figure = plt.figure(figsize=(12, 5), dpi=100)
        axis = figure.add_subplot(111)
        log_memory("Spectrogram after figure")

        # ---- specshow ----
        logger.info("  Spectrogram: rendering specshow...")
        spec_image = librosa.display.specshow(
            spectrogram_db,
            sr=sample_rate,
            x_axis="time",
            y_axis="hz",
            ax=axis,
        )

        # ---- Release spectrogram_db after specshow rendered ----
        del spectrogram_db
        logger.info("  Spectrogram: spectrogram data released after rendering")

        # ---- colorbar ----
        logger.info("  Spectrogram: adding colorbar...")
        figure.colorbar(spec_image, ax=[axis], format="%+2.0f dB")
        axis.set_title("Spectrogram")
        axis.set_xlabel("Time")
        axis.set_ylabel("Frequency")
        figure.tight_layout()

        del spec_image

        # ---- savefig ----
        logger.info("  Spectrogram: saving PNG (1200x500, 100dpi)...")
        log_memory("Spectrogram before savefig")
        figure.savefig(str(image_path), dpi=100)
        log_memory("Spectrogram after savefig")

        # ---- close + gc ----
        figure.clf()
        plt.close(figure)
        del figure
        logger.info("  Spectrogram: figure closed and released")

        gc.collect()
        log_memory("Spectrogram end")

        return SpectrogramResult(
            image_path=(Path("processed") / "spectrograms" / image_name).as_posix(),
            width=self._image_width,
            height=self._image_height,
        )


spectrogram_generator = SpectrogramGenerator()
