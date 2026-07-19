import logging
import time
from pathlib import Path
from typing import ClassVar

import numpy as np
import soundfile as sf
import soxr

from app.core.config import settings
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
        """Estimate musical key from a small set of bounded FFT windows."""
        logger.info("  Key detection: computing bounded NumPy chroma...")
        log_memory("Key detection start")
        window_size = 8192
        chroma_sum = np.zeros(12, dtype=np.float64)
        if y.size >= window_size:
            starts = np.linspace(0, y.size - window_size, num=12, dtype=np.int64)
            window = np.hanning(window_size).astype(np.float32)
            frequencies = np.fft.rfftfreq(window_size, d=1.0 / sr)
            valid = (frequencies >= 55.0) & (frequencies <= 5000.0)
            midi = np.rint(69.0 + 12.0 * np.log2(frequencies[valid] / 440.0))
            pitch_classes = np.mod(midi.astype(np.int16), 12)
            for start in starts:
                spectrum = np.abs(np.fft.rfft(y[start : start + window_size] * window))
                power = np.square(spectrum[valid], dtype=np.float64)
                chroma_sum += np.bincount(pitch_classes, weights=power, minlength=12)[
                    :12
                ]
        else:
            chroma_sum[0] = 1.0

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
        log_memory("Key detection end")
        return detected

    @staticmethod
    def _estimate_bpm(y: np.ndarray, sr: int) -> float:
        """Estimate tempo from bounded spectral flux without scipy or numba."""
        stride = max(1, sr // 5512)
        reduced = y[::stride]
        reduced_sr = sr / stride
        fft_size = 512
        hop = 128
        frame_count = 1 + max(0, (reduced.size - fft_size) // hop)
        if frame_count < 8:
            return 120.0

        window = np.hanning(fft_size).astype(np.float32)
        onset = np.zeros(frame_count, dtype=np.float32)
        previous = np.zeros(fft_size // 2 + 1, dtype=np.float32)
        for index in range(frame_count):
            start = index * hop
            magnitude = np.abs(np.fft.rfft(reduced[start : start + fft_size] * window))
            onset[index] = np.maximum(magnitude - previous, 0.0).sum()
            previous = magnitude

        onset -= np.median(onset)
        onset = np.maximum(onset, 0.0)
        onset -= onset.mean()
        envelope_rate = reduced_sr / hop
        min_lag = max(1, int(envelope_rate * 60.0 / 200.0))
        max_lag = min(onset.size - 1, int(envelope_rate * 60.0 / 60.0))
        if max_lag <= min_lag or not np.any(onset):
            return 120.0

        correlations = []
        for lag in range(min_lag, max_lag + 1):
            left = onset[:-lag]
            right = onset[lag:]
            denominator = np.linalg.norm(left) * np.linalg.norm(right)
            correlations.append(
                float(np.dot(left, right) / denominator) if denominator else 0.0
            )
        lag = min_lag + int(np.argmax(correlations))
        bpm = 60.0 * envelope_rate / lag
        while bpm < 80.0:
            bpm *= 2.0
        while bpm > 180.0:
            bpm /= 2.0
        return float(bpm)

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
                duration = audio_data.size / sample_rate
            else:
                logger.info("  Loading audio file...")
                load_start = time.monotonic()
                with sf.SoundFile(str(audio_path)) as audio_file:
                    native_sr = int(audio_file.samplerate)
                    decoded = audio_file.read(
                        frames=native_sr * settings.ANALYSIS_MAX_DURATION,
                        dtype="float32",
                        always_2d=True,
                    )
                mono = decoded.mean(axis=1, dtype=np.float32)
                del decoded
                sample_rate = settings.ANALYSIS_SAMPLE_RATE
                audio_data = (
                    soxr.resample(mono, native_sr, sample_rate, quality="LQ")
                    if native_sr != sample_rate
                    else mono
                )
                audio_data = np.ascontiguousarray(audio_data, dtype=np.float32)
                load_elapsed = time.monotonic() - load_start
                log_memory("After bounded decode")
                duration = audio_data.size / sample_rate
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
                    "  Calling lightweight BPM estimator (sr=%d)...", sample_rate
                )
                logger.info("  (bounded energy envelope + short-lag autocorrelation)")

                tempo = self._estimate_bpm(audio_data, int(sample_rate))

                bpm_elapsed = time.monotonic() - bpm_start
                logger.info("  lightweight BPM estimation returned")
                log_memory_detail(
                    "After beat_track",
                    f"tempo={tempo}",
                )
                logger.info("  === BEAT_TRACK END (%.2f s) ===", bpm_elapsed)
                logger.info("")

            except Exception:
                logger.error("  === BEAT_TRACK FAILED ===")
                log_memory_detail("beat_track FAILED")
                raise

            logger.info("  Computing RMS energy...")
            energy = float(
                np.sqrt(np.mean(np.square(audio_data[::4], dtype=np.float64)))
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

        except (sf.LibsndfileError, OSError, ValueError) as exc:
            logger.exception("Audio analysis failed for: %s", audio_path.name)
            raise AudioAnalysisException(audio_path.name) from exc

        bpm = round(float(tempo), 2)
        energy = round(energy, 4)

        log_memory("AudioAnalyzer end")

        return AudioAnalysis(
            filename=audio_path.name,
            duration=round(
                float(sf_info.duration) if sf_info is not None else float(duration),
                2,
            ),
            sample_rate=(
                int(sf_info.samplerate) if sf_info is not None else int(sample_rate)
            ),
            bpm=bpm,
            energy=energy,
            key=detected_key,
            camelot=camelot_code,
        )
