import gc
import logging
import time
import traceback
from pathlib import Path
from typing import ClassVar

import librosa
import numpy as np
import soundfile as sf
from app.core.exceptions import AudioAnalysisException
from app.core.log_utils import (
    log_memory,
    log_memory_detail,
)
from app.domain.entities.track import AudioAnalysis

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

    NOTES: ClassVar[list[str]] = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
    ]

    # Camelot Wheel Mapping
    CAMELOT_WHEEL: ClassVar[dict[str, str]] = {
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

    def analyze(
        self,
        audio_path: Path,
        audio_data: np.ndarray | None = None,
        sample_rate: int | None = None,
    ) -> AudioAnalysis:
        """
        Analyze an audio file and extract its main characteristics.

        Parameters
        ----------
        audio_path : Path
            Path to the audio file (used for metadata even if audio_data provided).
        audio_data : np.ndarray | None
            Pre-loaded mono audio array. If None, loads from file.
        sample_rate : int | None
            Sample rate corresponding to audio_data. Required if audio_data provided.
        """
        logger.info("  AudioAnalyzer starting for: %s", audio_path.name)
        log_memory("AudioAnalyzer start")

        # ---- File info before load ----
        try:
            file_size = audio_path.stat().st_size
            file_ext = audio_path.suffix.lower()
            file_exists = audio_path.exists()
            logger.info(
                "  File info: path=%s | exists=%s | size=%d bytes (%.2f MB) | ext=%s",
                audio_path,
                file_exists,
                file_size,
                file_size / (1024 * 1024),
                file_ext,
            )

            sf_info = sf.info(str(audio_path))
            logger.info(
                "  soundfile.info: samplerate=%d | channels=%d | frames=%d"
                " | duration=%.2f s | subtype=%s",
                sf_info.samplerate,
                sf_info.channels,
                sf_info.frames,
                sf_info.duration,
                sf_info.subtype,
            )
        except Exception:
            logger.exception("  File info gathering failed (non-fatal)")
            sf_info = None

        try:
            if audio_data is not None and sample_rate is not None:
                logger.info("  Using pre-loaded audio data (single-load optimization)")
                duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            else:
                logger.info("  Loading audio file...")
                load_start = time.monotonic()
                _y, _sr = librosa.load(
                    audio_path,
                    sr=None,
                    mono=True,
                )
                audio_data = _y
                sample_rate = int(_sr)
                load_elapsed = time.monotonic() - load_start
                log_memory("After librosa.load")
                duration = librosa.get_duration(y=audio_data, sr=sample_rate)
                logger.info(
                    "  Audio loaded in %.2f s | dtype=%s | shape=%s"
                    " | nbytes=%d (%.2f MB) | sr=%d | duration=%.2f s",
                    load_elapsed,
                    audio_data.dtype,
                    audio_data.shape,
                    audio_data.nbytes,
                    audio_data.nbytes / (1024 * 1024),
                    sample_rate,
                    duration,
                )

            # ================================================================
            # BEAT_TRACK — INSTRUMENTED
            # ================================================================
            # Internamente o beat_track faz:
            #   1. onset_strength = librosa.onset.onset_strength(y, sr)
            #      - Cria espectrograma STFT internamente (n_fft=2048, hop_length=512)
            #      - calcula mel-spectrogram (n_mels=128, fmax=11025)
            #      - soma espectral ponderada por banda mel -> onset envelope
            #      - O envelope de onset é um array 1D de tamanho ~ N/hop_length
            #      - Para uma track de 2:30 @ 44100 Hz: ~12900 samples
            #      - Isso são ~103 KB — não é o problema
            #   2. tempo, beats = librosa.beat.beat_track(onset_envelope=onsets, sr=sr)
            #      - Estima BPM via autocorrelação do envelope de onset
            #      - Calcula beat frames via predição dinâmica
            #      - A autocorrelação usa FFT (scipy.signal.fftconvolve ou np.fft)
            #      - Objetos temporários: envelope FFT, autocorrelação, beat frames
            # POSSÍVEL GARGALO: se a FFT criar arrays maiores que o esperado
            # POSSÍVEL GARGALO: scipy.signal.fftconvolve pode alocar buffers 2x
            # ================================================================
            logger.info("")
            logger.info("  === BEAT_TRACK START ===")
            logger.info(
                "  Input audio: shape=%s | dtype=%s | nbytes=%.2f MB | sr=%d",
                audio_data.shape,
                audio_data.dtype,
                audio_data.nbytes / (1024 * 1024),
                sample_rate,
            )
            log_memory_detail(
                "Before beat_track", f"audio_data shape={audio_data.shape}"
            )
            bpm_start = time.monotonic()

            try:
                # ---- Início do beat_track ----
                logger.info(
                    "  Calling librosa.beat.beat_track(y, sr=%d)...", sample_rate
                )
                logger.info(
                    "  (This will internally compute onset_strength + tempo estimation)"
                )

                tempo, beats = librosa.beat.beat_track(
                    y=audio_data,
                    sr=sample_rate,
                )

                bpm_elapsed = time.monotonic() - bpm_start
                logger.info("  librosa.beat.beat_track returned")
                beats_shape = beats.shape if hasattr(beats, "shape") else "N/A"
                log_memory_detail(
                    "After beat_track",
                    f"tempo={tempo}, beats.shape={beats_shape}",
                )
                logger.info("  === BEAT_TRACK END (%.2f s) ===", bpm_elapsed)
                logger.info("")

            except Exception:
                logger.error("  === BEAT_TRACK FAILED ===")
                log_memory_detail("beat_track FAILED")
                logger.error("  Traceback:\n%s", traceback.format_exc())
                raise

            # ---- Tarefa 5: gc.collect() após beat_track ----
            gc.collect()
            log_memory_detail("After beat_track + gc.collect")
            logger.info("  === POST BEAT_TRACK GC ===")
            # Verificar objetos grandes ainda vivos
            large_objects: list[tuple[str, tuple[int, ...], type, int]] = []
            for obj in gc.get_objects():
                try:
                    if isinstance(obj, np.ndarray) and obj.nbytes > 1024 * 1024:
                        large_objects.append(
                            (type(obj).__name__, obj.shape, obj.dtype, obj.nbytes)
                        )
                except ReferenceError:
                    pass
            if large_objects:
                logger.info("  Large numpy arrays still alive after beat_track + gc:")
                for i, (typ, shape, dtype, nbytes) in enumerate(large_objects):
                    logger.info(
                        "    [%d] %s shape=%s dtype=%s nbytes=%.2f MB",
                        i,
                        typ,
                        shape,
                        dtype,
                        nbytes / (1024 * 1024),
                    )
            else:
                logger.info(
                    "  No large numpy arrays (>1 MB) alive after beat_track + gc"
                )
            logger.info("  === END POST BEAT_TRACK GC ===")

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
