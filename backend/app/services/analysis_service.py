import gc
import json
import logging
import time
from uuid import uuid4

import librosa
import numpy as np
from app.ai.agent import DJAgent, dj_agent
from app.ai.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.audio.services.analyzer import AudioAnalyzer
from app.audio.services.spectrogram import (
    SpectrogramGenerator,
    spectrogram_generator,
)
from app.audio.services.waveform import (
    WaveformGenerator,
    waveform_generator,
)
from app.core.config import settings
from app.schemas.api import AnalysisMetadata, UploadAnalysisResponse
from app.schemas.spectrogram import Spectrograms
from app.schemas.waveform import Waveforms
from app.services.compatibility_service import (
    CompatibilityService,
    compatibility_service,
)
from app.services.infrastructure.storage_service import (
    StorageService,
    storage_service,
)
from app.utils.log_utils import log_memory
from fastapi import UploadFile

logger = logging.getLogger(__name__)


def _load_audio_once(path, label: str) -> tuple[np.ndarray, int]:
    """Load audio from disk exactly once. Used by AnalysisService to
    share the same ndarray across AudioAnalyzer, WaveformGenerator,
    and SpectrogramGenerator."""
    logger.info("  Loading audio for %s: %s", label, path.name)
    log_memory(f"Before load {label}")
    load_start = time.monotonic()
    audio_data, sr = librosa.load(path, sr=None, mono=True)
    elapsed = time.monotonic() - load_start
    log_memory(f"After load {label}")
    logger.info(
        "  Audio %s loaded in %.2f s | dtype=%s | shape=%s"
        " | nbytes=%d (%.2f MB) | sr=%d",
        label,
        elapsed,
        audio_data.dtype,
        audio_data.shape,
        audio_data.nbytes,
        audio_data.nbytes / (1024 * 1024),
        sr,
    )
    return audio_data, sr


def _release_audio(label: str, *arrays) -> None:
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
        audio_data_a = None
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
        audio_data_b = None
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
