from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

from app.application.use_cases.spotify.state_service import SpotifyStateService
from app.domain.entities.spotify_connection import SpotifyConnection
from app.domain.repositories.spotify_connection_repository import (
    SpotifyConnectionRepository,
)
from app.infrastructure.spotify.api_client import SpotifyApiClient
from app.infrastructure.spotify.oauth_client import SpotifyOAuthClient

logger = logging.getLogger(__name__)


class CompleteSpotifyConnectionUseCase:
    def __init__(
        self,
        oauth_client: SpotifyOAuthClient | None = None,
        state_service: SpotifyStateService | None = None,
        repository: SpotifyConnectionRepository | None = None,
    ) -> None:
        self._oauth = oauth_client or SpotifyOAuthClient()
        self._state_service = state_service or SpotifyStateService()
        self._repository = repository
        if repository:
            self._state_service.set_repository(repository)

    def set_repository(self, repository: SpotifyConnectionRepository) -> None:
        self._repository = repository
        self._state_service.set_repository(repository)

    async def execute(
        self,
        code: str | None,
        state: str,
        error: str | None = None,
    ) -> tuple[SpotifyConnection | None, str | None]:
        if error == "access_denied":
            logger.info("User denied Spotify authorization")
            return None, "Authorization denied. Please try again."

        if not code:
            return None, "Missing authorization code."

        user_id = self._state_service.validate_and_consume_state(state)
        if user_id is None:
            logger.warning("Invalid, expired, or replayed state parameter")
            return None, "Invalid or expired state. Please try connecting again."

        try:
            token_response = await self._oauth.exchange_code(code)
        except Exception:
            logger.error("Failed to exchange authorization code")
            return None, "Failed to complete authorization with Spotify."

        try:
            api_client = SpotifyApiClient(token_response.access_token)
            profile = api_client.get_current_user()
        except Exception:
            logger.error("Failed to fetch Spotify user profile")
            return None, "Failed to verify Spotify account."

        expires_at = int(time.time()) + token_response.expires_in
        now = datetime.now(UTC)

        connection = SpotifyConnection(
            user_id=user_id,
            spotify_user_id=profile.id,
            spotify_display_name=profile.display_name,
            spotify_email=profile.email,
            access_token=token_response.access_token,
            refresh_token=token_response.refresh_token or "",
            token_type=token_response.token_type,
            scope=token_response.scope,
            expires_at=expires_at,
            status="active",
            authorized_at=now,
        )

        if self._repository:
            connection = self._repository.save(connection)

        logger.info(
            "Spotify connected for user %s (spotify_id=%s)",
            user_id,
            profile.id,
        )
        return connection, None
