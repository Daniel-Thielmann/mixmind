import json
from uuid import uuid4

from app.audio.services.analyzer import AudioAnalyzer
from app.audio.services.spectrogram import (
    SpectrogramGenerator,
    spectrogram_generator,
)
from app.audio.services.waveform import WaveformGenerator, waveform_generator
from app.core.config import settings
from app.schemas.api import AnalysisMetadata, UploadAnalysisResponse
from app.schemas.spectrogram import Spectrograms
from app.schemas.waveform import Waveforms
from app.services.compatibility_service import (
    CompatibilityService,
    compatibility_service,
)
from app.services.infrastructure.storage_service import StorageService, storage_service
from fastapi import UploadFile


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
    ) -> None:
        self._storage = storage
        self._analyzer = analyzer or AudioAnalyzer()
        self._waveform_generator = waveform_service or waveform_generator
        self._spectrogram_generator = spectrogram_service or spectrogram_generator
        self._compatibility = compatibility or compatibility_service

    def analyze(
        self,
        track_a: UploadFile,
        track_b: UploadFile,
    ) -> UploadAnalysisResponse:
        """Store both uploads, analyze them, and return the API response."""

        analysis_id = uuid4().hex

        path_a = self._storage.save_audio(track_a)
        path_b = self._storage.save_audio(track_b)

        analysis_a = self._analyzer.analyze(path_a).model_copy(
            update={"filename": track_a.filename or ""}
        )
        analysis_b = self._analyzer.analyze(path_b).model_copy(
            update={"filename": track_b.filename or ""}
        )
        waveform_a = self._waveform_generator.generate(path_a, analysis_id, "a")
        waveform_b = self._waveform_generator.generate(path_b, analysis_id, "b")
        spectrogram_a = self._spectrogram_generator.generate(path_a, analysis_id, "a")
        spectrogram_b = self._spectrogram_generator.generate(path_b, analysis_id, "b")
        compatibility = self._compatibility.compare(analysis_a, analysis_b)

        waveforms = Waveforms(track_a=waveform_a, track_b=waveform_b)
        spectrograms = Spectrograms(track_a=spectrogram_a, track_b=spectrogram_b)

        response = UploadAnalysisResponse(
            status="success",
            message="Tracks analyzed successfully",
            analysis_id=analysis_id,
            track_a=analysis_a,
            track_b=analysis_b,
            compatibility=compatibility,
            waveforms=waveforms,
            spectrograms=spectrograms,
        )

        self._write_analysis_metadata(analysis_id, response)

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
