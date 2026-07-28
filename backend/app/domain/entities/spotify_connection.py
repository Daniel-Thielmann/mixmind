from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class SpotifyConnection:
    user_id: str
    spotify_user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    spotify_display_name: str | None = None
    spotify_email: str | None = None
    scope: str | None = None
    expires_at: int = 0
    status: str = "active"
    authorized_at: datetime | None = None
    last_refresh_at: datetime | None = None
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def is_expired(self) -> bool:
        import time

        return time.time() + 120 >= self.expires_at

    @property
    def scopes_list(self) -> list[str]:
        return self.scope.split() if self.scope else []

    @property
    def needs_reauthorization(self) -> bool:
        return self.status == "reauthorization_required"
