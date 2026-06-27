from fastapi import UploadFile

from app.audio.services.analyzer import AudioAnalyzer
from app.schemas.api import UploadAnalysisResponse
from app.services.infrastructure.storage_service import (
    StorageService,
    storage_service,
)


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
    ) -> None:
        self._storage = storage
        self._analyzer = analyzer or AudioAnalyzer()

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

        return UploadAnalysisResponse(
            status="success",
            message="Tracks analyzed successfully",
            track_a=analysis_a,
            track_b=analysis_b,
        )


analysis_service = AnalysisService()
