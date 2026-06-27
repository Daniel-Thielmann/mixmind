from fastapi import UploadFile

from app.audio.services.analyzer import AudioAnalyzer
from app.audio.services.converter import AudioConverter
from app.schemas.api import UploadAnalysisResponse, UploadedTrack
from app.services.recommendation_service import RecommendationService
from app.services.storage_service import StorageService, storage_service


class AnalysisService:
    """
    Orchestrates the analysis pipeline.

    Today it only stores uploaded files.
    The converter, analyzer and recommendation service are wired here so the
    endpoint stays unaware of the downstream pipeline.
    """

    def __init__(
        self,
        storage: StorageService = storage_service,
        converter: AudioConverter | None = None,
        analyzer: AudioAnalyzer | None = None,
        recommendation_service: RecommendationService | None = None,
    ) -> None:
        self._storage = storage
        self._converter = converter or AudioConverter()
        self._analyzer = analyzer or AudioAnalyzer()
        self._recommendation_service = recommendation_service or RecommendationService()

    def upload_tracks(
        self,
        track_a: UploadFile,
        track_b: UploadFile,
    ) -> UploadAnalysisResponse:

        path_a = self._storage.save(track_a)
        path_b = self._storage.save(track_b)

        return UploadAnalysisResponse(
            status="success",
            message="Tracks uploaded successfully",
            track_a=UploadedTrack(
                filename=track_a.filename or "",
                stored_as=path_a.name,
                status="uploaded",
            ),
            track_b=UploadedTrack(
                filename=track_b.filename or "",
                stored_as=path_b.name,
                status="uploaded",
            ),
        )


analysis_service = AnalysisService()
