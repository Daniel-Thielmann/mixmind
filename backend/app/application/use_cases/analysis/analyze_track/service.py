import gc
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from uuid import uuid4

import librosa
import numpy as np
from fastapi import UploadFile

from app.application.dto.api import AnalysisMetadata, UploadAnalysisResponse
from app.application.use_cases.compatibility.compare_tracks.service import (
    CompatibilityService,
    compatibility_service,
)
from app.core.config import settings
from app.core.log_utils import (
    get_memory_mb,
    log_audio_metadata,
    log_library_versions,
    log_memory,
)
from app.domain.value_objects.visualization import Spectrograms, Waveforms
from app.infrastructure.audio.analyzer import AudioAnalyzer
from app.infrastructure.audio.spectrogram import (
    SpectrogramGenerator,
    spectrogram_generator,
)
from app.infrastructure.audio.waveform import (
    WaveformGenerator,
    waveform_generator,
)
from app.infrastructure.llm.agent import DJAgent, dj_agent
from app.infrastructure.llm.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.infrastructure.storage.storage_service import (
    StorageService,
    storage_service,
)

logger = logging.getLogger(__name__)

# ---- Startup instrumentation ----
_logged_versions = False


def _ensure_version_logged() -> None:
    global _logged_versions
    if not _logged_versions:
        log_library_versions()
        _logged_versions = True


def _detect_load_backend(path: Path) -> str:
    """Detect which backend librosa will use for a given file."""
    ext = os.path.splitext(str(path))[1].lower()
    soundfile_exts = {".wav", ".flac", ".ogg", ".aiff", ".aif", ".au", ".pcm", ".svx"}
    if ext in soundfile_exts:
        return "soundfile"
    else:
        return "audioread (ffmpeg)"


def _log_file_details(path: Path, label: str) -> None:
    """Log detailed file information before loading."""
    try:
        stat = os.stat(str(path))
        ext = os.path.splitext(str(path))[1].lower()
        backend = _detect_load_backend(path)
        logger.info(
            "  File [%s]: path=%s | size=%d bytes (%.2f MB) | ext=%s | backend=%s",
            label,
            path.name,
            stat.st_size,
            stat.st_size / (1024 * 1024),
            ext,
            backend,
        )

        # For audioread backends, check ffmpeg availability
        if backend == "audioread (ffmpeg)":
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                first_line = result.stdout.split("\n")[0] if result.stdout else "N/A"
                logger.info("  ffmpeg: %s", first_line)
            except Exception as exc:
                logger.info("  ffmpeg check failed: %s", exc)

        # Try soundfile.info for metadata (works with most formats)
        try:
            import soundfile as sf

            sf_info = sf.info(str(path))
            logger.info(
                "  soundfile.info [%s]: samplerate=%d | channels=%d | frames=%d"
                " | duration=%.2f s | format=%s | subtype=%s",
                label,
                sf_info.samplerate,
                sf_info.channels,
                sf_info.frames,
                sf_info.duration,
                sf_info.format,
                sf_info.subtype,
            )
        except Exception as exc:
            logger.info("  soundfile.info [%s] not available: %s", label, exc)
    except Exception as exc:
        logger.warning("  File detail logging failed for %s: %s", label, exc)


def _load_audio_once(path: Path, label: str) -> tuple[np.ndarray, int]:
    """Load audio from disk exactly once. Used by AnalysisService to
    share the same ndarray across AudioAnalyzer, WaveformGenerator,
    and SpectrogramGenerator."""
    mem_entry = get_memory_mb()
    log_memory(f"Enter _load_audio_once {label}")

    _ensure_version_logged()

    log_memory(f"After version logging {label}")

    logger.info("")
    logger.info("=" * 50)
    logger.info("  LOADING AUDIO: %s (%s)", label, path.name)
    logger.info("=" * 50)

    _log_file_details(path, label)

    log_memory(f"After file details {label}")

    mem_before_load = get_memory_mb()
    log_memory(f"Before librosa.load {label}")
    load_start = time.monotonic()

    # ---- librosa.load ----
    # sr=None: native sample rate, no resampling
    # mono=True: average channels to mono
    _y, _sr = librosa.load(path, sr=None, mono=True)
    audio_data: np.ndarray = _y
    sr: int = int(_sr)

    load_elapsed = time.monotonic() - load_start
    mem_now = get_memory_mb()
    log_memory(f"After load {label}")

    log_audio_metadata(label, audio_data, sr, load_elapsed)

    delta_from_load = mem_now - mem_before_load
    ndarray_mb = audio_data.nbytes / (1024 * 1024)
    overhead_mb = delta_from_load - ndarray_mb

    logger.info("")
    logger.info("  --- MEMORY ACCOUNTING [%s] ---", label)
    logger.info("  Memory at entry:        %.2f MB", mem_entry)
    logger.info("  Memory BEFORE load:     %.2f MB", mem_before_load)
    logger.info("  Memory AFTER load:      %.2f MB", mem_now)
    logger.info("  Cost: version+file info: +%.2f MB", mem_before_load - mem_entry)
    logger.info("  Delta (librosa.load):   +%.2f MB", delta_from_load)
    logger.info("  ndarray.nbytes:         %.2f MB", ndarray_mb)
    logger.info("  Overhead (delta - arr):  %.2f MB", overhead_mb)
    logger.info(
        "  Ratio (delta/ndarray):  %.1fx",
        delta_from_load / ndarray_mb if ndarray_mb > 0 else 0,
    )
    if overhead_mb > ndarray_mb * 2:
        logger.warning(
            "  *** HIGH MEMORY OVERHEAD [%s]: overhead (%.2f MB)"
            " is %.1fx the ndarray size (%.2f MB) ***",
            label,
            overhead_mb,
            overhead_mb / ndarray_mb if ndarray_mb > 0 else 0,
            ndarray_mb,
        )
    logger.info("  --- END ACCOUNTING ---")
    logger.info("")

    return audio_data, sr


def _release_audio(label: str, *arrays: object) -> None:
    """Delete numpy arrays and force garbage collection."""
    for arr in arrays:
        if arr is not None:
            del arr
    gc.collect()
    log_memory(f"After release {label}")
    logger.info("  Released memory for %s", label)


class AnalysisService:
    """
    Orchestrates the analysis pipeline.

    Generates a unique session identifier for each analysis, persists all
    artefacts inside a dedicated folder, and writes an ``analysis.json``
    metadata file.
    """

    def __init__(
        self,
        storage: StorageService = storage_service,
        analyzer: AudioAnalyzer | None = None,
        waveform_service: WaveformGenerator | None = None,
        spectrogram_service: SpectrogramGenerator | None = None,
        compatibility: CompatibilityService | None = None,
        ai_agent: DJAgent | None = None,
    ) -> None:
        self._storage = storage
        self._analyzer = analyzer or AudioAnalyzer()
        self._waveform_generator = waveform_service or waveform_generator
        self._spectrogram_generator = spectrogram_service or spectrogram_generator
        self._compatibility = compatibility or compatibility_service
        self._ai_agent = ai_agent or dj_agent

    def analyze(
        self,
        track_a: UploadFile,
        track_b: UploadFile,
    ) -> UploadAnalysisResponse:
        """Store both uploads, analyze them, and return the API response."""

        logger.info("=" * 60)
        logger.info("Starting analysis pipeline (single-load optimized)")
        logger.info("=" * 60)
        log_memory("Initial")
        pipeline_start = time.monotonic()

        analysis_id = uuid4().hex

        # ---- Step 1 - Saving uploaded files ----
        step_start = time.monotonic()
        try:
            log_memory("Before save")
            path_a = self._storage.save_audio(track_a)
            path_b = self._storage.save_audio(track_b)
            log_memory("After save")
            logger.info(
                "Step 1 - Saving uploaded files completed in %.2f s | files: %s, %s",
                time.monotonic() - step_start,
                path_a.name,
                path_b.name,
            )
        except Exception:
            logger.exception("Step 1 - Saving uploaded files FAILED")
            raise

        # ---- Step 2 - Audio analysis Track A ----
        step_start = time.monotonic()
        try:
            audio_data_a, sr_a = _load_audio_once(path_a, "Track A")
            log_memory("Before AudioAnalyzer A")
            analysis_a = self._analyzer.analyze(
                path_a, audio_data=audio_data_a, sample_rate=sr_a
            ).model_copy(update={"filename": track_a.filename or ""})
            log_memory("After AudioAnalyzer A")
            logger.info(
                "Step 2 - Audio analysis Track A completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 2 - Audio analysis Track A FAILED")
            raise

        # ---- Step 3 - Waveform Track A (reuses audio_data_a) ----
        step_start = time.monotonic()
        try:
            log_memory("Before Waveform A")
            waveform_a = self._waveform_generator.generate(
                path_a, audio_data=audio_data_a, sample_rate=sr_a
            )
            log_memory("After Waveform A")
            logger.info(
                "Step 3 - Waveform Track A completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 3 - Waveform Track A FAILED")
            raise

        # ---- Release audio_data_a BEFORE Spectrogram to free ~25 MB ----
        _release_audio("Track A audio (before Spectrogram)", audio_data_a)
        audio_data_a = None  # type: ignore[assignment]
        gc.collect()

        # ---- Step 4 - Spectrogram Track A (loads fresh — no audio_data alive) ----
        step_start = time.monotonic()
        try:
            log_memory("Before Spectrogram A")
            spectrogram_a = self._spectrogram_generator.generate(path_a)
            log_memory("After Spectrogram A")
            logger.info(
                "Step 4 - Spectrogram Track A completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 4 - Spectrogram Track A FAILED")
            raise

        # ---- Step 5 - Audio analysis Track B ----
        step_start = time.monotonic()
        try:
            audio_data_b, sr_b = _load_audio_once(path_b, "Track B")
            log_memory("Before AudioAnalyzer B")
            analysis_b = self._analyzer.analyze(
                path_b, audio_data=audio_data_b, sample_rate=sr_b
            ).model_copy(update={"filename": track_b.filename or ""})
            log_memory("After AudioAnalyzer B")
            logger.info(
                "Step 5 - Audio analysis Track B completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 5 - Audio analysis Track B FAILED")
            raise

        # ---- Step 6 - Waveform Track B (reuses audio_data_b) ----
        step_start = time.monotonic()
        try:
            log_memory("Before Waveform B")
            waveform_b = self._waveform_generator.generate(
                path_b, audio_data=audio_data_b, sample_rate=sr_b
            )
            log_memory("After Waveform B")
            logger.info(
                "Step 6 - Waveform Track B completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 6 - Waveform Track B FAILED")
            raise

        # ---- Release audio_data_b BEFORE Spectrogram to free ~20 MB ----
        _release_audio("Track B audio (before Spectrogram)", audio_data_b)
        audio_data_b = None  # type: ignore[assignment]
        gc.collect()

        # ---- Step 7 - Spectrogram Track B (loads fresh — no audio_data alive) ----
        step_start = time.monotonic()
        try:
            log_memory("Before Spectrogram B")
            spectrogram_b = self._spectrogram_generator.generate(path_b)
            log_memory("After Spectrogram B")
            logger.info(
                "Step 7 - Spectrogram Track B completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 7 - Spectrogram Track B FAILED")
            raise

        # ---- Step 8 - Compatibility Engine ----
        step_start = time.monotonic()
        try:
            compatibility = self._compatibility.compare(
                analysis_a,
                analysis_b,
            )
            logger.info(
                "Step 8 - Compatibility Engine completed in %.4f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 8 - Compatibility Engine FAILED")
            raise

        waveforms = Waveforms(
            track_a=waveform_a,
            track_b=waveform_b,
        )

        spectrograms = Spectrograms(
            track_a=spectrogram_a,
            track_b=spectrogram_b,
        )

        # ---- Mirror generated visualizations to Supabase Storage ----
        upload_artifact = getattr(self._storage, "upload_artifact", None)
        if callable(upload_artifact):
            storage_root = settings.processed_path.parent
            waveform_a_path = storage_root / waveform_a.image_path
            waveform_b_path = storage_root / waveform_b.image_path
            spectrogram_a_path = storage_root / spectrogram_a.image_path
            spectrogram_b_path = storage_root / spectrogram_b.image_path

            waveform_a = waveform_a.model_copy(
                update={
                    "url": upload_artifact(
                        waveform_a_path,
                        f"analyses/{analysis_id}/waveforms/{waveform_a_path.name}",
                    )
                }
            )
            waveform_b = waveform_b.model_copy(
                update={
                    "url": upload_artifact(
                        waveform_b_path,
                        f"analyses/{analysis_id}/waveforms/{waveform_b_path.name}",
                    )
                }
            )
            spectrogram_a = spectrogram_a.model_copy(
                update={
                    "url": upload_artifact(
                        spectrogram_a_path,
                        f"analyses/{analysis_id}/spectrograms/{spectrogram_a_path.name}",
                    )
                }
            )
            spectrogram_b = spectrogram_b.model_copy(
                update={
                    "url": upload_artifact(
                        spectrogram_b_path,
                        f"analyses/{analysis_id}/spectrograms/{spectrogram_b_path.name}",
                    )
                }
            )
            waveforms = Waveforms(track_a=waveform_a, track_b=waveform_b)
            spectrograms = Spectrograms(
                track_a=spectrogram_a,
                track_b=spectrogram_b,
            )

        # ---- Step 9 - Build API Response ----
        step_start = time.monotonic()
        try:
            response = UploadAnalysisResponse(
                status="success",
                message="Tracks analyzed successfully",
                analysis_id=analysis_id,
                track_a=analysis_a,
                track_b=analysis_b,
                compatibility=compatibility,
                ai_recommendation=AIRecommendationResponse(
                    summary="",
                    mix_direction="",
                    transition_quality="",
                    transition_type="",
                    confidence=0,
                    tempo_analysis=TempoAnalysis(difference="", recommendation=""),
                    energy_analysis=EnergyAnalysis(difference="", recommendation=""),
                    compatibility_analysis=CompatibilityAnalysis(
                        score="", interpretation=""
                    ),
                    mix_strategy=MixStrategy(
                        before_transition="",
                        during_transition="",
                        after_transition="",
                    ),
                    dj_execution=DJExecution(
                        loop="",
                        eq="",
                        filter="",
                        tempo_fader="",
                        phrase_matching="",
                        cue_point="",
                    ),
                    club_tip="",
                    professional_notes="",
                    risks=[],
                    best_use_case="",
                    risk_level="",
                ),
                waveforms=waveforms,
                spectrograms=spectrograms,
            )
            logger.info(
                "Step 9 - Build API Response completed in %.4f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 9 - Build API Response FAILED")
            raise

        # ---- Step 10 - AI Recommendation ----
        step_start = time.monotonic()
        try:
            log_memory("Before AI")
            ai_recommendation = self._ai_agent.recommend(response)
            response = response.model_copy(
                update={"ai_recommendation": ai_recommendation}
            )
            log_memory("After AI")
            logger.info(
                "Step 10 - AI Recommendation completed in %.2f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 10 - AI Recommendation FAILED")
            raise

        # ---- Step 11 - Write analysis.json ----
        step_start = time.monotonic()
        try:
            self._write_analysis_metadata(
                analysis_id,
                response,
            )
            logger.info(
                "Step 11 - Write analysis.json completed in %.4f s",
                time.monotonic() - step_start,
            )
        except Exception:
            logger.exception("Step 11 - Write analysis.json FAILED")
            raise

        total_time = time.monotonic() - pipeline_start
        log_memory("Final")
        logger.info("=" * 60)
        logger.info("Analysis completed successfully | Total time: %.2f s", total_time)
        logger.info("=" * 60)

        return response

    def _write_analysis_metadata(
        self,
        analysis_id: str,
        response: UploadAnalysisResponse,
    ) -> None:
        """Persist analysis metadata as JSON inside the session folder."""

        metadata = AnalysisMetadata(
            analysis_id=analysis_id,
            track_a=response.track_a,
            track_b=response.track_b,
            compatibility=response.compatibility,
            ai_recommendation=response.ai_recommendation,
            waveforms=response.waveforms,
            spectrograms=response.spectrograms,
        )

        analysis_dir = settings.analysis_path / analysis_id
        analysis_dir.mkdir(parents=True, exist_ok=True)

        json_path = analysis_dir / "analysis.json"

        json_path.write_text(
            json.dumps(
                metadata.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


analysis_service = AnalysisService()
