from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class SpotifyProfileAccessDeniedError(Exception):
    """Spotify denied Web API access for the authorized account."""


@dataclass
class SpotifyUserProfile:
    id: str
    display_name: str | None
    email: str | None
    images: list[dict[str, Any]]
    country: str | None
    product: str | None
    followers: dict[str, Any]


class SpotifyApiClient:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def get_current_user(self) -> SpotifyUserProfile:
        response = httpx.get(
            f"{self.BASE_URL}/me",
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code == 403:
            raise SpotifyProfileAccessDeniedError
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        return SpotifyUserProfile(
            id=data["id"],
            display_name=data.get("display_name"),
            email=data.get("email"),
            images=data.get("images", []),
            country=data.get("country"),
            product=data.get("product"),
            followers=data.get("followers", {}),
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }
