from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import AudioProviderUnavailableError
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata


class YouTubeApiClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or settings.YOUTUBE_API_KEY

    async def search(self, query: str, page_token: str | None = None) -> dict[str, Any]:
        return await self._get(
            "/search",
            {
                "part": "snippet",
                "type": "video",
                "videoCategoryId": "10",
                "maxResults": 25,
                "q": query,
                "pageToken": page_token,
            },
        )

    async def metadata(self, video_id: str) -> SpotifyTrackMetadata:
        payload = await self._get(
            "/videos", {"part": "snippet,contentDetails", "id": video_id}
        )
        items = payload.get("items", [])
        if not items:
            raise AudioProviderUnavailableError(detail="YouTube video was not found.")
        item = items[0]
        snippet = item.get("snippet", {})
        return SpotifyTrackMetadata(
            spotify_id=video_id,
            spotify_url=f"https://www.youtube.com/watch?v={video_id}",
            title=str(snippet.get("title") or "YouTube track"),
            artists=(str(snippet.get("channelTitle") or "YouTube"),),
            album="YouTube",
            duration_ms=_duration_ms(
                str(item.get("contentDetails", {}).get("duration") or "PT0S")
            ),
            artwork_url=((snippet.get("thumbnails") or {}).get("high") or {}).get(
                "url"
            ),
        )

    async def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self._api_key:
            raise AudioProviderUnavailableError(
                detail="YouTube Data API is not configured."
            )
        clean = {key: value for key, value in params.items() if value}
        clean["key"] = self._api_key
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.BASE_URL + path, params=clean)
        except httpx.HTTPError as exc:
            raise AudioProviderUnavailableError(
                detail="YouTube catalog is unavailable."
            ) from exc
        if response.status_code != 200:
            raise AudioProviderUnavailableError(
                detail=f"YouTube API returned status {response.status_code}."
            )
        return response.json()


def _duration_ms(value: str) -> int:
    import re

    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not match:
        return 0
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return (hours * 3600 + minutes * 60 + seconds) * 1000
