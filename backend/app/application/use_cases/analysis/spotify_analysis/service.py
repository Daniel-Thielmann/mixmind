from __future__ import annotations

import logging
import subprocess
import time
from contextlib import suppress
from pathlib import Path
from typing import BinaryIO, Protocol

from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track.service import (
    AnalysisService,
)
from app.application.use_cases.analysis.progress import (
    AnalysisProgressCallback,
    AnalysisProgressEvent,
    AnalysisStage,
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


class TrackMetadataClient(Protocol):
    async def get_track_metadata(self, track_id: str) -> SpotifyTrackMetadata: ...


class RemoteAudioDownloader(Protocol):
    def acquire(self, metadata: SpotifyTrackMetadata) -> AcquiredAudio: ...


class _DownloadedAudioSource:
    def __init__(
        self, path: Path, filename: str, content_type: str = "audio/mpeg"
    ) -> None:
        self.filename: str | None = filename
        self.content_type: str | None = content_type
        self.file: BinaryIO = path.open("rb")

    def close(self) -> None:
        self.file.close()


class RemoteTrackAnalysisService:
    def __init__(
        self,
        analysis_service: AnalysisService | None = None,
        downloader: RemoteAudioDownloader | None = None,
        provider_name: str = "Spotify",
    ) -> None:
        self._analysis_service = analysis_service or AnalysisService()
        self._downloader = downloader or RapidApiSpotifyDownloaderProvider()
        self._provider_name = provider_name

    async def analyze(
        self,
        request: SpotifyAnalysisRequest,
        spotify_api_client: TrackMetadataClient,
        on_progress: AnalysisProgressCallback | None = None,
    ) -> UploadAnalysisResponse:
        import asyncio

        started_at = time.monotonic()
        if on_progress is not None:
            on_progress(
                AnalysisProgressEvent(
                    stage=AnalysisStage.ACQUIRING_TRACKS,
                    progress=5,
                    message=f"Fetching tracks from {self._provider_name}",
                )
            )
        track_a_meta = await spotify_api_client.get_track_metadata(
            request.get_track_a().spotify_track_id
        )
        track_b_meta = await spotify_api_client.get_track_metadata(
            request.get_track_b().spotify_track_id
        )
        logger.info(
            "remote_analysis_stage | provider=%s | stage=metadata | elapsed_ms=%.0f",
            self._provider_name.lower(),
            (time.monotonic() - started_at) * 1000,
        )

        logger.info(
            "Acquired %s metadata: A='%s' (%s), B='%s' (%s)",
            self._provider_name,
            track_a_meta.title,
            track_a_meta.spotify_id,
            track_b_meta.title,
            track_b_meta.spotify_id,
        )

        download_started_at = time.monotonic()
        acquired_a = await asyncio.to_thread(
            self._download_and_validate,
            track_a_meta,
            "track_a",
        )
        try:
            acquired_b = await asyncio.to_thread(
                self._download_and_validate,
                track_b_meta,
                "track_b",
            )
        except Exception:
            self._cleanup(acquired_a)
            raise

        if on_progress is not None:
            on_progress(
                AnalysisProgressEvent(
                    stage=AnalysisStage.TRACKS_ACQUIRED,
                    progress=20,
                    message="Tracks acquired and validated",
                )
            )

        logger.info(
            "remote_analysis_stage | provider=%s | stage=downloads | elapsed_ms=%.0f",
            self._provider_name.lower(),
            (time.monotonic() - download_started_at) * 1000,
        )

        source_a: _DownloadedAudioSource | None = None
        source_b: _DownloadedAudioSource | None = None
        try:
            source_a = _DownloadedAudioSource(
                path=acquired_a.local_path,
                filename=acquired_a.original_filename
                or f"{track_a_meta.spotify_id}.mp3",
                content_type=acquired_a.mime_type,
            )
            source_b = _DownloadedAudioSource(
                path=acquired_b.local_path,
                filename=acquired_b.original_filename
                or f"{track_b_meta.spotify_id}.mp3",
                content_type=acquired_b.mime_type,
            )
            analysis_started_at = time.monotonic()

            def report_analysis(event: AnalysisProgressEvent) -> None:
                if on_progress is None:
                    return
                on_progress(
                    event.model_copy(
                        update={"progress": 20 + round(event.progress * 0.8)}
                    )
                )

            response = await asyncio.to_thread(
                self._analysis_service.analyze,
                source_a,
                source_b,
                report_analysis,
            )
            logger.info(
                "remote_analysis_stage | provider=%s | stage=dsp | elapsed_ms=%.0f | total_ms=%.0f",
                self._provider_name.lower(),
                (time.monotonic() - analysis_started_at) * 1000,
                (time.monotonic() - started_at) * 1000,
            )
            return response
        finally:
            if source_a is not None:
                with suppress(OSError):
                    source_a.close()
            if source_b is not None:
                with suppress(OSError):
                    source_b.close()
            self._cleanup(acquired_a)
            self._cleanup(acquired_b)

    def _download_and_validate(
        self, metadata: SpotifyTrackMetadata, position: TrackPosition
    ) -> AcquiredAudio:
        acquired = self._downloader.acquire(metadata)
        try:
            self._ensure_decodable_audio(acquired, position)
            self._validate_audio_length(acquired, metadata, position)
        except Exception:
            self._cleanup(acquired)
            raise
        return acquired

    def _ensure_decodable_audio(
        self, acquired: AcquiredAudio, position: TrackPosition
    ) -> None:
        import soundfile as sf

        try:
            sf.info(str(acquired.local_path))
            return
        except Exception as probe_error:
            logger.info(
                "SoundFile could not open %s; normalizing with FFmpeg: %s",
                position,
                type(probe_error).__name__,
            )

        source_path = acquired.local_path
        normalized_path = source_path.with_suffix(".normalized.wav")
        try:
            completed = subprocess.run(
                [
                    "ffmpeg",
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    str(source_path),
                    "-vn",
                    "-acodec",
                    "pcm_s16le",
                    str(normalized_path),
                ],
                capture_output=True,
                check=False,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            normalized_path.unlink(missing_ok=True)
            raise InvalidDownloadedAudioError(
                detail=f"Downloaded audio for {position} could not be decoded."
            ) from exc

        if completed.returncode != 0 or not normalized_path.exists():
            normalized_path.unlink(missing_ok=True)
            raise InvalidDownloadedAudioError(
                detail=f"Downloaded audio for {position} is not a valid audio file."
            )

        try:
            info = sf.info(str(normalized_path))
            if info.frames <= 0 or info.samplerate <= 0:
                raise ValueError("normalized audio is empty")
        except Exception as exc:
            normalized_path.unlink(missing_ok=True)
            raise InvalidDownloadedAudioError(
                detail=f"Downloaded audio for {position} is not a valid audio file."
            ) from exc

        source_path.unlink(missing_ok=True)
        acquired.local_path = normalized_path
        acquired.mime_type = "audio/wav"
        acquired.size_bytes = normalized_path.stat().st_size
        acquired.checksum_sha256 = None
        acquired.original_filename = f"{source_path.stem}.wav"

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
            expected_duration = metadata.duration_seconds
            diff = abs(file_duration - expected_duration)

            if diff > _DURATION_WARNING_SECONDS:
                raise AudioDurationMismatchError(
                    detail=(
                        f"Downloaded {position} duration ({file_duration:.1f}s) "
                        f"differs from {self._provider_name} metadata ({expected_duration:.1f}s) "
                        f"by {diff:.1f}s."
                    )
                )
            if diff > _DURATION_TOLERANCE_SECONDS:
                logger.warning(
                    "Duration mismatch for %s: file=%.1fs vs %s=%.1fs (diff=%.1fs)",
                    position,
                    file_duration,
                    self._provider_name.lower(),
                    expected_duration,
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


SpotifyAnalysisService = RemoteTrackAnalysisService
spotify_analysis_service = RemoteTrackAnalysisService()
