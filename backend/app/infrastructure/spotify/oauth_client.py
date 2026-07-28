from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


class SpotifyGrantError(Exception):
    def __init__(self, error: str, error_description: str | None = None) -> None:
        self.error = error
        self.error_description = error_description
        super().__init__(error_description or error)


@dataclass
class SpotifyTokenResponse:
    access_token: str
    refresh_token: str | None
    token_type: str
    scope: str
    expires_in: int


class SpotifyOAuthClient:
    AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self) -> None:
        self._client_id = settings.SPOTIFY_CLIENT_ID
        self._client_secret = settings.SPOTIFY_CLIENT_SECRET
        self._redirect_uri = settings.SPOTIFY_REDIRECT_URI
        self._scopes = settings.SPOTIFY_SCOPES

    @property
    def scopes(self) -> str:
        return self._scopes

    def build_authorize_url(self, state: str) -> str:
        params = {
            "client_id": self._client_id,
            "response_type": "code",
            "redirect_uri": self._redirect_uri,
            "scope": self._scopes,
            "state": state,
        }
        from urllib.parse import urlencode

        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> SpotifyTokenResponse:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
        }
        return await self._post_token(data)

    async def refresh_access_token(self, refresh_token: str) -> SpotifyTokenResponse:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        return await self._post_token(data)

    async def _post_token(self, data: dict[str, str]) -> SpotifyTokenResponse:
        auth = httpx.BasicAuth(
            username=self._client_id,
            password=self._client_secret,
        )
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.TOKEN_URL,
                data=data,
                auth=auth,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code == 400:
            payload: dict[str, Any] = response.json()
            error = payload.get("error", "invalid_request")
            desc = payload.get("error_description")
            raise SpotifyGrantError(error=error, error_description=desc)
        response.raise_for_status()
        payload = response.json()
        return SpotifyTokenResponse(
            access_token=payload["access_token"],
            refresh_token=payload.get("refresh_token"),
            token_type=payload.get("token_type", "Bearer"),
            scope=payload.get("scope", ""),
            expires_in=payload["expires_in"],
        )
