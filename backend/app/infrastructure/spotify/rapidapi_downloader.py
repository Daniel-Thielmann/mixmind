from __future__ import annotations

import hashlib
import logging
from pathlib import Path

import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import (
    AudioDownloadNotFoundError,
    AudioDownloadTimeoutError,
    AudioDownloadTooLargeError,
    AudioProviderUnavailableError,
    ExternalProviderRateLimitError,
    InvalidDownloadedAudioError,
)
from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata
from app.infrastructure.spotify.rapidapi_models import RapidApiDownloadResponse

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 256 * 1024
_MAX_SIZE_BYTES: int = 200 * 1024 * 1024
_ALLOWED_SCHEMES = frozenset({"http", "https"})


class RapidApiSpotifyDownloaderProvider:
    def __init__(
        self,
        api_key: str | None = None,
        api_host: str | None = None,
        base_url: str | None = None,
        temp_dir: Path | None = None,
    ) -> None:
        self._api_key = api_key or settings.RAPIDAPI_KEY
        self._api_host = api_host or settings.RAPIDAPI_SPOTIFY_DOWNLOADER_HOST
        self._base_url = base_url or settings.RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL
        self._temp_dir = temp_dir or settings.temp_path
        self._timeout = httpx.Timeout(
            connect=15.0,
            read=settings.RAPIDAPI_DOWNLOAD_TIMEOUT,
            write=30.0,
            pool=10.0,
        )
        self._max_size = settings.RAPIDAPI_DOWNLOAD_MAX_SIZE * 1024 * 1024
        self._request_timeout = settings.RAPIDAPI_REQUEST_TIMEOUT

    def acquire(self, track_metadata: SpotifyTrackMetadata) -> AcquiredAudio:
        if not self._api_key or not self._api_host or not self._base_url:
            raise AudioProviderUnavailableError(
                detail="RapidAPI is not configured. Set RAPIDAPI_KEY and related variables."
            )

        download_url = self._request_download_url(track_metadata.spotify_id)
        return self._download_file(download_url, track_metadata)

    def _request_download_url(self, spotify_track_id: str) -> str:
        headers = {
            "x-rapidapi-key": self._api_key,
            "x-rapidapi-host": self._api_host,
        }
        params: dict[str, str] = {"songId": spotify_track_id}

        try:
            with httpx.Client(timeout=self._request_timeout) as client:
                response = client.get(
                    self._base_url.rstrip("/") + "/downloadSong",
                    headers=headers,
                    params=params,
                )
        except httpx.TimeoutException as exc:
            raise AudioDownloadTimeoutError() from exc
        except httpx.ConnectError as exc:
            raise AudioProviderUnavailableError(
                detail="Could not connect to the external audio provider."
            ) from exc
        except httpx.HTTPError as exc:
            raise AudioProviderUnavailableError(
                detail="External audio provider request failed."
            ) from exc

        if response.status_code == 429:
            raise ExternalProviderRateLimitError()
        if response.status_code == 404:
            raise AudioDownloadNotFoundError()
        if response.status_code >= 500:
            raise AudioProviderUnavailableError()
        if response.status_code != 200:
            raise AudioProviderUnavailableError(
                detail=f"External provider returned status {response.status_code}."
            )

        parsed = self._parse_download_response(response.json())
        return parsed

    def _parse_download_response(self, data: dict[str, object]) -> str:
        try:
            parsed = RapidApiDownloadResponse.model_validate(data)
        except ValidationError as exc:
            raise InvalidDownloadedAudioError(
                detail="Invalid response format from audio provider."
            ) from exc

        if not parsed.success:
            message = parsed.message or "Unknown error"
            raise AudioDownloadNotFoundError(detail=message)

        if parsed.data is None or not parsed.data.download_link:
            raise AudioDownloadNotFoundError(
                detail="Download URL not found in provider response."
            )

        return parsed.data.download_link

    def _download_file(
        self, download_url: str, track_metadata: SpotifyTrackMetadata
    ) -> AcquiredAudio:
        self._validate_download_url(download_url)
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        import secrets

        temp_name = f"spotify_{track_metadata.spotify_id}_{secrets.token_hex(8)}.mp3"
        dest = self._temp_dir / temp_name
        digest = hashlib.sha256()
        total = 0

        try:
            with httpx.Client(timeout=self._timeout, follow_redirects=True) as client:
                with client.stream("GET", download_url) as response:
                    if response.status_code != 200:
                        raise AudioProviderUnavailableError(
                            detail=f"Download returned status {response.status_code}."
                        )
                    content_type: str = (
                        response.headers.get("content-type", "audio/mpeg")
                        or "audio/mpeg"
                    )
                    content_length_str: str | None = response.headers.get(
                        "content-length"
                    )
                    if content_length_str:
                        try:
                            reported_size = int(content_length_str)
                            if reported_size > self._max_size:
                                raise AudioDownloadTooLargeError()
                        except (ValueError, TypeError):
                            pass

                    with open(dest, "wb") as target:
                        for chunk in response.iter_bytes(chunk_size=_CHUNK_SIZE):
                            total += len(chunk)
                            if total > self._max_size:
                                dest.unlink(missing_ok=True)
                                raise AudioDownloadTooLargeError()
                            digest.update(chunk)
                            target.write(chunk)
        except AudioDownloadTooLargeError:
            raise
        except httpx.TimeoutException as exc:
            dest.unlink(missing_ok=True)
            raise AudioDownloadTimeoutError() from exc
        except httpx.ConnectError as exc:
            dest.unlink(missing_ok=True)
            raise AudioProviderUnavailableError(
                detail="Could not connect to download server."
            ) from exc
        except httpx.HTTPError as exc:
            dest.unlink(missing_ok=True)
            raise AudioProviderUnavailableError(
                detail="Download failed due to an HTTP error."
            ) from exc
        except Exception:
            dest.unlink(missing_ok=True)
            raise

        if total == 0:
            dest.unlink(missing_ok=True)
            raise InvalidDownloadedAudioError(detail="Downloaded file is empty.")

        return AcquiredAudio(
            local_path=dest,
            mime_type=content_type,
            provider="rapidapi_spotify_downloader",
            temporary=True,
            size_bytes=total,
            checksum_sha256=digest.hexdigest(),
            original_filename=track_metadata.filename_safe(),
        )

    def _validate_download_url(self, url: str) -> None:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in _ALLOWED_SCHEMES:
            raise InvalidDownloadedAudioError(
                detail=f"Invalid download URL scheme: {parsed.scheme}."
            )
