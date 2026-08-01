from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import settings
from app.domain.repositories.spotify_connection_repository import (
    SpotifyConnectionRepository,
)

STATE_TTL = 600


class SpotifyStateService:
    def __init__(self, repository: SpotifyConnectionRepository | None = None) -> None:
        self._repository = repository

    def set_repository(self, repository: SpotifyConnectionRepository) -> None:
        self._repository = repository

    def _secret(self) -> bytes:
        return (
            settings.INTERNAL_AUTH_SECRET
            or settings.SPOTIFY_CLIENT_SECRET
            or "insecure-fallback"
        ).encode()

    def create_state(self, user_id: str, return_to: str = "/dashboard") -> str:
        if self._repository is None:
            raise RuntimeError("Spotify state repository is not configured")
        nonce = secrets.token_hex(32)
        expires_at = int(time.time()) + STATE_TTL
        self._repository.delete_expired_oauth_states()
        self._repository.create_oauth_state(nonce, user_id, "spotify", expires_at)
        payload = json.dumps(
            {"n": nonce, "iat": int(time.time()), "rt": return_to},
            separators=(",", ":"),
        )
        sig = hmac.new(self._secret(), payload.encode(), hashlib.sha256).hexdigest()
        encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
        return f"{encoded}.{sig}"

    def validate_and_consume_state(self, state: str) -> tuple[str, str] | None:
        if self._repository is None:
            return None
        try:
            parts = state.split(".")
            if len(parts) != 2:
                return None
            payload_b64, sig = parts
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            payload = base64.urlsafe_b64decode(payload_b64).decode()
            expected_sig = hmac.new(
                self._secret(), payload.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(expected_sig, sig):
                return None
            data: dict[str, Any] = json.loads(payload)
            nonce = data.get("n")
            if not nonce:
                return None
            state_record = self._repository.find_oauth_state(nonce)
            if state_record is None:
                return None
            if getattr(state_record, "consumed", False):
                return None
            if int(time.time()) > getattr(state_record, "expires_at", 0):
                return None
            user_id = getattr(state_record, "user_id", None)
            if not user_id:
                return None
            consumed = self._repository.consume_oauth_state(nonce)
            if not consumed:
                return None
            return user_id, str(data.get("rt") or "/dashboard")
        except Exception:
            return None
