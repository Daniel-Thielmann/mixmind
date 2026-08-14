from __future__ import annotations

import hashlib
import logging
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.exceptions import (
    AudioDownloadTooLargeError,
    AudioProviderUnavailableError,
    ExternalProviderRateLimitError,
    InvalidDownloadedAudioError,
)
from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata

logger = logging.getLogger(__name__)

_provider_lock = threading.Lock()
_MAX_CONVERSION_ATTEMPTS = 3


class RapidApiYouTubeDownloader:
    def __init__(self, temp_dir: Path | None = None) -> None:
        self._temp_dir = temp_dir or settings.temp_path
        self._max_size = settings.RAPIDAPI_DOWNLOAD_MAX_SIZE * 1024 * 1024

    def acquire(self, metadata: SpotifyTrackMetadata) -> AcquiredAudio:
        # The provider's entry-level plans reject concurrent conversions. The
        # shared analysis service may download in parallel, so serialize only
        # this provider without slowing down providers that support concurrency.
        with _provider_lock:
            return self._acquire_locked(metadata)

    def _acquire_locked(self, metadata: SpotifyTrackMetadata) -> AcquiredAudio:
        key = settings.RAPIDAPI_YOUTUBE_MP3_KEY
        if not key:
            raise AudioProviderUnavailableError(
                detail="YouTube audio provider is not configured."
            )
        headers = {
            "x-rapidapi-key": key,
            "x-rapidapi-host": settings.RAPIDAPI_YOUTUBE_MP3_HOST,
            "Content-Type": "application/json",
        }
        response = self._request_conversion(metadata.spotify_url, headers)
        if response.status_code != 200:
            raise AudioProviderUnavailableError(
                detail=f"YouTube conversion provider returned status {response.status_code}."
            )
        download_url = _extract_url(response)
        if urlparse(download_url).scheme not in {"http", "https"}:
            raise InvalidDownloadedAudioError(
                detail="YouTube provider returned an invalid download URL."
            )
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        destination = (
            self._temp_dir / f"youtube_{metadata.spotify_id}_{secrets.token_hex(8)}.mp3"
        )
        digest = hashlib.sha256()
        total = 0
        try:
            with httpx.stream(
                "GET",
                download_url,
                follow_redirects=True,
                timeout=settings.RAPIDAPI_YOUTUBE_MP3_TIMEOUT,
            ) as stream:
                if stream.status_code != 200:
                    raise AudioProviderUnavailableError(
                        detail="YouTube audio download was rejected."
                    )
                with destination.open("wb") as target:
                    for chunk in stream.iter_bytes(256 * 1024):
                        total += len(chunk)
                        if total > self._max_size:
                            raise AudioDownloadTooLargeError()
                        digest.update(chunk)
                        target.write(chunk)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        if total == 0:
            destination.unlink(missing_ok=True)
            raise InvalidDownloadedAudioError(
                detail="YouTube provider returned an empty audio file."
            )
        return AcquiredAudio(
            local_path=destination,
            mime_type="audio/mpeg",
            provider="rapidapi_youtube_mp3",
            size_bytes=total,
            checksum_sha256=digest.hexdigest(),
            original_filename=f"{metadata.spotify_id}.mp3",
        )

    def _request_conversion(
        self, video_url: str, headers: dict[str, str]
    ) -> httpx.Response:
        endpoint = settings.RAPIDAPI_YOUTUBE_MP3_BASE_URL.rstrip("/") + "/download/mp3"
        for attempt in range(_MAX_CONVERSION_ATTEMPTS):
            try:
                response = httpx.get(
                    endpoint,
                    params={"url": video_url},
                    headers=headers,
                    timeout=settings.RAPIDAPI_YOUTUBE_MP3_TIMEOUT,
                )
            except httpx.HTTPError as exc:
                raise AudioProviderUnavailableError(
                    detail="YouTube conversion provider is unavailable."
                ) from exc

            if response.status_code != 429:
                return response
            if attempt + 1 >= _MAX_CONVERSION_ATTEMPTS:
                raise ExternalProviderRateLimitError(
                    detail=(
                        "YouTube audio provider is busy. Wait a moment and try again."
                    )
                )

            delay = _retry_delay_seconds(response, attempt)
            logger.warning(
                "YouTube provider rate limited conversion; retrying in %.1fs "
                "(attempt %d/%d)",
                delay,
                attempt + 2,
                _MAX_CONVERSION_ATTEMPTS,
            )
            time.sleep(delay)

        raise AssertionError("conversion retry loop exhausted")


def _extract_url(response: httpx.Response) -> str:
    text = response.text.strip().strip('"')
    try:
        data = response.json()
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            for key in ("url", "link", "downloadUrl", "download_url"):
                if data.get(key):
                    return str(data[key])
    except ValueError:
        pass
    return text


def _retry_delay_seconds(response: httpx.Response, attempt: int) -> float:
    try:
        retry_after = float(response.headers.get("Retry-After", ""))
        if retry_after > 0:
            return min(retry_after, 20.0)
    except (TypeError, ValueError):
        pass
    return min(3.0 * (attempt + 1), 10.0)
