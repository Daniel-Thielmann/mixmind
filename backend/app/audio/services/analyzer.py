import logging
import time
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from app.core.exceptions import AudioAnalysisException
from app.schemas.audio import AudioAnalysis
from app.utils.log_utils import log_memory

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyze audio files and extract audio features using Librosa."""

    # Krumhansl-Schmuckler Profiles (Mathematical representation of musical scales)
    MAJOR_PROFILE = np.array(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    )
    MINOR_PROFILE = np.array(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    )

    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # Camelot Wheel Mapping
    CAMELOT_WHEEL = {
        "B Major": "1B",
        "G# Minor": "1A",
        "F# Major": "2B",
        "D# Minor": "2A",
        "C# Major": "3B",
        "A# Minor": "3A",
        "G# Major": "4B",
        "F Minor": "4A",
        "D# Major": "5B",
        "C Minor": "5A",
        "A# Major": "6B",
        "G Minor": "6A",
        "F Major": "7B",
        "D Minor": "7A",
        "C Major": "8B",
        "A Minor": "8A",
        "G Major": "9B",
        "E Minor": "9A",
        "D Major": "10B",
        "B Minor": "10A",
        "A Major": "11B",
        "F# Minor": "11A",
        "E Major": "12B",
        "C# Minor": "12A",
    }

    def _detect_key(self, y: np.ndarray, sr: int) -> str:
        """Calculates the musical key using the Krumhansl-Schmuckler algorithm."""

        logger.info("  Key detection: computing chroma_cqt (potentially heavy)...")
        log_memory("Chroma CQT start")

        # POTENCIAL GARGALO: chroma_cqt é computacionalmente caro para arquivos longos
        # e pode consumir muita memória dependendo do tamanho do áudio.
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        except Exception:
            logger.exception(
                "  chroma_cqt FAILED — this may be the root cause of the 502"
            )
            raise

        log_memory("Chroma CQT end")
        logger.info("  chroma_cqt computed — shape: %s", chroma.shape)

        chroma_sum = np.sum(chroma, axis=1)

        major_correlations = []
        minor_correlations = []

        for i in range(12):
            major_rot = np.roll(self.MAJOR_PROFILE, i)
            minor_rot = np.roll(self.MINOR_PROFILE, i)

            major_correlations.append(np.corrcoef(chroma_sum, major_rot)[0, 1])
            minor_correlations.append(np.corrcoef(chroma_sum, minor_rot)[0, 1])

        max_major_idx = np.argmax(major_correlations)
        max_minor_idx = np.argmax(minor_correlations)

        if major_correlations[max_major_idx] > minor_correlations[max_minor_idx]:
            detected = f"{self.NOTES[max_major_idx]} Major"
        else:
            detected = f"{self.NOTES[max_minor_idx]} Minor"

        logger.info("  Key detected: %s", detected)
        return detected

    def analyze(self, audio_path: Path) -> AudioAnalysis:
        """
        Analyze an audio file and extract its main characteristics.
        """
        logger.info("  AudioAnalyzer starting for: %s", audio_path.name)
        log_memory("AudioAnalyzer start")

        try:
            # POTENCIAL GARGALO: librosa.load carrega o arquivo inteiro em memória
            logger.info("  Loading audio file...")
            load_start = time.monotonic()
            audio_data, sample_rate = librosa.load(
                audio_path,
                sr=None,
                mono=True,
            )
            logger.info(
                "  Audio loaded in %.2f s | duration: %.2f s | sr: %d",
                time.monotonic() - load_start,
                librosa.get_duration(y=audio_data, sr=sample_rate),
                sample_rate,
            )
            log_memory("After librosa.load")

            duration = librosa.get_duration(
                y=audio_data,
                sr=sample_rate,
            )

            logger.info("  Computing BPM...")
            bpm_start = time.monotonic()
            tempo, _ = librosa.beat.beat_track(
                y=audio_data,
                sr=sample_rate,
            )
            logger.info("  BPM computed in %.2f s", time.monotonic() - bpm_start)

            logger.info("  Computing RMS energy...")
            rms = librosa.feature.rms(
                y=audio_data,
            )

            logger.info("  Detecting musical key (Camelot)...")
            key_start = time.monotonic()
            detected_key = self._detect_key(audio_data, int(sample_rate))
            camelot_code = self.CAMELOT_WHEEL.get(detected_key, "Unknown")
            logger.info(
                "  Key detection completed in %.2f s | key: %s | camelot: %s",
                time.monotonic() - key_start,
                detected_key,
                camelot_code,
            )

        except (
            librosa.util.exceptions.ParameterError,
            sf.LibsndfileError,
            OSError,
            ValueError,
        ) as exc:
            logger.exception("Audio analysis failed for: %s", audio_path.name)
            raise AudioAnalysisException(audio_path.name) from exc

        tempo = np.asarray(tempo).reshape(-1)[0]
        bpm = round(float(tempo), 2)

        energy = round(float(np.mean(rms)), 4)

        log_memory("AudioAnalyzer end")

        return AudioAnalysis(
            filename=audio_path.name,
            duration=round(float(duration), 2),
            sample_rate=int(sample_rate),
            bpm=bpm,
            energy=energy,
            key=detected_key,
            camelot=camelot_code,
        )
