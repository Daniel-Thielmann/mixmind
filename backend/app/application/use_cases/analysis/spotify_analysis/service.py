from __future__ import annotations

import logging
from pathlib import Path
from typing import BinaryIO, Protocol

from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track.service import (
    AnalysisService,
)
from app.application.use_cases.analysis.spotify_analysis.dto import (
    SpotifyAnalysisRequest,
    TrackPosition,
)
from app.core.exceptions import (
    AudioDurationMismatchError,
    InvalidDownloadedAudioError,
)
from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata
from app.infrastructure.spotify.extended_api_client import ExtendedSpotifyApiClient
from app.infrastructure.spotify.rapidapi_downloader import (
    RapidApiSpotifyDownloaderProvider,
)

logger = logging.getLogger(__name__)

_DURATION_TOLERANCE_SECONDS = 5
_DURATION_WARNING_SECONDS = 15


class UploadSource(Protocol):
    filename: str | None
    content_type: str | None
    file: BinaryIO


class _DownloadedAudioSource:
    def __init__(
        self, path: Path, filename: str, content_type: str = "audio/mpeg"
    ) -> None:
        self.filename: str | None = filename
        self.content_type: str | None = content_type
        self.file: BinaryIO = path.open("rb")


class SpotifyAnalysisService:
    def __init__(
        self,
        analysis_service: AnalysisService | None = None,
        downloader: RapidApiSpotifyDownloaderProvider | None = None,
    ) -> None:
        self._analysis_service = analysis_service or AnalysisService()
        self._downloader = downloader or RapidApiSpotifyDownloaderProvider()

    async def analyze(
        self,
        request: SpotifyAnalysisRequest,
        spotify_api_client: ExtendedSpotifyApiClient,
    ) -> UploadAnalysisResponse:
        track_a_meta = await spotify_api_client.get_track_metadata(
            request.get_track_a().spotify_track_id
        )
        track_b_meta = await spotify_api_client.get_track_metadata(
            request.get_track_b().spotify_track_id
        )

        logger.info(
            "Acquired Spotify metadata: A='%s' (%s), B='%s' (%s)",
            track_a_meta.title,
            track_a_meta.spotify_id,
            track_b_meta.title,
            track_b_meta.spotify_id,
        )

        acquired_a = self._download_and_validate(track_a_meta, "track_a")
        try:
            acquired_b = self._download_and_validate(track_b_meta, "track_b")
        except Exception:
            self._cleanup(acquired_a)
            raise

        source_a = _DownloadedAudioSource(
            path=acquired_a.local_path,
            filename=acquired_a.original_filename or f"{track_a_meta.spotify_id}.mp3",
            content_type=acquired_a.mime_type,
        )
        source_b = _DownloadedAudioSource(
            path=acquired_b.local_path,
            filename=acquired_b.original_filename or f"{track_b_meta.spotify_id}.mp3",
            content_type=acquired_b.mime_type,
        )

        try:
            import asyncio

            response = await asyncio.to_thread(
                self._analysis_service.analyze, source_a, source_b
            )
        except Exception:
            self._cleanup(acquired_a)
            self._cleanup(acquired_b)
            raise

        self._cleanup(acquired_a)
        self._cleanup(acquired_b)

        return response

    def _download_and_validate(
        self, metadata: SpotifyTrackMetadata, position: TrackPosition
    ) -> AcquiredAudio:
        acquired = self._downloader.acquire(metadata)
        try:
            self._validate_audio_length(acquired, metadata, position)
        except Exception:
            self._cleanup(acquired)
            raise
        return acquired

    def _validate_audio_length(
        self,
        acquired: AcquiredAudio,
        metadata: SpotifyTrackMetadata,
        position: TrackPosition,
    ) -> None:
        import soundfile as sf

        try:
            info = sf.info(str(acquired.local_path))
            file_duration = info.duration
            spotify_duration = metadata.duration_seconds
            diff = abs(file_duration - spotify_duration)

            if diff > _DURATION_WARNING_SECONDS:
                if diff > _DURATION_TOLERANCE_SECONDS:
                    raise AudioDurationMismatchError(
                        detail=(
                            f"Downloaded {position} duration ({file_duration:.1f}s) "
                            f"differs from Spotify metadata ({spotify_duration:.1f}s) "
                            f"by {diff:.1f}s."
                        )
                    )
                logger.warning(
                    "Duration mismatch for %s: file=%.1fs vs spotify=%.1fs (diff=%.1fs)",
                    position,
                    file_duration,
                    spotify_duration,
                    diff,
                )
        except AudioDurationMismatchError:
            raise
        except Exception as exc:
            raise InvalidDownloadedAudioError(
                detail=f"Failed to validate audio duration for {position}."
            ) from exc

    def _cleanup(self, acquired: AcquiredAudio) -> None:
        try:
            path = acquired.local_path
            if path.exists():
                path.unlink()
                logger.debug("Cleaned up temporary file: %s", path.name)
        except OSError:
            logger.warning("Failed to clean up temporary file: %s", acquired.local_path)


spotify_analysis_service = SpotifyAnalysisService()
