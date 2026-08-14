from __future__ import annotations

import hashlib
import secrets
from pathlib import Path
from urllib.parse import urlparse

import httpx

from app.core.config import settings
from app.core.exceptions import (
    AudioDownloadTooLargeError,
    AudioProviderUnavailableError,
    InvalidDownloadedAudioError,
)
from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata


class RapidApiYouTubeDownloader:
    def __init__(self, temp_dir: Path | None = None) -> None:
        self._temp_dir = temp_dir or settings.temp_path
        self._max_size = settings.RAPIDAPI_DOWNLOAD_MAX_SIZE * 1024 * 1024

    def acquire(self, metadata: SpotifyTrackMetadata) -> AcquiredAudio:
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
        try:
            response = httpx.get(
                settings.RAPIDAPI_YOUTUBE_MP3_BASE_URL.rstrip("/") + "/download/mp3",
                params={"url": metadata.spotify_url},
                headers=headers,
                timeout=settings.RAPIDAPI_YOUTUBE_MP3_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            raise AudioProviderUnavailableError(
                detail="YouTube conversion provider is unavailable."
            ) from exc
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
