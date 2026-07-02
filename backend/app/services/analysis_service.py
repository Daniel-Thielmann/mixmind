from app.audio.services.analyzer import AudioAnalyzer
from app.audio.services.spectrogram import (
    SpectrogramGenerator,
    spectrogram_generator,
)
from app.audio.services.waveform import WaveformGenerator, waveform_generator
from app.schemas.api import UploadAnalysisResponse
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

    It stores the uploaded files and delegates audio extraction to the
    analyzer. Future pipeline stages can be introduced here without changing
    the endpoint contract.
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

        path_a = self._storage.save_audio(track_a)
        path_b = self._storage.save_audio(track_b)

        analysis_a = self._analyzer.analyze(path_a).model_copy(
            update={"filename": track_a.filename or ""}
        )
        analysis_b = self._analyzer.analyze(path_b).model_copy(
            update={"filename": track_b.filename or ""}
        )
        waveform_a = self._waveform_generator.generate(path_a)
        waveform_b = self._waveform_generator.generate(path_b)
        spectrogram_a = self._spectrogram_generator.generate(path_a)
        spectrogram_b = self._spectrogram_generator.generate(path_b)
        compatibility = self._compatibility.compare(analysis_a, analysis_b)

        return UploadAnalysisResponse(
            status="success",
            message="Tracks analyzed successfully",
            track_a=analysis_a,
            track_b=analysis_b,
            compatibility=compatibility,
            waveforms=Waveforms(track_a=waveform_a, track_b=waveform_b),
            spectrograms=Spectrograms(track_a=spectrogram_a, track_b=spectrogram_b),
        )


analysis_service = AnalysisService()
