from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.exceptions import (
    SpotifyApiError,
    SpotifyApiUnavailableError,
    SpotifyAuthenticationError,
    SpotifyBadRequestError,
    SpotifyPlaylistForbiddenError,
    SpotifyRateLimitError,
    SpotifyTrackNotFoundError,
)
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata

logger = logging.getLogger(__name__)

SPOTIFY_API_BASE = "https://api.spotify.com/v1"


@dataclass
class SpotifyPaging:
    href: str
    items: list[dict[str, Any]]
    limit: int
    next: str | None
    offset: int
    previous: str | None
    total: int


@dataclass
class SpotifyPlaylistSummary:
    id: str
    name: str
    description: str
    images: list[dict[str, Any]]
    tracks_total: int
    owner_display_name: str
    snapshot_id: str


@dataclass
class SpotifyTrackSummary:
    id: str
    name: str
    artists: list[dict[str, Any]]
    album: dict[str, Any]
    duration_ms: int
    external_urls: dict[str, str]
    popularity: int
    isrc: str | None = None


_shared_client: httpx.AsyncClient | None = None


def _get_shared_client() -> httpx.AsyncClient:
    global _shared_client
    if _shared_client is None:
        _shared_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=10.0, read=25.0, write=30.0, pool=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
    return _shared_client


class ExtendedSpotifyApiClient:
    def __init__(
        self,
        access_token: str,
        refresh_access_token: Callable[[], Awaitable[str | None]] | None = None,
    ) -> None:
        self._access_token = access_token
        self._refresh_access_token = refresh_access_token

    async def get_track_metadata(self, track_id: str) -> SpotifyTrackMetadata:
        data = await self._get(f"/tracks/{track_id}")
        return self._parse_track(data)

    async def get_tracks_batch(
        self, track_ids: list[str]
    ) -> list[SpotifyTrackMetadata]:
        if not track_ids:
            return []
        ids_param = ",".join(track_ids)
        data = await self._get(f"/tracks?ids={ids_param}")
        tracks_data: list[dict[str, Any]] = data.get("tracks", [])
        results: list[SpotifyTrackMetadata] = []
        for item in tracks_data:
            if item is None:
                continue
            results.append(self._parse_track(item))
        return results

    async def get_user_playlists(
        self, limit: int = 20, offset: int = 0
    ) -> SpotifyPaging:
        data = await self._get(f"/me/playlists?limit={limit}&offset={offset}")
        return self._parse_paging(data)

    async def get_playlist_tracks(
        self, playlist_id: str, limit: int = 50, offset: int = 0
    ) -> SpotifyPaging:
        data = await self._get(
            f"/playlists/{playlist_id}/items?limit={limit}&offset={offset}"
        )
        return self._parse_paging(data)

    async def get_saved_tracks(self, limit: int = 20, offset: int = 0) -> SpotifyPaging:
        data = await self._get(f"/me/tracks?limit={limit}&offset={offset}")
        return self._parse_paging(data)

    async def search_tracks(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> SpotifyPaging:
        import urllib.parse

        clamped = max(1, min(limit, 10))
        safe_offset = max(0, offset)
        params = {
            "q": query,
            "type": "track",
            "limit": str(clamped),
            "offset": str(safe_offset),
        }
        query_string = urllib.parse.urlencode(params)
        data = await self._get(f"/search?{query_string}")
        tracks_data: dict[str, Any] = data.get("tracks", {})
        return self._parse_paging(tracks_data)

    async def _get(self, path: str) -> dict[str, Any]:
        url = f"{SPOTIFY_API_BASE}{path}"
        client = _get_shared_client()
        try:
            response = await client.get(url, headers=self._headers())
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning(
                "Spotify API transport error | path=%s | error=%s",
                path.split("?")[0],
                type(exc).__name__,
            )
            raise SpotifyApiUnavailableError() from exc

        if response.status_code == 401 and self._refresh_access_token is not None:
            refreshed_token = await self._refresh_access_token()
            if refreshed_token:
                self._access_token = refreshed_token
                try:
                    response = await client.get(url, headers=self._headers())
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    raise SpotifyApiUnavailableError() from exc
        if response.status_code == 200:
            return response.json()
        self._handle_error_response(response, path)
        raise AssertionError("Spotify error handler returned unexpectedly")

    def _handle_error_response(self, response: httpx.Response, path: str) -> None:
        spotify_error_body: dict[str, Any] | None = None
        try:
            spotify_error_body = response.json()
        except Exception:
            pass

        safe_path = path.split("?")[0]
        safe_params: dict[str, str] = {}
        if "?" in path:
            query_part = path.split("?", 1)[1]
            for pair in query_part.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    if k == "q":
                        safe_params[k] = v[:20] + "..." if len(v) > 20 else v
                    else:
                        safe_params[k] = v

        error_msg = "unknown"
        if spotify_error_body:
            error_obj = spotify_error_body.get("error")
            if isinstance(error_obj, dict):
                error_msg = error_obj.get("message", str(spotify_error_body))

        logger.warning(
            "Spotify API error | method=GET | path=%s | status=%d | params=%s | spotify_error=%s",
            safe_path,
            response.status_code,
            safe_params,
            error_msg,
        )

        if response.status_code == 400:
            raise SpotifyBadRequestError(spotify_response=spotify_error_body)
        if response.status_code == 401:
            raise SpotifyAuthenticationError()
        if response.status_code == 403:
            raise SpotifyPlaylistForbiddenError()
        if response.status_code == 404:
            raise SpotifyTrackNotFoundError()
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            detail = "Spotify API rate limit exceeded. Try again later."
            if retry_after and retry_after.isdigit():
                detail = f"Spotify is busy. Try again in {retry_after} seconds."
            raise SpotifyRateLimitError(detail=detail)
        if 500 <= response.status_code < 600:
            raise SpotifyApiUnavailableError()
        raise SpotifyApiError(
            detail=f"Spotify API returned status {response.status_code}."
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def _parse_track(self, data: dict[str, Any]) -> SpotifyTrackMetadata:
        track_id: str = data.get("id", "")
        external_urls: dict[str, Any] = data.get("external_urls", {})
        spotify_url: str = external_urls.get(
            "spotify", f"https://open.spotify.com/track/{track_id}"
        )
        title: str = data.get("name", "Unknown Track")
        artists_raw: list[dict[str, Any]] = data.get("artists", [])
        artists: tuple[str, ...] = tuple(
            a.get("name", "Unknown Artist") for a in artists_raw
        )
        album_raw: dict[str, Any] = data.get("album", {})
        album: str = album_raw.get("name", "Unknown Album")
        duration_ms: int = int(data.get("duration_ms", 0))
        popularity: int = int(data.get("popularity", 0))

        images: list[dict[str, Any]] = album_raw.get("images", [])
        artwork_url: str | None = images[0]["url"] if images else None

        isrc: str | None = None
        external_ids: dict[str, Any] | None = data.get("external_ids")
        if external_ids:
            isrc = external_ids.get("isrc")

        return SpotifyTrackMetadata(
            spotify_id=track_id,
            spotify_url=spotify_url,
            title=title,
            artists=artists,
            album=album,
            duration_ms=duration_ms,
            isrc=isrc,
            artwork_url=artwork_url,
            popularity=popularity,
        )

    def _parse_paging(self, data: dict[str, Any]) -> SpotifyPaging:
        return SpotifyPaging(
            href=data.get("href", ""),
            items=data.get("items", []),
            limit=int(data.get("limit", 20)),
            next=data.get("next"),
            offset=int(data.get("offset", 0)),
            previous=data.get("previous"),
            total=int(data.get("total", 0)),
        )

    @staticmethod
    def extract_track_from_item(item: dict[str, Any]) -> SpotifyTrackSummary | None:
        track: dict[str, Any] | None = None
        if "item" in item:
            track = item["item"]
        elif "track" in item:
            track = item["track"]
        elif "id" in item:
            track = item
        if not track or not track.get("id"):
            return None
        isrc: str | None = None
        external_ids: dict[str, Any] | None = track.get("external_ids")
        if external_ids:
            isrc = external_ids.get("isrc")
        return SpotifyTrackSummary(
            id=track["id"],
            name=track.get("name", "Unknown"),
            artists=track.get("artists", []),
            album=track.get("album", {}),
            duration_ms=int(track.get("duration_ms", 0)),
            external_urls=track.get("external_urls", {}),
            popularity=int(track.get("popularity", 0)),
            isrc=isrc,
        )
